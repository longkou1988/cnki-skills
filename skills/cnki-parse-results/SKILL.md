---
name: cnki-parse-results
description: Extract and deduplicate records from the currently open CNKI results page without changing the search.
---

# CNKI parse-results

1. Verify the current page is a results list; an empty/loading page is not a zero-results finding.
2. Identify the result container and a representative row using current accessibility/DOM observations. Ignore menus, recommendations, advertisements and cited-reference lists.
3. Extract exact title, observed article URL, displayed authors, authors_complete, source, date, date_kind, document_type, DOI or observed record ID, site_rank and page. Never infer open access from a download link.
4. Distinguish “等”/ellipsis from a complete author list. If complete authors are needed, open the detail or native citation export. Do not invent a DOI from an identifier.
5. Deduplicate by normalized DOI; otherwise observed database+record ID. Without strong identifiers flag title/year matches for manual review. Similar titles with different DOIs remain distinct.
6. Preserve the site ordering and record displayed_count, unique_count, total_results, query, filters, sort and retrieved_at. A requested 20 rows must be 20 distinct observed papers, or an explicit shortfall.
7. Render numbered records with links and missing fields disclosed. Do not rename records, fill gaps with recommendations or re-count the same paper under another title.

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
