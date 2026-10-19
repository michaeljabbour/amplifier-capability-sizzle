#!/usr/bin/env python3
"""Check the built site, the skill contract, the downloads and the privacy patterns, without network access."""
import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.dont_write_bytecode = True
from build import BUNDLE, skill_files  # noqa: E402

TEXT = {'.md', '.py', '.mjs', '.js', '.html', '.css', '.json', '.yml', '.svg', '.txt', '.vtt', ''}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.references, self.downloads, self.duplicates = set(), [], [], []
        self.textarea, self.skill, self.h1s, self.lang = False, '', 0, None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'h1':
            self.h1s += 1
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.duplicates.append(attrs['id'])
            self.ids.add(attrs['id'])
        for key in ('href', 'src', 'poster'):
            if key in attrs:
                self.references.append(attrs[key])
        if 'download' in attrs:
            self.downloads.append(attrs.get('href', ''))
        if tag == 'textarea' and attrs.get('id') == 'skill-text':
            self.textarea = True

    def handle_endtag(self, tag):
        if tag == 'textarea':
            self.textarea = False

    def handle_data(self, data):
        if self.textarea:
            self.skill += data


def skill_contract():
    content = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    _, front, body = content.split('---', 2)
    keys = {line.split(':', 1)[0] for line in front.strip().splitlines() if line and not line[0].isspace()}
    # The Agent Skills fields, plus user-invocable, which Amplifier needs to register /sizzle (it defaults to off).
    # The strict reference validator (skills-ref) rejects user-invocable; drop it if that validator matters more.
    allowed = {'name', 'description', 'license', 'compatibility', 'metadata', 'user-invocable'}
    assert {'name', 'description'} <= keys <= allowed, f'Frontmatter keys: {keys}'
    fields = {k.strip(): v for k, v in (line.split(':', 1) for line in front.strip().splitlines())}
    version = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))['version']
    assert fields.get('version', '').strip().strip('"') == version, 'SKILL.md metadata version differs from project.json'
    assert len(fields.get('compatibility', '').strip().strip('"')) <= 500, 'Compatibility over 500 characters'
    assert fields['name'].strip().strip('"') == 'sizzle', 'The skill is named sizzle'
    assert len(fields['description'].strip().strip('"')) <= 1024, 'Description over 1024 characters'
    lines = body.lstrip('\n').splitlines()
    assert len(lines) < 500, f'SKILL.md body has {len(lines)} lines; keep it under 500'
    for forbidden in ('$ARGUMENTS', '${CLAUDE_SKILL_DIR}'):
        assert forbidden not in body, f'Host-specific syntax in SKILL.md: {forbidden}'
    assert not re.search(r'!`[^`]+`', body), 'Command injection syntax in SKILL.md'
    for path in sorted(set(re.findall(r'`((?:tools|references)/[\w./-]+)`', body))):
        assert (ROOT / path).exists(), f'SKILL.md names a missing file: {path}'
    return len(lines)


def shipped_text_files():
    skip = {'.git', '_site', '__pycache__', 'node_modules'}
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and not skip.intersection(path.relative_to(ROOT).parts) and path.suffix in TEXT and path.name != '.DS_Store':
            yield path


def privacy_and_style():
    email = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]*[A-Za-z]{2,}')
    home = re.compile(r'/Users/[A-Za-z]|/home/[A-Za-z]|[A-Z]:\\Users\\')
    secret = re.compile(r'\bsk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|gh[pousr]_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY')
    count = 0
    for path in shipped_text_files():
        text = path.read_text(encoding='utf-8', errors='replace')
        rel = path.relative_to(ROOT)
        assert not email.search(text), f'Email address in {rel}: {email.search(text).group()}'
        assert not home.search(text), f'Home directory path in {rel}'
        assert not secret.search(text), f'Credential-like string in {rel}'
        if path.suffix in {'.md', '.html', '.json'}:
            assert '—' not in text, f'Em dash in {rel}'
        count += 1
    images = 0
    for path in sorted(ROOT.rglob('*')):
        if path.suffix.lower() in {'.png', '.jpg', '.jpeg'} and '_site' not in path.parts and '.git' not in path.parts:
            data = path.read_bytes()
            if path.suffix.lower() == '.png':
                assert not any(chunk in data for chunk in (b'tEXt', b'iTXt', b'zTXt', b'eXIf')), f'PNG metadata in {path.relative_to(ROOT)}'
            else:
                assert b'Exif' not in data[:4096] and b'http://ns.adobe.com/xap' not in data, f'JPEG metadata in {path.relative_to(ROOT)}'
            images += 1
    videos = 0
    for path in sorted(ROOT.rglob('*.mp4')):
        if '_site' in path.parts or '.git' in path.parts:
            continue
        moov = movie_box(path.read_bytes())
        assert moov, f'No movie box in {path.relative_to(ROOT)}'
        for tag in (b'\xa9xyz', b'\xa9day', b'\xa9nam', b'\xa9ART', b'\xa9cmt', b'location', b'creation_time', b'com.apple.quicktime'):
            assert tag not in moov, f'Video metadata {tag!r} in {path.relative_to(ROOT)}'
        videos += 1
    return count, images, videos


