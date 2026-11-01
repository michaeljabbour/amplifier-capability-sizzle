"""Offline request-boundary regressions; no provider, network or real keys."""
import base64
import contextlib
import io
import json
import os
import sys
import unittest
import urllib.parse
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import tts


class TransportTests(unittest.TestCase):
    KEYS = {'elevenlabs': 'ELEVENLABS_API_KEY', 'openai': 'OPENAI_API_KEY',
            'azure': 'AZURE_SPEECH_KEY', 'google': 'GOOGLE_API_KEY'}
    OVERRIDES = {'elevenlabs': 'ELEVENLABS_BASE_URL', 'openai': 'OPENAI_BASE_URL',
                 'azure': 'AZURE_SPEECH_ENDPOINT', 'google': 'GOOGLE_TTS_ENDPOINT'}
    HEADERS = {'elevenlabs': 'xi-api-key', 'openai': 'authorization',
               'azure': 'ocp-apim-subscription-key', 'google': 'x-goog-api-key'}

    @contextlib.contextmanager
    def wire(self, env=None):
        calls = []
        def send(request, **kwargs):
            calls.append(request)
            if request.get_header('X-goog-api-key'):
                return io.BytesIO(json.dumps({'audioContent': base64.b64encode(b'audio').decode()}).encode())
            return io.BytesIO(b'audio')
        with mock.patch.dict(os.environ, env or {}, clear=True), \
                mock.patch.object(tts.urllib.request, 'urlopen', side_effect=send), \
                mock.patch.object(tts.urllib.request, 'build_opener', return_value=SimpleNamespace(open=send)):
            yield calls

    def request_key(self, request, provider):
        headers = {k.lower(): v for k, v in request.header_items()}
        return headers[self.HEADERS[provider]]

    def test_default_provider_origins_keep_existing_keys_and_payloads(self):
        hosts = {'elevenlabs': 'api.elevenlabs.io', 'openai': 'api.openai.com',
                 'azure': 'eastus.tts.speech.microsoft.com', 'google': 'texttospeech.googleapis.com'}
        for provider, name in self.KEYS.items():
            with self.subTest(provider=provider), self.wire({name: 'official-sentinel',
                    'AZURE_SPEECH_REGION': 'eastus', 'SIZZLE_TTS_API_KEY': 'other-sentinel'}) as calls:
                audio, ext = tts.synthesize(provider, 'Fictional line <&>', 'en-US-Test', '', 'warm')
                self.assertEqual(audio, b'audio')
                self.assertEqual(ext, '.mp3' if provider == 'elevenlabs' else '.wav')
                self.assertEqual(len(calls), 1)
                request = calls[0]
                self.assertEqual(urllib.parse.urlsplit(request.full_url).hostname, hosts[provider])
                self.assertIn('official-sentinel', self.request_key(request, provider))
                self.assertNotIn('other-sentinel', self.request_key(request, provider))
                self.assertEqual(request.get_method(), 'POST')
                self.assertIn(b'Fictional line', request.data)

    def test_remote_http_and_malformed_endpoints_never_send(self):
        bad = ['http://example.invalid/tts', 'ftp://example.invalid/tts',
               'file:///tmp/tts', 'https:///missing', 'https://user:SENTINEL@127.0.0.1/tts',
               'https://example.invalid/tts#SENTINEL', 'https://example.invalid:99999/tts',
               ' https://example.invalid/tts', 'https://example.invalid/\nSENTINEL',
               'https://example.invalid/%0d%0aSENTINEL', 'https://example.invalid/\u200bSENTINEL',
               'http://localhost.example.invalid/tts', 'http://127.1/tts',
               'http://2130706433/tts', 'http://[::1%25zone]/tts', 'https://example.invalid\\x',
               'https://example.invalid%20SENTINEL/tts', 'https://example.invalid:/tts',
               'http://[::1]extra/tts', 'https://[::1]extra/tts']
        for provider, override in self.OVERRIDES.items():
            for endpoint in bad:
                with self.subTest(provider=provider, endpoint=endpoint), self.wire({override: endpoint,
                        self.KEYS[provider]: 'official-sentinel', 'SIZZLE_TTS_API_KEY': 'custom-sentinel'}) as calls:
                    with self.assertRaises(SystemExit) as error:
                        tts.synthesize(provider, 'line', 'en-US-Test', '', '')
                    self.assertEqual(calls, [])
                    self.assertNotIn('SENTINEL', str(error.exception))

    def test_custom_origin_never_falls_back_to_official_key(self):
        for provider, override in self.OVERRIDES.items():
            with self.subTest(provider=provider), self.wire({override: 'https://custom.example.invalid/tts',
                    self.KEYS[provider]: 'official-sentinel'}) as calls:
                with self.assertRaises(SystemExit) as error:
                    tts.synthesize(provider, 'line', 'en-US-Test', '', '')
                self.assertIn('SIZZLE_TTS_API_KEY', str(error.exception))
                self.assertNotIn('official-sentinel', str(error.exception))
                self.assertEqual(calls, [])

    def test_custom_https_and_loopback_use_only_explicit_custom_key(self):
        for provider, override in self.OVERRIDES.items():
            for endpoint in ['https://custom.example.invalid/tts', 'http://localhost:8181/tts',
                             'http://127.0.0.1:8181/tts', 'http://[::1]:8181/tts']:
                with self.subTest(provider=provider, endpoint=endpoint), self.wire({override: endpoint,
                        self.KEYS[provider]: 'official-sentinel', 'SIZZLE_TTS_API_KEY': 'custom-sentinel'}) as calls:
                    self.assertEqual(tts.synthesize(provider, 'line', 'en-US-Test', '', '')[0], b'audio')
                    self.assertEqual(len(calls), 1)
                    key = self.request_key(calls[0], provider)
                    self.assertIn('custom-sentinel', key)
                    self.assertNotIn('official-sentinel', key)

    def test_default_host_on_nondefault_port_needs_custom_key(self):
        with self.wire({'OPENAI_BASE_URL': 'https://api.openai.com:8443/v1',
                        'OPENAI_API_KEY': 'official-sentinel'}) as calls:
            with self.assertRaises(SystemExit):
                tts.synthesize('openai', 'line', 'voice', '', '')
            self.assertEqual(calls, [])
        with self.wire({'OPENAI_BASE_URL': 'https://api.openai.com:443/v1',
                        'OPENAI_API_KEY': 'official-sentinel'}) as calls:
            tts.synthesize('openai', 'line', 'voice', '', '')
            self.assertIn('official-sentinel', self.request_key(calls[0], 'openai'))

    def test_elevenlabs_voice_stays_one_path_component(self):
        with self.wire({'ELEVENLABS_API_KEY': 'official-sentinel'}) as calls:
            tts.synthesize('elevenlabs', 'line', 'voice /?#', '', '')
            parts = urllib.parse.urlsplit(calls[0].full_url)
            self.assertEqual(parts.hostname, 'api.elevenlabs.io')
            self.assertTrue(parts.path.endswith('voice%20%2F%3F%23'))
            self.assertEqual(parts.query, 'output_format=mp3_44100_128')
            self.assertEqual(parts.fragment, '')

    def test_invalid_key_stops_before_request_without_echo(self):
        for key in ['', ' secret', 'secret\nSENTINEL', 'secret\u200bSENTINEL']:
            with self.subTest(key=repr(key)), self.wire({'OPENAI_API_KEY': key}) as calls:
                with self.assertRaises(SystemExit) as error:
                    tts.synthesize('openai', 'line', 'voice', '', '')
                self.assertEqual(calls, [])
                self.assertNotIn('SENTINEL', str(error.exception))

    def test_check_is_network_free_and_understands_custom_key(self):
        with self.wire({'OPENAI_BASE_URL': 'http://localhost:8181/v1',
                        'SIZZLE_TTS_API_KEY': 'custom-sentinel'}) as calls, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertTrue(tts.check('openai', 'voice', ''))
            self.assertEqual(calls, [])
            self.assertNotIn('custom-sentinel', output.getvalue())
        with self.wire({'OPENAI_BASE_URL': 'https://user:SENTINEL@127.0.0.1/v1',
                        'SIZZLE_TTS_API_KEY': 'custom-sentinel'}) as calls, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertFalse(tts.check('openai', 'voice', ''))
            self.assertEqual(calls, [])
            self.assertNotIn('SENTINEL', output.getvalue())

    def test_base_query_refused_without_echo(self):
        for provider, override in [('openai', 'OPENAI_BASE_URL'), ('elevenlabs', 'ELEVENLABS_BASE_URL')]:
            with self.subTest(provider=provider), self.wire({override: 'https://custom.example.invalid/v1?token=SENTINEL',
                        'SIZZLE_TTS_API_KEY': 'custom-sentinel'}) as calls:
                with self.assertRaises(SystemExit) as error:
                    tts.synthesize(provider, 'line', 'voice', '', '')
                self.assertEqual(calls, [])
                self.assertNotIn('SENTINEL', str(error.exception))


if __name__ == '__main__':
    unittest.main()
