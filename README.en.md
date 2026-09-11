# CNKI Skills

CNKI literature workflow skills for **Codex, Claude Code and WorkBuddy**: eight
operation skills, a Claude agent and an installable Codex workflow entrypoint.

**Defaults to the domestic CNKI site.** Every skill starts from
`https://kns.cnki.net/kns8s/defaultresult/index` (verified working: renders the
subject search and journal filters, honours an institutional login), falling back
to `https://www.cnki.net/`. Overseas mirrors such as oversea.cnki.net and
global.cnki.net are never the starting point — the homepage may redirect there
silently depending on the network exit point. They are used only as a last-resort
fallback, after telling the user why the domestic site failed. See
[Browser adapters](docs/browser-adapters.md).

**Experimental release:** offline citation conversion is tested. Domestic search,
result parsing and PDF download are now verified end to end (2026-09-11: subject
search under an institutional login, five PDFs taken from the detail-page
PDF下载 control and checked with the `%PDF-` header and `file`); native citation
export and batch download are still unverified. The 下载 link in the result list
does not name a format and may deliver CAJ — confirm the format on the detail
page. Detail pages can also open behind a puzzle CAPTCHA that needs the user.
Earlier development runs were redirected to the overseas site, where advanced
search triggered a CAPTCHA. See [validation](docs/validation.md) and
[Browser adapters](docs/browser-adapters.md).

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

**WorkBuddy** installs to ~/.workbuddy/skills (installer target added in 1.1;
with older copies, copy the directories manually):

```sh
python3 scripts/install.py --target workbuddy
# or manually: for d in skills/*/; do cp -R "$d" ~/.workbuddy/skills/; done
```

WorkBuddy drives the logged-in browser through the `bsk` CLI from `browser-skill`:
`bsk session start` → `bsk navigate <url> --session <id>` → `bsk snapshot` →
interact → `bsk session stop <id>`.

If `bsk click` reports `DOM Error while querying`, suspect protocol drift between
the bsk CLI/daemon and the browser extension: run `bsk update -y` and start a new
session; if it still fails, extract the links the page already exposes read-only
and `bsk navigate` to one of them. See
[Browser adapters](docs/browser-adapters.md).

## Modules

cnki-search (keywords), cnki-advanced-search (fields/dates),
cnki-parse-results (extraction/deduplication), cnki-navigate-pages (pages/sort),
cnki-paper-detail (metadata/reading), cnki-journal-browse (journal/issues),
cnki-download (PDF by default; CAJ only when explicitly requested or accepted), cnki-export (citations),
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

## Follow me

<p align="center">
  <img src="assets/wechat-channel-qrcode.png" alt="Scan the QR code to follow my video channel" width="280">
  <br>
  <sub>Scan the QR code to follow my WeChat video channel</sub>
</p>
