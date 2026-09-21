# Validation record / 验证记录

Date: 2026-09-09. Local tests completed before 08:43 UTC.
Release status: experimental; offline components tested, live acceptance incomplete.

## Automated checks

Executed on Python 3.9 with bibtexparser 1.4.3 (independent output parser)
and PyYAML 6.0.2:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

12 tests passed: single Chinese citation parsing, batch unique keys and escaping,
DOI duplicate/conflict handling, distinct-ID retention, missing year omission,
incomplete-author rejection, RIS records/continuation/terminator validation,
EndNote tagged conversion, invalid metadata rejection, GB18030 CLI conversion
and overwrite refusal, nine skill frontmatters, both installation layouts and
existing-target protection. Fixtures are synthetic, not actual CNKI exports.

All nine SKILL.md folders also passed the Codex skill-creator quick validator.
Parser dependency emitted deprecation warnings but no test failures.
No Zotero/EndNote desktop import or LaTeX compilation was performed.

## Live attempts

| Stage | Codex | Claude Code | WorkBuddy |
|---|---|---|---|
| Browser connector | Chrome CDP navigation/focus timeouts; in-app browser works | CLI present; Chrome DevTools MCP not configured | `bsk` CLI + browser extension, works |
| Entry discovery | www.cnki.net redirected to overseas homepage | Not tested | kns.cnki.net domestic entry reached directly |
| Chinese UI | Language switch to /chn/ verified | Not tested | Domestic Chinese UI, no switch needed |
| Advanced-search entry | Click led to “拖动下方拼图完成验证” | Not tested | Not tested |
| Query submission and journal filter | Blocked before submission | Not tested | 主题 search submitted; 学术期刊 filter applied |
| Publication-date sorting and pagination | Not tested | Not tested | Not tested |
| Result deduplication against live rows | Not tested | Not tested | Observed network-first/正式版 duplicate of one title |
| Complete author list and detail/full text | Not tested | Not tested | Detail page opened; 文章目录 and metadata rendered |
| Journal issue navigation | Not tested | Not tested | Not tested |
| Native single/batch citation export | Not tested | Not tested | Not tested |
| Actual authorized PDF/CAJ download | Not tested | Not tested | Verified 2026-09-11: 5 × PDF, file-checked |

**WorkBuddy run (2026-09-09, domestic site).** Opened
https://kns.cnki.net/kns8s/defaultresult/index with the user's logged-in browser;
an institutional login was recognised. Entered 主题: 生成式人工智能 高校教师 and
submitted. The domestic result page returned 总库 1055 / 学术期刊 674 /
学位论文 210 / 会议 48, rendered the 篇名/作者/刊名/发表时间/被引/下载/操作 table,
and no CAPTCHA appeared. The first seven rows were parsed; one title appeared
twice (online-first and formally indexed versions of the same paper), which
confirms the deduplication rule. This verifies domestic search and result
parsing only.

No CAPTCHA was solved, access purchased, credentials captured or full text
redistributed. The earlier overseas entry observation does not verify domestic
KNS; the domestic run above does verify search and parsing but not export or
download. No CNKI citation fixture is claimed.

## 2026-09-11 run (domestic site, WorkBuddy): PDF download verified

Environment: macOS, `bsk` 0.1.10 → 0.2.1, Chromium with an institutional login
(广东商学院华商学院) already present.

Query: 主题 = 生成式人工智能, 学术期刊 database, site default relevance sort.
Result counts: 总库 26,100 (2.61万) / 学术期刊 17,111. First page held 20 rows.

Five records were selected on title relevance and journal tier, keeping their
original list numbers (3, 9, 12, 14, 17). Each was opened on its detail page and
downloaded with the **PDF下载** control:

| List no. | Format | Size | Pages | `file` result |
|---|---|---|---|---|
| 3 | PDF | 984,203 B | 18 | PDF document, version 1.6 |
| 9 | PDF | 828,052 B | 9 | PDF document, version 1.6 |
| 12 | PDF | 764,462 B | 8 | PDF document, version 1.6 |
| 14 | PDF | 881,350 B | 7 | PDF document, version 1.4 |
| 17 | PDF | 1,658,611 B | — | PDF document, version 1.6 |

