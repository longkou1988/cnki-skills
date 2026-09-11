---
name: cnki-download
description: Download CNKI papers as PDF by default through authorized native links; use CAJ only when explicitly requested or accepted.
---

# CNKI download

1. Verify the requested paper identity and the user's download request. Default to PDF unless the user explicitly requests another format. Carry this preference through retries and batch operations. Before starting any transfer, create the local date folder described below.
2. Inspect the paper's observed native download controls, including any download menu. Prefer a control explicitly labeled PDF or PDF下载. A generic 下载/整本下载 button does not establish the format; inspect its options or the paper detail page before proceeding. Do not reconstruct file endpoints, change URL parameters to force PDF, replay cookies, use another institution's proxy or purchase access without explicit authority.
3. If no authorized PDF option is available after inspecting those controls, mark the item “PDF unavailable” or “PDF access blocked” as appropriate and continue other requested items. Do not silently fall back to CAJ. Download CAJ only if the user explicitly requests or accepts it; prior acceptance within the same task remains valid. Do not rename CAJ to .pdf, install a converter/viewer or print HTML as a substitute PDF unless separately requested.
4. Verify the actual file using the browser's documented download receipt or an authorized local directory: completed transfer, non-empty file and matching paper identity. For PDF, confirm PDF content using file-type inspection or a PDF reader/parser; extension alone is insufficient. CAJ or an HTML login/error page saved as .pdf is failure. Report an unexpected format and retain the PDF preference on retry; do not delete the unexpected file automatically.
5. Batch only specifically requested records; verify selected identities/count and the chosen PDF format, obey the displayed batch limit and collect per-item status. If the batch control only offers CAJ or its format is unclear, use individual verified PDF controls instead. Report remaining unavailable items without substituting CAJ.
6. Return the absolute date-folder link and confirmed local file links, plus blocked/failed items and reasons. Only count a file as saved when it has been verified in that folder. If the runtime cannot inspect the saved file, say “download initiated, file not verified.”
7. Do not upload full texts to GitHub, Zotero or another service unless separately requested. Zotero import is optional and requires available connector support; this package does not transfer authenticated browser cookies.

## Local destination — create first

- Unless the user specifies a destination, use the user's Downloads directory with
  `CNKI/YYYY-MM-DD/` beneath it (for example, `~/Downloads/CNKI/2026-09-11/`).
  Resolve the actual absolute path; do not pass a literal `~` to a browser API.
- Compute the date once at task start in the user's local timezone and create the
  folder before clicking Download. Reuse an existing same-date folder without
  clearing it. If the user supplies a base directory, create the date subfolder
  there; if they supply an exact final folder, respect it without double nesting.
- Use a documented per-download or per-session destination setting when available.
  Do not invent browser APIs or change global browser preferences. If the browser
  only saves to its default directory, use the exact completed-download receipt
  to identify each task-owned file, then move it into the date folder and verify
  it there. Never sweep the Downloads directory or move unrelated files.
- Keep a useful title/author filename when possible, sanitize filesystem-invalid
  characters, and retain `.pdf` only for confirmed PDFs. Never overwrite an
  existing file: reuse a verified identical paper or append a unique suffix.
- If local filesystem access or download receipts are unavailable, report that
  limitation and the actual known save location; do not claim the requested
  folder was created or populated. Never substitute a cloud upload.

## Efficient execution and bounded waiting

- Reuse the authorized logged-in session, existing result list and already verified
  paper metadata. Do not repeat searches, reload the homepage or reopen a detail
  page for each retry when the current observed PDF control is still valid.
- For multiple requested papers, prefer a verified native PDF batch operation
  within the displayed limit. Otherwise use individual PDF controls, keeping a
  per-item receipt/status. Do not launch duplicate transfers while one is active,
  or add unbounded parallel requests that could trigger site throttling.
- Prefer documented completion events/receipts over fixed sleeps. Where polling
  is necessary, check the specific transfer at short bounded intervals (about
  2–5 seconds if supported), stop immediately on completion, and verify once.
  A changing byte count or transfer status is progress; a repeated screenshot is
  not. Do not repeatedly parse a partially downloaded file.
- If there is no observed progress for 60 seconds, inspect the current transfer
  and visible page once for a login, CAPTCHA, access or network error. Do not
  reclick an active download. Retry only a confirmed failed transfer, at most
  once; after a second failure without progress, report it and continue other
  accessible items. An active but stalled transfer should be reported as pending,
  not silently restarted or called complete.
- Continue waiting on a progressing transfer, keeping the user informed at least
  once per minute. Respect user-specified deadlines and runtime wait limits.
  Report site-side blockers honestly; these workflow rules do not guarantee
  faster CNKI network throughput.

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
On 2026-09-11 a domestic run downloaded five 生成式人工智能 papers with the
detail-page **PDF下载** control under an institutional login; each file was
checked with the `%PDF-` header and `file` type report. The result-list 下载 link
does not name a format — a run the same day took that link and received a `.caj`
file — so resolve the format on the detail page, where CAJ下载 and PDF下载 are
separate controls. Domestic PDF download is therefore verified; native citation
export and batch download are not.
Treat domestic and international platforms separately. Never report an attempted
click as a successful search/export/download. Keep publication date, online-first
date and indexing date distinct. Missing fields stay missing.
