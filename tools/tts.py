#!/usr/bin/env python3
"""Voice a line with the text-to-speech provider the user configured (SKILL.md 0.2 and 5).

    python3 tools/tts.py --check
    python3 tools/tts.py "Fridays, the library stays open late." takes/L1.wav [--takes 4] [--style "warm, unhurried"]
    python3 tools/tts.py --lines lines.json --dir takes/ [--takes 4]      # lines.json: [{"id": "L1", "text": "..."}]

Configuration comes from the environment, never from files in the project:
    SIZZLE_TTS_PROVIDER   elevenlabs | openai | azure | google | command
    SIZZLE_TTS_VOICE      the provider's voice id or name (casting is a choice: there is no default voice)
    SIZZLE_TTS_MODEL      the model, where the provider has one
    SIZZLE_TTS_COMMAND    for "command": a command line with {out}, {text}, {text_file} and {voice} placeholders.
                          Without {text} or {text_file}, the text goes to the command's standard input.
                          TRUSTED CONFIGURATION: it runs as a local command with your privileges. Set it only from
                          your own environment, never from project files or text you did not write.
    SIZZLE_TTS_COMMAND_TIMEOUT  seconds before the command is killed (default 120; --command-timeout overrides)
    SIZZLE_TTS_COMMAND_EXT  the format that command writes, as an extension (default .wav; .aiff for macOS say)
Keys: ELEVENLABS_API_KEY; OPENAI_API_KEY; AZURE_SPEECH_KEY with AZURE_SPEECH_REGION; GOOGLE_API_KEY.
These keys are used only at their provider's default HTTPS origin. Custom endpoints use SIZZLE_TTS_API_KEY
explicitly, without falling back to the provider key. HTTPS is required except for literal loopback IPs or
localhost. Redirects are refused. Flags override the variables. Keys are never printed or logged.

Each take is one paid request: there are no automatic retries. Providers that return the same audio for the
same text give one distinct take; vary the punctuation or --style instead. Every request is appended to a
generation log (generation-log.jsonl beside the output, or --log). Audio is converted to the output's
extension with ffmpeg when the provider returns another format. Standard library only, plus ffmpeg.

--lines ids become file names inside --dir, so they must be plain names (no path separators, "..", absolute
paths, or NUL); anything that would resolve outside --dir is refused before a request is paid for. Existing
files are overwritten by default (as before); pass --no-overwrite to refuse instead.
"""
import argparse
import base64
import datetime
import http.client
import ipaddress
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PureWindowsPath
from xml.sax.saxutils import escape

DEFAULT_COMMAND_TIMEOUT = 120.0
PROVIDERS = ('elevenlabs', 'openai', 'azure', 'google', 'command')
KEYS = {'elevenlabs': ['ELEVENLABS_API_KEY'], 'openai': ['OPENAI_API_KEY'], 'azure': ['AZURE_SPEECH_KEY', 'AZURE_SPEECH_REGION'],
        'google': ['GOOGLE_API_KEY'], 'command': ['SIZZLE_TTS_COMMAND']}


def safe_basename(value):
    """Return value if it is a plain file name; otherwise exit. Rejects separators, absolute paths, '..', empty, NUL."""
    if not isinstance(value, str) or not value or value in ('.', '..') or '\0' in value \
            or '/' in value or '\\' in value or value.startswith('~') or Path(value).is_absolute() \
            or PureWindowsPath(value).is_absolute() or PureWindowsPath(value).drive:
        raise SystemExit(f'unsafe line id {value!r}: ids must be plain file names (no path separators, \'..\', absolute paths or NUL)')
    if value != value.strip() or value.endswith('.'):
        raise SystemExit(f'unsafe line id {value!r}: no leading/trailing whitespace or trailing dot')
    return value


def target_in_dir(out_dir, line_id, fmt, overwrite=True):
    """Build <out_dir>/<id>.<fmt>, proving the resolved path stays inside out_dir."""
    safe_basename(line_id)
    if not fmt or not fmt.isalnum():
        raise SystemExit(f'unsafe --format {fmt!r}: use a plain extension such as wav or mp3')
    root = Path(out_dir).resolve()
    target = (root / f'{line_id}.{fmt}').resolve()
    if target.parent != root:
        raise SystemExit(f'line id {line_id!r} resolves outside {root}')
    if not overwrite and target.exists():
        raise SystemExit(f'{target} exists and --no-overwrite is set')
    return target


