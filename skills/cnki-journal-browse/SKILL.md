---
name: cnki-journal-browse
description: Browse a journal and its issues on CNKI through observed publication-navigation links.
---

# CNKI journal-browse

1. Use the visible 出版物检索/期刊导航 control from the CNKI entry or a supplied journal link. Search the exact journal name.
2. Verify identity by journal title, ISSN/CN number and publisher if displayed; do not convert the name to a guessed URL slug.
3. Read journal scope and accessible metadata, then open the offered year/issue controls and extract its article list.
4. If the user requests latest articles, distinguish online-first material from the most recent numbered issue.
5. Report any journal metrics with the source edition/year. Do not equate CNKI composite impact factor with JCR impact factor or infer a current core-journal classification.
6. Extract article links from the issue itself; preserve sequence and mark shortened authors. Pagination follows visible controls.
7. External editorial/publisher links are a separate destination; label them and preserve the user's access route.

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
