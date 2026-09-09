# CNKI Skills

CNKI literature workflow skills for **Codex and Claude Code**: eight operation
skills, a Claude agent and an installable Codex workflow entrypoint.

**Experimental release:** offline citation conversion is tested. Domestic CNKI
search, pagination, details, file download and native export are not end-to-end
verified. The development browser was redirected to the overseas site, where
advanced search triggered a CAPTCHA. See [validation](docs/validation.md).

This is a UI-guided agent skill bundle, not a fixed-selector scraper or an official
CNKI API. [中文](README.md) · [Browser adapters](docs/browser-adapters.md)

## Install

Requires Python 3.9+ and a separately configured browser connector:
Codex's available browser tools, or Chrome DevTools MCP for Claude Code.

```sh
git clone https://github.com/longkou1988/cnki-skills.git
cd cnki-skills
python3 scripts/install.py --target codex --dry-run
python3 scripts/install.py --target codex
# Or:
python3 scripts/install.py --target claude
```

Default destinations: CODEX_HOME/skills (otherwise ~/.codex/skills), or
~/.claude/skills plus ~/.claude/agents. For project-local installation use
--project /path/to/project; Codex uses .agents/skills. Existing targets cause an
error before copying. No browser/MCP settings are changed.

## Modules

cnki-search (keywords), cnki-advanced-search (fields/dates),
cnki-parse-results (extraction/deduplication), cnki-navigate-pages (pages/sort),
cnki-paper-detail (metadata/reading), cnki-journal-browse (journal/issues),
cnki-download (authorized PDF/CAJ), cnki-export (citations),
cnki-researcher (workflow coordinator).

Example: “Use cnki-researcher to search Chinese journals for generative AI AND
enterprise innovation since 2023; list the latest 20, analyze the most relevant
five, and export BibTeX for both sets.”

Abstract-only analysis is explicitly labeled. Full-text reading requires actual
accessible full text. Login, CAPTCHA and subscription barriers return partial
progress; the bundle does not purchase access or transfer cookies.
Zotero import is optional via existing tools when explicitly requested.

## Offline conversion and testing

```sh
python3 skills/cnki-export/scripts/convert.py records.json --format json --output citations.bib
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

JSON, RIS and EndNote tagged journal records are supported. See the
[input contract](skills/cnki-export/references/formats.md). Names stay literal,
incomplete authors are rejected, duplicate conflicts fail, and missing optional
fields are omitted. Output is labeled offline-converted rather than native.
MIT. Independently authored; functional inspiration acknowledged in [NOTICE](NOTICE.md).
