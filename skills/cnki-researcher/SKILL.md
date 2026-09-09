---
name: cnki-researcher
description: Coordinate a CNKI literature workflow from search and screening to evidence-based reading and citation export.
---

# CNKI research workflow

Use the eight sibling cnki-* skills when installed; read each before its stage.
If one is missing, report the missing module and perform only stages supported
by the available tools. These are instructions, not automatic subagent spawning.

1. State the database, query/fields, period, sort, requested count and citation scope.
   Default to Chinese journal articles. For “since 2023” use 2023-01-01 through today.
2. Use cnki-search or cnki-advanced-search, cnki-navigate-pages and cnki-parse-results.
   Freeze a unique, source-linked result list before screening; retain site rank.
3. Select the requested subset based on title/abstract relevance to the question.
   Explain selection and retain original list numbers. Do not substitute newer or
   better-known papers outside the list without clearly reporting the change.
4. Use cnki-paper-detail. Full-text analysis requires retrieved readable full text;
   otherwise label abstract/preview analysis and identify missing evidence.
5. Use cnki-export for the requested citation set. If “export the citations” is
   unspecified, export the listed set and a separate selected-subset file.
6. Before delivery compare all titles/identifiers against extracted records,
   ensure no duplicate filler entries, and verify exported counts and file paths.
7. Return the search manifest, result list, reading analysis, .bib artifact and
   any limitations. Never claim a blocked stage completed.

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