def movie_box(data):
    """The MP4 'moov' box, where titles, dates and locations would live."""
    i = 0
    while i + 8 <= len(data):
        size, kind = int.from_bytes(data[i:i + 4], 'big'), data[i + 4:i + 8]
        if size == 1:
            size = int.from_bytes(data[i + 8:i + 16], 'big')
        if size < 8:
            return None
        if kind == b'moov':
            return data[i:i + size]
        i += size
    return None


def check(output):
    page = Page()
    raw = (output / 'index.html').read_text(encoding='utf-8')
    page.feed(raw)
    assert not page.duplicates, f'Duplicate IDs: {page.duplicates}'
    assert page.h1s == 1 and page.lang == 'en', 'Expected one page title and an English document language'
    assert not re.search(r'@@[A-Z_]+@@', raw), 'Unresolved placeholders'
    local = 0
    for reference in page.references:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme == 'https', f'Unexpected external protocol: {reference}'
            continue
        assert not parsed.path.startswith('/'), f'Root-relative link would break repository hosting: {reference}'
        target = (output / unquote(parsed.path)).resolve() if parsed.path else output / 'index.html'
        assert target.is_relative_to(output.resolve()), f'Link escapes output: {reference}'
        assert target.exists(), f'Missing link or asset: {reference}'
        if parsed.fragment:
            assert target.name == 'index.html' and parsed.fragment in page.ids, f'Missing anchor: {reference}'
        local += 1
    markdown = 0
    for document in output.rglob('*.md'):
        for reference in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (document.parent / unquote(parsed.path)).resolve()
            assert target.is_relative_to(output.resolve()), f'Markdown link escapes output: {document.name}: {reference}'
            assert target.exists(), f'Missing Markdown link: {document.relative_to(output)}: {reference}'
            markdown += 1
    assert page.skill == (ROOT / 'SKILL.md').read_text(encoding='utf-8'), 'Copy source differs from SKILL.md'
    files = skill_files()
    for name in files:
        assert (ROOT / name).read_bytes() == (output / name).read_bytes(), f'Download changed source: {name}'
    assert (ROOT / 'tools/audit-hook.js').read_bytes() == (output / 'assets/audit-hook.js').read_bytes(), 'The page must run the shipped hook'
    with ZipFile(output / BUNDLE) as bundle:
        assert bundle.namelist() == ['sizzle/' + name for name in files], 'Bundle contents differ from the skill files'
        assert bundle.testzip() is None
        for name in files:
            assert bundle.read('sizzle/' + name) == (ROOT / name).read_bytes(), f'Bundle changed source: {name}'
    assert len(page.downloads) == 2, 'Expected the bundle and SKILL.md download links'
    film = json.loads((output / 'assets/film.json').read_text(encoding='utf-8'))
    assert [c['id'] for c in film['cuts']] == ['first', 'checked'] and film['cuts'][1]['changes']
    for name in ('assets/style.css', 'assets/family.css'):
        css = (output / name).read_text(encoding='utf-8')
        assert not re.search(r'@import|url\(\s*[\'"]?https?:', css), f'External CSS dependency: {name}'
    assert "default-src 'self'" in raw and "object-src 'none'" in raw
    body = skill_contract()
    texts, images, videos = privacy_and_style()
    digest = hashlib.sha256((output / BUNDLE).read_bytes()).hexdigest()
    print(f'PASS: {local} local links/assets and fragments; no missing targets or duplicate IDs')
    print(f'PASS: {markdown} local destinations in shipped Markdown documentation')
    print(f'PASS: source textarea, SKILL.md download and {len(files)} bundle files match the repository byte for byte')
    print(f'PASS: skill contract (name sizzle, {body} body lines, every named tool and reference exists)')
    print(f'PASS: {texts} text files free of emails, home paths, credential patterns and em dashes; {images} images and {videos} videos without metadata')
    print('PASS: two film cuts, local assets, static CSP, repository-subpath-safe links')
    print(f'Bundle SHA-256: {digest}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    check(args.output.resolve())