def command_timeout(value=None, env=None):
    """Seconds allowed for SIZZLE_TTS_COMMAND: explicit value, else SIZZLE_TTS_COMMAND_TIMEOUT, else the default."""
    raw = value if value is not None else (env if env is not None else os.environ).get('SIZZLE_TTS_COMMAND_TIMEOUT')
    if raw in (None, ''):
        return DEFAULT_COMMAND_TIMEOUT
    try:
        seconds = float(raw)
    except (TypeError, ValueError):
        raise SystemExit(f'invalid command timeout {raw!r}: give a positive number of seconds')
    if not seconds > 0:
        raise SystemExit(f'invalid command timeout {raw!r}: give a positive number of seconds')
    return seconds


def loopback_host(host):
    if host == 'localhost':
        return True
    try:
        return '%' not in host and ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def endpoint_parts(url):
    """Validate before urllib can normalize unsafe input; never echo the URL."""
    if not isinstance(url, str) or not url or '\\' in url \
            or any(c.isspace() or unicodedata.category(c) in ('Cc', 'Cf', 'Cs') for c in url):
        raise SystemExit('Invalid TTS endpoint URL; use HTTPS or loopback HTTP.')
    try:
        decoded = urllib.parse.unquote(url)
        if any(unicodedata.category(c) in ('Cc', 'Cf', 'Cs') for c in decoded):
            raise ValueError('encoded control')
        parts = urllib.parse.urlsplit(url)
        host, port = parts.hostname, parts.port
        if parts.scheme not in ('https', 'http') or not host or parts.fragment \
                or parts.username is not None or parts.password is not None \
                or '%' in host or parts.netloc.endswith(':') \
                or (parts.netloc.startswith('[') and not re.fullmatch(r'\[[^\]]+\](?::[0-9]+)?', parts.netloc)) \
                or (port is not None and not 1 <= port <= 65535):
            raise ValueError('invalid endpoint')
        if parts.scheme == 'http' and not loopback_host(host):
            raise ValueError('non-loopback HTTP')
    except (ValueError, UnicodeError):
        raise SystemExit('Invalid TTS endpoint URL; use HTTPS or loopback HTTP without userinfo or fragments.') from None
    return parts


