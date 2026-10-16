# Working on Sizzle

- Read `SKILL.md`, `references/lessons.md` and `tools/README.md` before changing the skill. Keep the skill's order and its hard rule: no generation call before the creative gate passes.
- Keep the `SKILL.md` body under 500 lines and portable: no host-specific syntax, and every `tools/` or `references/` path it names must exist. History and evidence go in `references/`, not in the skill.
- The site reads the creative gate and the technical gates from `SKILL.md`, and the tool and provider tables from `tools/README.md`, at build time. Change them there, never in the site's content.
- Tools stay small and copyable one by one. `tts.py` uses only the standard library. Keys come only from environment variables, are never printed or logged, and a paid request is never retried automatically.
- When a tool changes, run it on `tools/fixture.html` and confirm its known findings: lint reports SIZE, READ, SAFE and HIT; motion flags the dot.
- Write in American English, in plain words, with no em dashes and no hype. Use no client names, real people's names, email addresses, home directory paths or keys anywhere. Screenshots show only the product page, without metadata.
- Run `python3 scripts/build.py`, `python3 scripts/check.py` and `node --check site/site.js`, and inspect desktop and phone layouts after UI changes.
- Do not add a remote, push, publish, deploy or contact anyone unless asked.
