---
name: cnki-evidence-table
description: Build an evidence-linked Excel comparison of CNKI empirical papers, including samples, variable measurement, identification, robustness and mechanisms; distinguish abstract evidence from full-text reading.
---

# 实证研究对照表

Use for “比较这几篇论文的数据、变量、内生性处理和机制检验，附原文页码”。
Use cnki-paper-detail for source reading and cnki-download only when downloads
are authorized. Reading supplied local PDFs does not require another download.

1. Read [the shared ledger schema](../cnki-resume/references/schema.md), then use
   `../cnki-resume/scripts/workflow.py`. Reuse the current task. For a user-selected
   set without earlier screening, initialize a task with selection criteria
   “用户指定文献”; import and mark each paper included with its observed title as
   evidence. Do not invent a separate exclusion exercise.
   When the user requires full-text reading, initialize with
   `required_access: full_text`; partial evidence stays blocked until fulfilled.
2. Confirm title/author identity against each source. Read accessible material;
   record `full_text`, `preview` or `abstract_only`. Scanned/unreadable PDFs are a
   blocker until readable content is available, not completed full-text reading.
3. Extract supported fields from the schema. Every non-empty field requires
   `value`, a short exact `quote`, `locator`, and `source`. Prefer PDF page number
   (1-based), printed page if different, table number and section. For abstracts
   use locator `摘要` and only facts explicitly stated there. Do not infer sample
   size, coefficients, causal identification or mechanisms from a title.
4. Missing fields stay null. Distinguish “未报告” (checked the relevant full-text
   sections) from “未提取/证据不足” (not known). Record author's claims separately
   from your evaluation; field `limitations` contains author-stated limitations.
   Preserve model/column, units and sample context when recording an effect size.
   The program validates evidence structure, not whether a quote supports a claim;
   the agent must check every value against the source before saving `extract`.
5. Save each paper immediately and export `研究工作表.xlsx`. The 实证研究对照表
   sheet holds comparisons; 原文证据 holds per-field source excerpts and locators.
   All included papers remain visible, even if not yet read. Report the number
   with completed extraction, the number read in full, and missing evidence.

Do not claim causal effects merely because the authors report correlations.
Do not upload PDFs or the private ledger to the repository or third-party services.
