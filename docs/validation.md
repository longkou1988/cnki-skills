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
| Complete author list and detail/full text | Not tested | Not tested | Not tested |
| Journal issue navigation | Not tested | Not tested | Not tested |
| Native single/batch citation export | Not tested | Not tested | Not tested |
| Actual authorized PDF/CAJ download | Not tested | Not tested | Not tested |

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
