---
name: cnki-advanced-search
description: Search CNKI with subject, title, author, institution, journal and date filters using the current advanced-search UI.
---

# CNKI advanced-search

1. Open the visible 高级检索 link from the authorized entry. Inspect all available field and Boolean controls.
2. Translate intent into rows: topic → 主题, title → 篇名, author → 作者, institution → 作者单位, journal → 文献来源, only when those labels actually exist. If a field is unavailable, disclose that limitation instead of silently changing its meaning.
3. Connect separate concepts with AND. For the acceptance example use 主题=生成式人工智能 AND 主题=企业创新, journals only, publication date from 2023-01-01 through today's date. Preserve the user's own alternative query if provided.
4. Use the page's date controls; record whether they filter publication, online-first or year only. A year-only filter may include forthcoming issues: disclose this and inspect online dates when a strict cutoff matters.
5. Inspect any enabled synonym/Chinese-English expansion option; record the state and do not describe expanded search as exact matching.
6. Submit, then verify active criteria and result count. For newest first choose the visible date/发表时间 sort and verify descending selection. Do not pass ScienceDirect parameters such as qs, tak or sortBy.
7. Extract the requested results using cnki-parse-results if installed, or read each row's exact title, URL, date, source and displayed authors. Count unique records, preserve site order, and report missing/shortened fields.
8. If fewer results than requested, report the actual number. Broaden only within the user's scope and label the new search separately.

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
