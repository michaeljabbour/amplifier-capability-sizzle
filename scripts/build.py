#!/usr/bin/env python3
"""Build the static site and the skill bundle using only Python's standard library."""
import argparse
import html
import json
import re
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = 'sizzle.zip'


def escape(value):
    return html.escape(str(value), quote=True)


def inline(markdown):
    """Escape a line of Markdown, then render its bold and code spans."""
    text = escape(markdown)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', text)


def numbered(block):
    return re.findall(r'^\d+\. (.+)$', block, re.M)


def table_rows(block):
    rows = [line for line in block.splitlines() if line.startswith('|')]
    return [[cell.strip() for cell in row.strip('|').split('|')] for row in rows[2:]]


def skill_files():
    """Everything the skill needs beside SKILL.md: the references and the tools."""
    files = ['SKILL.md', 'LICENSE']
    files += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'references').iterdir()) if p.is_file() and not p.name.startswith('.')]
    files += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'tools').iterdir()) if p.is_file() and not p.name.startswith('.')]
    return files


def build(output):
    site = ROOT / 'site'
    config = json.loads((site / 'site.json').read_text(encoding='utf-8'))
    skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    tools_readme = (ROOT / 'tools/README.md').read_text(encoding='utf-8')
    # The page shows the skill's own gate and checks, never a second copy of them.
    gate = numbered(skill.split('## 4. The creative gate', 1)[1].split('Fix every failure', 1)[0])
    checks = numbered(skill.split('**8.4 Technical gates.**', 1)[1].split('**8.5', 1)[0])
    tools = table_rows(tools_readme.split('## Requirements', 1)[0])
    providers = table_rows(tools_readme.split('## Voice', 1)[1].split('`SIZZLE_TTS_MODEL`', 1)[0])
    if len(gate) != 15 or len(checks) != 8:
        raise ValueError(f'Expected 15 creative gate points and 8 technical gates, found {len(gate)} and {len(checks)}')
    if len(tools) < 8 or len(providers) < 5:
        raise ValueError('Expected the tools table and the provider table in tools/README.md')
    film = config['film']
    if [c['id'] for c in film['cuts']] != ['first', 'checked']:
        raise ValueError('The film needs a first cut and a checked cut, in that order')
    replacements = {
        'NAME': escape(config['name']),
        'DESCRIPTION': escape(config['description']),
        'FILM_TITLE': escape(film['title']),
        'FILM_BRIEF': escape(film['brief']),
        'FILM_LAST': str(int(film['duration'] * film['fps']) - 1),
        'FIRST_SUMMARY': escape(film['cuts'][0]['summary']),
        'CUT_BUTTONS': ''.join(f'<button type="button" data-cut="{escape(c["id"])}" aria-pressed="{"true" if i == 0 else "false"}">{escape(c["label"])}</button>'
                               for i, c in enumerate(film['cuts'])),
        'GATE': ''.join(f'<li><span>{inline(item)}</span></li>' for item in gate),
        'TECH_GATES': ''.join(f'<li><span>{inline(item)}</span></li>' for item in checks),
        'TOOLS': ''.join(f'<li>{inline(name)}<span>{inline(what)}</span></li>' for name, what, *_ in tools),
        'PROVIDERS': ''.join('<tr>' + ''.join(f'<td>{inline(cell)}</td>' for cell in row) + '</tr>' for row in providers),
        'BUNDLE': BUNDLE,
        'SKILL_SOURCE': escape(skill),
    }
    page = (site / 'template.html').read_text(encoding='utf-8')
    for key, value in replacements.items():
        page = page.replace('@@' + key + '@@', value)
    if re.search(r'@@[A-Z_]+@@', page):
        raise ValueError('Unresolved template placeholder')
    output.mkdir(parents=True, exist_ok=True)
    assets = output / 'assets'
    assets.mkdir(exist_ok=True)
    (output / 'index.html').write_text(page, encoding='utf-8')
    shutil.copy2(site / 'theme/style.css', assets / 'family.css')
    shutil.copy2(site / 'theme/LICENSE', assets / 'family-LICENSE.txt')
    shutil.copy2(site / 'style.css', assets / 'style.css')
    shutil.copy2(site / 'site.js', assets / 'site.js')
    shutil.copy2(ROOT / 'tools/audit-hook.js', assets / 'audit-hook.js')   # the page runs the hook the skill ships
    for asset in sorted((site / 'assets').iterdir()):
        if asset.is_file():
            shutil.copy2(asset, assets / asset.name)
    (assets / 'film.json').write_text(json.dumps(film, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    documentation = skill_files() + ['README.md', 'LICENSE', 'CHANGELOG.md', 'site/README.md', 'site/theme/LICENSE']
    documentation += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'docs').rglob('*')) if p.is_file() and not p.name.startswith('.')]
    for name in documentation:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    (output / '.nojekyll').touch()
    # Fixed archive metadata makes the download reproducible across builds.
    with ZipFile(output / BUNDLE, 'w', ZIP_DEFLATED) as bundle:
        for name in skill_files():
            info = ZipInfo('sizzle/' + name, (2026, 10, 16, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o755 if (ROOT / name).stat().st_mode & 0o100 else 0o644) << 16
            bundle.writestr(info, (ROOT / name).read_bytes())
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site', help='Static output directory (default: _site)')
    args = parser.parse_args()
    print(f'Built {build(args.output.resolve())}')
