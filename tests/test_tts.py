"""Trust-boundary tests for tools/tts.py (standard library only): python3 -m unittest discover -s tests -v"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import tts  # noqa: E402

TTS = str(ROOT / 'tools' / 'tts.py')
FAKE = [sys.executable, '-c', 'import sys,pathlib;pathlib.Path(sys.argv[1]).write_bytes(b"RIFFfake")']


def run_cli(args, env_extra=None, cwd=None):
    env = {**os.environ, 'SIZZLE_TTS_PROVIDER': 'command', 'SIZZLE_TTS_VOICE': 'v',
           'SIZZLE_TTS_COMMAND': ' '.join(f'"{p}"' if ' ' in p else p for p in FAKE[:2]) + ' "import sys,pathlib;pathlib.Path(sys.argv[1]).write_bytes(b\'RIFFfake\')" {out}'}
    env.update(env_extra or {})
    return subprocess.run([sys.executable, TTS, *args], capture_output=True, text=True, env=env, cwd=cwd, timeout=60)


class LineIdTests(unittest.TestCase):
    def test_bad_ids_rejected(self):
        for bad in ['../x', '..', '.', '', 'a/b', 'a\\b', '/etc/passwd', 'x\0y', 'C:\\x', '~root', ' a', 'a.', '..\\x', None, 5]:
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                tts.safe_basename(bad)

    def test_good_ids_accepted(self):
        for ok in ['L1', 'line-02', 'a.b', 'Ünï']:
            self.assertEqual(tts.safe_basename(ok), ok)

    def test_target_contained_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            t = tts.target_in_dir(d, 'L1', 'wav')
            self.assertEqual(t.parent, Path(d).resolve())
            t.write_bytes(b'x')
            self.assertEqual(tts.target_in_dir(d, 'L1', 'wav'), t)  # default overwrites
            with self.assertRaises(SystemExit):
                tts.target_in_dir(d, 'L1', 'wav', overwrite=False)
            with self.assertRaises(SystemExit):
                tts.target_in_dir(d, 'L1', '../wav')

    def test_symlinked_escape_refused(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            os.symlink(Path(outside) / 'x.wav', Path(d) / 'L1.wav')
            with self.assertRaises(SystemExit):
                tts.target_in_dir(d, 'L1', 'wav')

    def test_cli_traversal_writes_nothing_outside(self):
        with tempfile.TemporaryDirectory() as root:
            out = Path(root, 'out'); out.mkdir()
            lines = Path(root, 'lines.json')
            victim = Path(root, 'escaped.wav')
            lines.write_text(json.dumps([{'id': '../escaped', 'text': 'hi'}]))
            r = run_cli(['--lines', str(lines), '--dir', str(out)])
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(victim.exists())
            self.assertEqual(list(out.iterdir()), [])
            lines.write_text(json.dumps([{'id': str(Path(root, 'abs')), 'text': 'hi'}]))
            self.assertNotEqual(run_cli(['--lines', str(lines), '--dir', str(out)]).returncode, 0)
            self.assertFalse(Path(root, 'abs.wav').exists())

    def test_cli_good_id_and_overwrite_flag(self):
        with tempfile.TemporaryDirectory() as root:
            lines = Path(root, 'lines.json'); lines.write_text(json.dumps([{'id': 'L1', 'text': 'hi'}]))
            out = Path(root, 'o')
            self.assertEqual(run_cli(['--lines', str(lines), '--dir', str(out)]).returncode, 0)
            self.assertTrue((out / 'L1.wav').exists())
            self.assertEqual(run_cli(['--lines', str(lines), '--dir', str(out)]).returncode, 0)  # default overwrites
            self.assertNotEqual(run_cli(['--lines', str(lines), '--dir', str(out), '--no-overwrite']).returncode, 0)


class TimeoutTests(unittest.TestCase):
    def test_default_and_env(self):
        self.assertEqual(tts.command_timeout(None, {}), tts.DEFAULT_COMMAND_TIMEOUT)
        self.assertEqual(tts.command_timeout(None, {'SIZZLE_TTS_COMMAND_TIMEOUT': '7'}), 7.0)
        for bad in ['0', '-1', 'abc']:
            with self.assertRaises(SystemExit):
                tts.command_timeout(None, {'SIZZLE_TTS_COMMAND_TIMEOUT': bad})

    def test_hung_command_is_killed(self):
        sleeper = f'{sys.executable} -c "import time; time.sleep(30)" {{out}}'
        with mock.patch.dict(os.environ, {'SIZZLE_TTS_COMMAND': sleeper, 'SIZZLE_TTS_COMMAND_TIMEOUT': '0.5'}):
            with self.assertRaises(SystemExit) as ctx:
                tts.synthesize('command', 'hi', 'v', '', '')
        self.assertIn('timed out', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
