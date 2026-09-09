# Offline citation formats

Use only verified bibliographic data. The converter does not fetch CNKI or infer
missing fields. It supports journal articles only. It refuses to overwrite output.

JSON is a record or array:

```json
{
  "type": "article",
  "title": "示例题名（合成测试数据）",
  "authors": ["张三", "李四"],
  "authors_complete": true,
  "journal": "示例期刊",
  "year": "2026",
  "volume": "12",
  "issue": "3",
  "pages": "1-9",
  "url": "https://example.org/paper"
}
```

Required: title, authors array, authors_complete=true, journal.
Optional string fields: year, volume, issue, pages, doi, url, cnki_id
(include database + filename when both are observed).
Unknown optional fields must be omitted. Authors are preserved as literal BibTeX
names, avoiding guessed Chinese family/given-name splits; do not split a compound
Chinese name. Journal names, titles and individual authors must be source-verified.

RIS: TY=JOUR, TI/T1, AU/A1 (one author per tag), JO/JF/T2, PY/Y1,
VL, IS, SP, EP, DO, UR, and mandatory ER record terminator.
EndNote tagged: %0 Journal Article, %T, repeated %A, %J, %D, %V, %N,
%P, %R (DOI only), %U. Records begin with %0. Indented continuation lines
are supported. Other formats (including RefWorks and NoteExpress) are not parsed;
select a supported native format or verify fields into JSON.

Native export author lists must be complete; the converter rejects explicit
ellipsis/“等”/et al. Re-check against the detail page when completeness is unclear.
Exact strong-ID duplicates are merged only if non-empty fields agree. Ambiguous
title matches with distinct IDs are kept for manual review. Conflicts stop conversion.
The converter reports counts and warnings to stdout; retain these in the local run
manifest with input format, source page, retrieval time and native/converted status.
Do not put session-bearing URLs or personal library exports into a public repository.
