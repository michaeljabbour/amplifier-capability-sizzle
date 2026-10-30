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
Keys: ELEVENLABS_API_KEY; OPENAI_API_KEY (OPENAI_BASE_URL for a compatible endpoint); AZURE_SPEECH_KEY with
AZURE_SPEECH_REGION; GOOGLE_API_KEY. Flags override the variables. Keys are never printed or logged.

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
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.error
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


def post(url, headers, body, timeout=180):
    request = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        detail = error.read()[:400].decode('utf-8', 'replace')
        raise SystemExit(f'{url.split("?")[0]} answered {error.code}: {detail}')


def synthesize(provider, text, voice, model, style):
    """Return (audio bytes, file extension) from one request."""
    env = os.environ
    if provider == 'elevenlabs':
        base = env.get('ELEVENLABS_BASE_URL', 'https://api.elevenlabs.io')
        body = {'text': text, 'model_id': model or 'eleven_multilingual_v2'}
        audio = post(f'{base}/v1/text-to-speech/{voice}?output_format=mp3_44100_128',
                     {'xi-api-key': env['ELEVENLABS_API_KEY'], 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'},
                     json.dumps(body).encode())
        return audio, '.mp3'
    if provider == 'openai':
        base = env.get('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
        body = {'model': model or 'gpt-4o-mini-tts', 'voice': voice, 'input': text, 'response_format': 'wav'}
        if style:
            body['instructions'] = style
        audio = post(f'{base}/audio/speech', {'Authorization': f'Bearer {env["OPENAI_API_KEY"]}', 'Content-Type': 'application/json'},
                     json.dumps(body).encode())
        return audio, '.wav'
    if provider == 'azure':
        url = env.get('AZURE_SPEECH_ENDPOINT') or f'https://{env["AZURE_SPEECH_REGION"]}.tts.speech.microsoft.com/cognitiveservices/v1'
        lang = '-'.join(voice.split('-')[:2]) if voice.count('-') >= 2 else 'en-US'
        inner = escape(text)
        if style:
            inner = f'<mstts:express-as style="{escape(style)}">{inner}</mstts:express-as>'
        ssml = (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" '
                f'xml:lang="{lang}"><voice name="{escape(voice)}">{inner}</voice></speak>')
        audio = post(url, {'Ocp-Apim-Subscription-Key': env['AZURE_SPEECH_KEY'], 'Content-Type': 'application/ssml+xml',
                           'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm', 'User-Agent': 'sizzle-tts'}, ssml.encode())
        return audio, '.wav'
    if provider == 'google':
        base = env.get('GOOGLE_TTS_ENDPOINT', 'https://texttospeech.googleapis.com/v1/text:synthesize')
        lang = '-'.join(voice.split('-')[:2]) if voice.count('-') >= 2 else 'en-US'
        body = {'input': {'text': text}, 'voice': {'languageCode': lang, 'name': voice},
                'audioConfig': {'audioEncoding': 'LINEAR16', 'sampleRateHertz': 24000}}
        reply = post(base, {'X-Goog-Api-Key': env['GOOGLE_API_KEY'], 'Content-Type': 'application/json'}, json.dumps(body).encode())
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
    for name in KEYS.get(provider, []):
        present = bool(os.environ.get(name))
        ready &= present
        print(f'{name}: {"set" if present else "missing"}')
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