Every file was checked with the `%PDF-` header and the `file` type report; none
was an HTML login/error page, zero bytes, or a renamed CAJ file. This verifies
authorized domestic PDF download and file verification only. Native citation
export and batch download remain unverified.

Three failure modes were observed and are recorded in
[浏览器接入](browser-adapters.md):

1. `bsk click` on result-row links failed with `DOM Error while querying`
   (-32000). Root cause was protocol drift between the bsk CLI/daemon (0.1.10,
   protocol 1.0) and the browser extension (0.2.0, protocol 1.1). `bsk update -y`
   aligned the protocol (0.2.1 / 1.1) but row clicks still failed, so the run
   switched to read-only link extraction plus `bsk navigate`.
2. The first detail page opened behind 拖动下方拼图完成验证. The puzzle was handed
   to the user through `bsk request-help`; after control returned, a reload was
   needed before the download controls appeared. The puzzle was never automated.
3. `bsk reload` after a submitted search returned the empty entry page and lost
   the query and the 学术期刊 filter, so the search had to be re-entered.

A separate run the same day had downloaded one of these records from the
result-list 下载 link and received a `.caj` file. The result-list link does not
name a format; the detail page exposes separate CAJ下载 and PDF下载 controls.
This is the observed reason the PDF default must be resolved on the detail page.

## Reproducible acceptance procedure

On an authorized accessible CNKI journal search page:

1. Record retrieval time, actual platform/region and query field. Enter 主题:
   生成式人工智能 AND 主题: 企业创新, journal database only, 2023-01-01 through
   the test date (2026-09-09 for this release). Record synonym/translation expansion.
2. Record actual date filter semantics and selected descending publication-date
   sort. Verify page change while preserving filters.
3. Capture 20 distinct exact titles and links, or the actual shortfall. Check
   identity and complete author lists against details/native citations. Do not
   replace off-topic hits with invented/repeated titles.
4. Choose five based on relevance within that frozen set. Record the reason and
   access level. A preview/abstract analysis must not be described as full-text reading.
5. Export one citation and a batch; verify source counts, complete authors,
   identifiers and BibTeX parser/import results. Label native versus converted.
6. For an accessible paper requested for download, verify completed file transfer,
   format and identity. If none is accessible, mark blocked rather than pass.
7. Run separately in both environments. Update this table only with actual
   evidence; do not publish private account details or session-bearing URLs.

Public references consulted for workflow terminology:
- [CNKI domestic search entry](https://kns.cnki.net/kns8s/defaultresult/index), directly observed (default entry for these skills).
- [CNKI international Chinese homepage](https://oversea.cnki.net/chn/), observed earlier; fallback platform only.
- [CNKI usage guide hosted by Quanzhou Normal University Library](https://lib.qztc.edu.cn/2022/0405/c4818a267143/page.htm),
  useful for export/navigation terminology, not evidence of current DOM.


## 2026-09-21: screening, evidence tables and resume

31 automated tests passed locally, including the 12 existing tests. New coverage:
transaction rollback on conflicting imports, DOI enrichment without changing task
identity, ambiguous duplicate retention, evidence/access validation, invalidating
extraction after screening changes, idempotent screening replay, process restart,
concurrent claims (one wins), active-transfer inspection, artifact format/hash and
missing-file checks, required-full-text blockers, Excel/CSV formula safety,
independent workbook parsing using openpyxl, invalid-output cleanup, CLI errors,
and backed-up installation upgrades with unrelated-skill/symlink protection.

The three new skills and updated coordinator passed skill-creator validation.
`python3 scripts/demo_workflow.py --output <new-directory>` produced a five-sheet
XLSX, five CSVs, an audit snapshot and resumable SQLite ledger from three explicitly
synthetic records (included, excluded, uncertain). XLSX was read independently with
openpyxl; frozen headers, evidence locators, unknown fields and string cell types
were checked. No live CNKI search, article screening accuracy, PDF reading accuracy,
Excel desktop rendering or native citation export is claimed by this test run.
The runtime helper uses only the standard library; openpyxl is a test dependency.
