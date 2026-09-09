---
name: cnki-navigate-pages
description: Change CNKI result pages, page size or sorting while retaining the current search criteria.
---

# CNKI navigate-pages

1. Observe query/filter summary, current page, first result ID/title and selected sort.
2. Use visible 下一页/上一页 or an actual page number control. Do not synthesize offsets or query-string parameters.
3. For newest first select the visible publication-date option and descending order; distinguish publication time from update/indexing time. Report the offered date definition.
4. Change page size only to an offered value. Re-observe which page is selected after the change.
5. Verify page/first-record change and unchanged search filters; if an unrelated page opens, recover using observed browser history.
6. Extract only after loading settles. If the list repeats, stop rather than looping or counting duplicates. If next is disabled, return the accumulated unique count.
7. Do not locally reorder dates and label that as the platform's sorting. If site order differs from displayed issue dates, retain the order and explain the date distinction.

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
