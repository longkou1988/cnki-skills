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
