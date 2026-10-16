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
    SIZZLE_TTS_COMMAND_EXT  the format that command writes, as an extension (default .wav; .aiff for macOS say)
Keys: ELEVENLABS_API_KEY; OPENAI_API_KEY (OPENAI_BASE_URL for a compatible endpoint); AZURE_SPEECH_KEY with
AZURE_SPEECH_REGION; GOOGLE_API_KEY. Flags override the variables. Keys are never printed or logged.

Each take is one paid request: there are no automatic retries. Providers that return the same audio for the
same text give one distinct take; vary the punctuation or --style instead. Every request is appended to a
generation log (generation-log.jsonl beside the output, or --log). Audio is converted to the output's
extension with ffmpeg when the provider returns another format. Standard library only, plus ffmpeg.
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
from pathlib import Path
from xml.sax.saxutils import escape

PROVIDERS = ('elevenlabs', 'openai', 'azure', 'google', 'command')
KEYS = {'elevenlabs': ['ELEVENLABS_API_KEY'], 'openai': ['OPENAI_API_KEY'], 'azure': ['AZURE_SPEECH_KEY', 'AZURE_SPEECH_REGION'],
        'google': ['GOOGLE_API_KEY'], 'command': ['SIZZLE_TTS_COMMAND']}


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
            done = subprocess.run(argv, input=feed, capture_output=True)
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
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    provider = args.provider.lower()
    if args.check:
        sys.exit(0 if check(provider, args.voice, args.model) else 1)
    if not check(provider, args.voice, args.model):
        sys.exit('Configure the provider in the environment first (see the notes above and tools/README.md).')
    if args.lines:
        jobs = [(item['id'], item['text'], Path(args.dir) / f"{item['id']}.{args.format}") for item in json.load(open(args.lines))]
    elif args.text and args.out:
        jobs = [(Path(args.out).stem, args.text, Path(args.out))]
    else:
        sys.exit('Give a line and an output file, or --lines with --dir.')
    log = Path(args.log) if args.log else jobs[0][2].parent / 'generation-log.jsonl'
    for line_id, text, target in jobs:
        for k in range(1, args.takes + 1):
            path = target if args.takes == 1 else target.with_name(f'{target.stem}_t{k}{target.suffix}')
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
