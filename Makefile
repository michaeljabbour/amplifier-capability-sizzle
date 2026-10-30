.PHONY: build check preview scan
build:
	python3 scripts/build.py
check: build
	python3 scripts/check.py
	node --check site/site.js
	for f in tools/*.mjs tools/audit-hook.js; do node --check $$f || exit 1; done
	python3 -c "import ast, sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]" tools/*.py scripts/*.py
preview: build
	python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
scan:
	rm -rf .work/scan && mkdir -p .work/scan
	python3 scripts/capability.py install --dest .work/scan
	skillspector scan .work/scan/sizzle --no-llm --baseline .skillspector-baseline.yaml
