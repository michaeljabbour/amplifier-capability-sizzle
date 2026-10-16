# Website

This page follows the Taste × Elegance skill site: a small static Python build, the Amplifier family visual language, a two-column hero, local assets, fine rules and restrained navigation. The generated `_site/` directory works on any static host, including a repository subpath on GitHub Pages, because every link is relative or a page anchor. `.github/workflows/pages.yml` builds, checks and publishes `_site/` from `main`.

## Build and preview

From the repository root, with Python 3.11 or later:

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open `http://127.0.0.1:8000`. The build uses only Python's standard library. The film's notes load from a local JSON file, so preview over HTTP rather than opening the HTML with `file://`.

## Edit

- `site.json`: metadata, and the invented film's title, brief, string roles and the notes for each cut.
- `template.html`: semantic page content and layout.
- `style.css`: product styles and responsive behavior.
- `site.js`: the invented film, drawn as a pure function of time; its audit, using the hook in `../tools/audit-hook.js`; the in-browser lint and motion checks, with the rules of `../tools/lint.mjs` and `../tools/motion.mjs`; and copy feedback.
- `assets/`: the SVG favicon and share card, and the poster shown without JavaScript. Some social platforms need raster share images; no claim of platform support is made for the SVG.
- `../SKILL.md` and `../tools/README.md`: the source of the download, the bundle, the embedded source, the creative gate, the technical gates, the tool list and the provider table. Do not copy those lists into another content file.

## Theme provenance

`theme/style.css` is an unmodified snapshot of the Amplifier Smart Tools family theme v0.1.0, as preserved in the Taste × Elegance project. `theme/LICENSE` keeps its original MIT notice. The product template, film, SVG assets and styles are new.

## Design notes

- Paper `#f6f4ee`, ink `#252823`, muted `#64685e`, rules `#d8d8cc` and gold `#80642f` come from the family theme. The ember accent `#9c4426` reaches 5.8:1 on paper.
- Georgia headings and Arial body text, with system fallbacks and no font requests.
- The film is the one expressive element. It is invented for explanation, and its findings are measured from its own frames in the browser.
- Nothing moves on its own. The film plays only from its Play control, and the scrubber, the cut buttons and the audit toggle are native controls. Reduced motion turns off smooth scrolling. Without JavaScript, a poster and a link to the worked example remain.

## Deployment

The Pages source is GitHub Actions. The workflow separates build and deployment, checks the output before upload, and uploads only `_site/`. Deployment gets `pages: write` and `id-token: write`; the build has read access only. No project secrets or backend services are needed. Official GitHub action revisions are pinned to fixed commits. Pushes to `main` rebuild and redeploy the site, and manual runs are available from Actions.

The live URL is <https://michaeljabbour.github.io/amplifier-skill-sizzle/>. Keep asset, navigation and download paths relative so repository-subpath hosting works.
