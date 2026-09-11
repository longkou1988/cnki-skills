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
   When downloads are requested, use cnki-download with PDF as the default.
   Create the local Downloads/CNKI/YYYY-MM-DD folder first (user's local date;
   respect a supplied destination), then save and verify files there. Reuse the
   current session and follow cnki-download's bounded progress-based waiting.
   Preserve an explicit user format choice; otherwise do not substitute CAJ
   when PDF is unavailable. Continue accessible items and report the shortfall.
5. Use cnki-export for the requested citation set. If “export the citations” is
   unspecified, export the listed set and a separate selected-subset file.
6. Before delivery compare all titles/identifiers against extracted records,
   ensure no duplicate filler entries, and verify exported counts and file paths.
7. Return the search manifest, result list, reading analysis, .bib artifact and
   any limitations. Never claim a blocked stage completed.

## Browser and access
Use the user's available browser connector. Claude Code: Chrome DevTools MCP
(list pages → select page → take snapshot → interact). Codex: use its available
browser skill/tool and documented API. WorkBuddy: the `browser-skill` CLI (`bsk`)
— `bsk session start` → `bsk navigate <url> --session <id>` → `bsk snapshot` →
interact → `bsk session stop <id>` (mandatory, even on error paths). Read that
tool's instructions first; do not assume Chrome DevTools names exist in the other
runtimes. If no connector is available, report the missing dependency, without
installing it implicitly.

Start at an already-open CNKI official/authorized institutional entry. Otherwise
**default to the domestic CNKI site**, in this order:
1. https://kns.cnki.net/kns8s/defaultresult/index — domestic 检索 entry (verified
   working: renders 主题 + 学术期刊 controls and the result table, and honours an
   institutional login).
2. https://www.cnki.net/ — domestic homepage, only if the entry above is unreachable.

Never start at an overseas mirror (oversea.cnki.net, global.cnki.net,
data.oversea.cnki.net, scholar.cnki.net, ar.oversea.cnki.net or similar).
Detection: if the page title is "CNKI Overseas" or the host contains `oversea`,
you are on the international platform — www.cnki.net may silently redirect there
depending on the network exit point. Navigate straight to the kns.cnki.net entry
above instead of staying on the mirror.
Preserve the current institution route and observed links; do not reconstruct
proxy URLs or trust a hostname solely because it contains "cnki".
Inspect current visible controls before acting; refresh observations after navigation.
Do not invent selectors, search API payloads, article URLs, download hashes or session tokens.
Use read-only DOM extraction only if supported and grounded in observed markup.
If an operation fails twice without progress, preserve completed records and report
the blocker. Login and CAPTCHA require user intervention under the runtime policy;
do not evade detection or bypass access controls. Do not export cookies or credentials.
Close owned temporary tabs when finished, retaining only a page needed for user handoff.

### Overseas fallback (last resort only)
Fall back to an overseas mirror only when the domestic site is genuinely
unreachable or blocked for the user — for example kns.cnki.net times out, returns
a network/ISP block page, or shows an access blocker with no institutional route
available. When that happens:
1. Tell the user explicitly that the domestic site failed, state the observed
   reason (timeout, block page, missing institution entitlement), and say you are
   switching to the international platform.
2. Record which platform produced every result: the overseas edition indexes a
   different corpus, so counts, full text and export formats are not comparable
   with domestic CNKI results.
3. Re-check whether an authorized domestic route exists before continuing; if the
   user has one, ask before settling for the overseas edition.
Do not treat a plain redirect to oversea.cnki.net as "the domestic site is down"
by itself — navigate to the kns.cnki.net entry first.

## Evidence
This release is a UI-guided workflow, not a tested site scraper. In development,
www.cnki.net redirected to oversea.cnki.net; Chinese language selection reached
/chn/, exposing 主题, 搜索, 高级检索 and 出版物检索. Clicking 高级检索 on the
overseas platform triggered a puzzle CAPTCHA before query submission.
A later run opened https://kns.cnki.net/kns8s/defaultresult/index directly: the
domestic 检索 page rendered 主题/学术期刊 controls and a result table, an
institutional login was recognised, and a 主题 keyword search returned 总库 /
学术期刊 / 学位论文 counts without a CAPTCHA. The domestic entry is therefore the
verified default; the overseas platform is fallback only (see above).
Domestic full-text download and export controls remain unverified. Treat domestic
and international platforms separately. Never report an attempted click as a
successful search/export/download. Keep publication date, online-first date and
indexing date distinct. Missing fields stay missing.
