---
name: cnki-export
description: Export CNKI citations natively or convert verified JSON, RIS or EndNote tagged records into UTF-8 BibTeX.
---

# CNKI export

1. Resolve the requested set (single, selected list or all listed papers). Preserve exact titles and identities. Verify selected checkboxes before opening the visible 导出/参考文献 control; do not assume selection survives paging.
2. Prefer an offered native BibTeX option. Otherwise export the actual offered EndNote tagged or RIS format, or build verified structured JSON from detail metadata. Do not call a constructed conversion a native CNKI export.
3. For format details and schema read [references/formats.md](references/formats.md). Convert with [scripts/convert.py](scripts/convert.py):
   `python3 <skill-dir>/scripts/convert.py input.json --format json --output citations.bib`
   Formats: json, ris, endnote. Input encoding defaults to UTF-8; explicitly use --encoding gb18030 if confirmed.
4. The converter is offline and refuses incomplete author lists, conflicting duplicate metadata and unsupported record types. Resolve those from the source; do not weaken validation to force an export.
5. Validate the resulting file with an independent BibTeX parser when available, count unique entries, compare titles/DOIs/authors to the source and test Chinese names/special characters. The converter's successful exit alone is not an import test.
6. Deliver the .bib file and conversion provenance/warnings. Missing year/volume/pages remain omitted. If only a formatted GB/T reference is available, verify individual fields against the detail page before forming JSON; do not regex-guess all metadata from prose.
7. Optional Zotero: import the .bib through an available, documented local connector only when requested. No cookie transfer or bundled third-party push script.

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