def provider_endpoint(provider, voice):
    env = os.environ
    if provider == 'elevenlabs':
        base = env.get('ELEVENLABS_BASE_URL', 'https://api.elevenlabs.io').rstrip('/')
        endpoint_parts(base)
        if urllib.parse.urlsplit(base).query:
            raise SystemExit('The ElevenLabs base URL must not contain a query.')
        url = f'{base}/v1/text-to-speech/{urllib.parse.quote(voice, safe="")}?output_format=mp3_44100_128'
    elif provider == 'openai':
        base = env.get('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
        endpoint_parts(base)
        if urllib.parse.urlsplit(base).query:
            raise SystemExit('The OpenAI base URL must not contain a query.')
        url = f'{base}/audio/speech'
    elif provider == 'azure':
        url = env.get('AZURE_SPEECH_ENDPOINT')
        if not url:
            region = env.get('AZURE_SPEECH_REGION', '')
            if not re.fullmatch(r'[a-zA-Z0-9-]+', region):
                raise SystemExit('Set a valid AZURE_SPEECH_REGION or an explicit speech endpoint.')
            url = f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1'
    elif provider == 'google':
        url = env.get('GOOGLE_TTS_ENDPOINT', 'https://texttospeech.googleapis.com/v1/text:synthesize')
    else:
        raise SystemExit('No network endpoint for this TTS provider.')
    endpoint_parts(url)
    return url


def endpoint_key_name(provider, url):
    """An ambient provider key belongs only to its exact default HTTPS origin."""
    parts = endpoint_parts(url)
    hosts = {'elevenlabs': 'api.elevenlabs.io', 'openai': 'api.openai.com',
             'google': 'texttospeech.googleapis.com'}
    region = os.environ.get('AZURE_SPEECH_REGION', '')
    if re.fullmatch(r'[a-zA-Z0-9-]+', region):
        hosts['azure'] = f'{region.lower()}.tts.speech.microsoft.com'
    if parts.scheme == 'https' and (parts.port or 443) == 443 and parts.hostname == hosts.get(provider):
        return KEYS[provider][0]
    return 'SIZZLE_TTS_API_KEY'


def endpoint_key(provider, url):
    name = endpoint_key_name(provider, url)
    key = os.environ.get(name, '')
    if not key or any(ord(c) < 33 or ord(c) > 126 for c in key):
        if name == 'SIZZLE_TTS_API_KEY':
            raise SystemExit('A custom TTS origin requires an explicit SIZZLE_TTS_API_KEY; provider keys are not forwarded.')
        raise SystemExit(f'Set a valid {name} in the environment.')
    return key


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirected paid POST must not replay its body or credential headers."""
    def http_error_302(self, req, fp, code, msg, headers):
        fp.close()
        raise SystemExit(f'TTS redirect refused (HTTP {code}); configure the final endpoint explicitly.')

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def post(url, headers, body, timeout=180):
    parts = endpoint_parts(url)
    try:
        request = urllib.request.Request(url, data=body, headers=headers, method='POST')
        handlers = [NoRedirect()]
        if loopback_host(parts.hostname):
            handlers.append(urllib.request.ProxyHandler({}))
        opener = urllib.request.build_opener(*handlers)
        with opener.open(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        try:
            error.close()
        except (OSError, ValueError, http.client.HTTPException):
            pass
        raise SystemExit(f'TTS provider returned HTTP {error.code}; response details are omitted.') from None
    except (urllib.error.URLError, OSError, ValueError, UnicodeError, http.client.HTTPException):
        raise SystemExit('TTS request failed; check the provider connection and endpoint configuration.') from None


def synthesize(provider, text, voice, model, style):
    """Return (audio bytes, file extension) from one request."""
    env = os.environ
    if provider == 'elevenlabs':
        url = provider_endpoint(provider, voice)
        body = {'text': text, 'model_id': model or 'eleven_multilingual_v2'}
        audio = post(url,
                     {'xi-api-key': endpoint_key(provider, url), 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'},
                     json.dumps(body).encode())
        return audio, '.mp3'
    if provider == 'openai':
        url = provider_endpoint(provider, voice)
        body = {'model': model or 'gpt-4o-mini-tts', 'voice': voice, 'input': text, 'response_format': 'wav'}
        if style:
            body['instructions'] = style
        audio = post(url, {'Authorization': f'Bearer {endpoint_key(provider, url)}', 'Content-Type': 'application/json'},
                     json.dumps(body).encode())
        return audio, '.wav'
    if provider == 'azure':
        url = provider_endpoint(provider, voice)
        lang = '-'.join(voice.split('-')[:2]) if voice.count('-') >= 2 else 'en-US'
        inner = escape(text)
        if style:
            inner = f'<mstts:express-as style="{escape(style)}">{inner}</mstts:express-as>'
        ssml = (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" '
                f'xml:lang="{lang}"><voice name="{escape(voice)}">{inner}</voice></speak>')
        audio = post(url, {'Ocp-Apim-Subscription-Key': endpoint_key(provider, url), 'Content-Type': 'application/ssml+xml',
                           'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm', 'User-Agent': 'sizzle-tts'}, ssml.encode())
        return audio, '.wav'
    if provider == 'google':
        url = provider_endpoint(provider, voice)
        lang = '-'.join(voice.split('-')[:2]) if voice.count('-') >= 2 else 'en-US'
        body = {'input': {'text': text}, 'voice': {'languageCode': lang, 'name': voice},
                'audioConfig': {'audioEncoding': 'LINEAR16', 'sampleRateHertz': 24000}}
        reply = post(url, {'X-Goog-Api-Key': endpoint_key(provider, url), 'Content-Type': 'application/json'}, json.dumps(body).encode())
        return base64.b64decode(json.loads(reply)['audioContent']), '.wav'
    if provider == 'command':
        template = env['SIZZLE_TTS_COMMAND']
        if '{out}' not in template:
            raise SystemExit('SIZZLE_TTS_COMMAND needs an {out} placeholder for the audio file it writes')
        with tempfile.TemporaryDirectory() as tmp:
            text_file = Path(tmp, 'line.txt')
            text_file.write_text(text, encoding='utf-8')
            out = Path(tmp, 'take' + (env.get('SIZZLE_TTS_COMMAND_EXT') or '.wav'))
            values = {'out': str(out), 'text': text, 'text_file': str(text_file), 'voice': voice or ''}
            argv = [part.format(**values) for part in shlex.split(template)]
            feed = None if ('{text}' in template or '{text_file}' in template) else text.encode()
            try:
                done = subprocess.run(argv, input=feed, capture_output=True, timeout=command_timeout())
            except subprocess.TimeoutExpired:
                raise SystemExit(f'the TTS command timed out after {command_timeout():g}s and was killed '
                                 '(raise SIZZLE_TTS_COMMAND_TIMEOUT or --command-timeout if it needs longer)')
            if done.returncode != 0 or not out.exists():
                raise SystemExit(f'the TTS command failed ({done.returncode}): {done.stderr[-400:].decode("utf-8", "replace")}')
            return out.read_bytes(), out.suffix
    raise SystemExit(f'unknown provider {provider!r}; use one of {", ".join(PROVIDERS)}')


def write(audio, ext, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == ext:
        target.write_bytes(audio)
        return
    if not shutil.which('ffmpeg'):
        raise SystemExit(f'ffmpeg is needed to turn {ext} into {target.suffix}')
    with tempfile.NamedTemporaryFile(suffix=ext) as raw:
        raw.write(audio)
        raw.flush()
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw.name, str(target)], check=True)


def check(provider, voice, model):
    print(f'provider: {provider or "not set (SIZZLE_TTS_PROVIDER)"}')
    print(f'voice:    {voice or "not set (SIZZLE_TTS_VOICE)"}')
    print(f'model:    {model or "provider default"}')
    ready = bool(provider in PROVIDERS and (voice or provider == 'command'))
    required = KEYS.get(provider, [])
    if provider in PROVIDERS and provider != 'command':
        try:
            url = provider_endpoint(provider, voice or 'check')
            required = [endpoint_key_name(provider, url)]
        except SystemExit as error:
            print(str(error))
            ready = False
            required = []
    for name in required:
        present = bool(os.environ.get(name))
        ready &= present
        print(f'{name}: {"set" if present else "missing"}')
    if ready and provider != 'command':
        try:
            endpoint_key(provider, url)
        except SystemExit:
            print('key: invalid configuration')
            ready = False
    print('ready' if ready else 'not ready')
    return ready


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('text', nargs='?')
    ap.add_argument('out', nargs='?')
    ap.add_argument('--lines', help='JSON list of {"id", "text"} to voice into --dir')
    ap.add_argument('--dir', default='.')
    ap.add_argument('--takes', type=int, default=1)
    ap.add_argument('--provider', default=os.environ.get('SIZZLE_TTS_PROVIDER', ''))
    ap.add_argument('--voice', default=os.environ.get('SIZZLE_TTS_VOICE', ''))
    ap.add_argument('--model', default=os.environ.get('SIZZLE_TTS_MODEL', ''))
    ap.add_argument('--style', default='', help='a style instruction (openai) or style name (azure)')
    ap.add_argument('--format', default='wav', help='output extension for --lines (wav or mp3)')
    ap.add_argument('--log')
    ap.add_argument('--no-overwrite', action='store_true', help='refuse to replace existing output files (default: overwrite)')
    ap.add_argument('--command-timeout', type=float, default=None,
                    help='seconds before SIZZLE_TTS_COMMAND is killed (default: SIZZLE_TTS_COMMAND_TIMEOUT or 120)')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if args.command_timeout is not None:
        os.environ['SIZZLE_TTS_COMMAND_TIMEOUT'] = str(args.command_timeout)
    command_timeout()
    provider = args.provider.lower()
    if args.check:
        sys.exit(0 if check(provider, args.voice, args.model) else 1)
    if not check(provider, args.voice, args.model):
        sys.exit('Configure the provider in the environment first (see the notes above and tools/README.md).')
    if args.lines:
        with open(args.lines, encoding='utf-8') as fh:
            items = json.load(fh)
        jobs = [(item['id'], item['text'], target_in_dir(args.dir, item['id'], args.format, not args.no_overwrite)) for item in items]
    elif args.text and args.out:
        jobs = [(Path(args.out).stem, args.text, Path(args.out))]
    else:
        sys.exit('Give a line and an output file, or --lines with --dir.')
    log = Path(args.log) if args.log else jobs[0][2].parent / 'generation-log.jsonl'
    for line_id, text, target in jobs:
        for k in range(1, args.takes + 1):
            path = target if args.takes == 1 else target.with_name(f'{target.stem}_t{k}{target.suffix}')
            if args.no_overwrite and path.exists():
                sys.exit(f'{path} exists and --no-overwrite is set')
            audio, ext = synthesize(provider, text, args.voice, args.model, args.style)
            write(audio, ext, path)
            entry = {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'provider': provider,
                     'voice': args.voice, 'model': args.model or 'default', 'style': args.style, 'line': line_id, 'take': k,
                     'text': text, 'file': str(path)}
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, 'a', encoding='utf-8') as fh:
                fh.write(json.dumps(entry) + '\n')
            print(f'{path}  ({provider}, take {k})')


if __name__ == '__main__':
    main()
