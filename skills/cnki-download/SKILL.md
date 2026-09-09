---
name: cnki-download
description: Download CNKI papers through normal authorized PDF or CAJ links when the user requests downloads.
---

# CNKI download

1. Verify the requested paper identity and the user's download request. Inspect available PDF/CAJ/整本下载 controls and access status.
2. Use the observed native download control. Do not reconstruct file endpoints, replay cookies, use another institution's proxy or purchase access without explicit authority.
3. If only CAJ is available, report the format. Do not rename a CAJ file to .pdf or install a viewer implicitly.
4. Verify the actual file using the browser's documented download receipt or an authorized local directory: completed transfer, non-empty file, correct format and matching paper identity. An HTML login/error page saved as .pdf is failure.
5. Batch only specifically requested records; verify selected identities/count, obey the displayed batch limit and collect per-item status.
6. Return confirmed local file links where available, plus blocked/failed items and reasons. If the runtime cannot inspect the saved file, say “download initiated, file not verified.”
7. Do not upload full texts to GitHub, Zotero or another service unless separately requested. Zotero import is optional and requires available connector support; this package does not transfer authenticated browser cookies.

## Browser and access
Use the user's available browser connector. Claude Code: Chrome DevTools MCP
(list pages → select page → take snapshot → interact). Codex: use its available
browser skill/tool and documented API. Read that tool's instructions first;
do not assume Chrome DevTools names exist in Codex. If no connector is available,
report the missing dependency, without installing it implicitly.
Start at an already-open CNKI official/authorized institutional entry, otherwise
https://www.cnki.net/. Preserve the current institution route and observed links;
do not reconstruct proxy URLs or trust a hostname solely because it contains "cnki".
Inspect current visible controls before acting; refresh observations after navigation.
Do not invent selectors, search API payloads, article URLs, download hashes or session tokens.
Use read-only DOM extraction only if supported and grounded in observed markup.
If an operation fails twice without progress, preserve completed records and report
the blocker. Login and CAPTCHA require user intervention under the runtime policy;
do not evade detection or bypass access controls. Do not export cookies or credentials.
Close owned temporary tabs when finished, retaining only a page needed for user handoff.

## Evidence
This release is a UI-guided workflow, not a tested site scraper. In development,
www.cnki.net redirected to oversea.cnki.net; Chinese language selection reached
/chn/, exposing 主题, 搜索, 高级检索 and 出版物检索. Clicking 高级检索 triggered
a puzzle CAPTCHA before query submission. Treat domestic and international
platforms separately; domestic results/detail controls remain unverified. Never report
an attempted click as a successful search/export/download. Keep publication date,
online-first date and indexing date distinct. Missing fields stay missing.
