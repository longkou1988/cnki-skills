---
name: cnki-search
description: Search Chinese journal literature on CNKI by keywords; use for basic China National Knowledge Infrastructure searches.
---

# CNKI search

1. Record the requested keywords verbatim; default to subject/主题 if that field is offered. State the actual field used. Do not silently add synonyms or restrictive filters.
2. Inspect the homepage search box and database selector. Choose academic journals/学术期刊 when available; otherwise search then filter to journals.
3. Enter keywords through the UI and submit. Wait for a result list, explicit zero-results message, or access blocker.
4. Report actual query, database, retrieval time, total count and current sort. Extract up to the requested count (default 20) through cnki-parse-results if installed; otherwise use the rules below.
5. Read each distinct result row: title and observed detail URL, displayed authors, source, date, document type, DOI/record identifier if exposed. Mark shortened author lists incomplete. Preserve site rank; never substitute a paraphrased title for a new record.
6. For additional pages use the visible next-page control, verifying the page indicator and changed first record. Stop at the count or end; report shortfalls. Deduplicate on DOI, then observed database+record ID, otherwise flag matching title/year for review.
Example: “使用 cnki-search 搜索生成式人工智能”。

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
