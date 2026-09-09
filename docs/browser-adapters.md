# Browser adapters / 浏览器接入

## Codex
Use an already available browser tool or browser skill. Inspect its documented
methods first. With Codex desktop computer use, discover current tabs, read the
accessibility state, fill/click observed elements, then fetch new state after each
navigation. Only use read-only page evaluation if the runtime supports it.
Codex CLI without browser tools cannot run the live stages; offline conversion
still works. Installing these skills does not install or configure a browser plugin.

## Claude Code
Use a configured Chrome DevTools MCP server. Typical workflow:
list_pages → select_page (or new_page) → take_snapshot → fill/click → take_snapshot.
Read the available tool schema instead of assuming parameter names.
Use evaluate_script only for grounded, read-only page extraction if supported.
A user can configure the server using the official package instructions:
https://github.com/ChromeDevTools/chrome-devtools-mcp
No anti-detection flags or webdriver overrides are required by this package.
The development environment did not have this MCP configured; CLI presence alone
does not establish compatibility.

## WorkBuddy
WorkBuddy drives the user's real, logged-in Chromium through the `bsk` CLI
provided by the `browser-skill` package (`bsk` must be on PATH and the browser
extension connected; `bsk status` confirms this).

```sh
bsk session start                      # prints a 4-letter session id
bsk navigate <url> --session <id>
bsk snapshot --session <id>            # aria tree with @e1, @e2 … refs
bsk fill @e16 --value "…" --session <id>
bsk click @e18 --session <id>
bsk session stop <id>                  # mandatory, even on failure paths
```

Refs invalidate after navigation, so re-snapshot before every interaction.
`bsk session stop <id>` must run in a finally-style path; never rely on the idle
timeout. Login and CAPTCHA are human steps: call `bsk request-help` instead of
retrying blindly.

## Domestic entry (default) — observed 2026-09-09
Navigating directly to https://kns.cnki.net/kns8s/defaultresult/index reached the
domestic 检索 page (page title 检索-中国知网). Observed:
- 主题 field selector plus an empty keyword textbox
- database selector 总库, and per-type counts (学术期刊, 学位论文, 会议, 报纸 …)
- result table with columns 篇名 / 作者 / 刊名 / 发表时间 / 被引 / 下载 / 操作
- an institutional login banner was honoured; a 主题 keyword search returned
  total + per-database counts with no CAPTCHA

Use this entry first. https://www.cnki.net/ is the domestic fallback, but it may
redirect to the overseas site depending on the network exit point — check the
page title and host after navigating.
The search submit control sits next to the keyword box and carries no accessible
label; identify it by snapshot position rather than by name.

## Overseas entry (fallback only) — earlier observation
A visit to https://www.cnki.net/ in one in-app browser redirected to
https://oversea.cnki.net/index/. The English site exposed Switch language,
Subject, search, Advanced Search and Publication Search.
Choosing 简体中文 reached https://oversea.cnki.net/chn/:
- 主题 search field (observed id txt_SearchText)
- 搜索 (observed id search)
- 高级检索 linking to /kns8s/advsearch?language=chs
- 出版物检索 linking to /knavi/?language=chs
- 中国学术期刊全文数据库 linking to /res/category/journal?language=chs

These are observations of the international Chinese page, not assertions about
the domestic KNS page. Re-observe at runtime. On the overseas platform clicking
高级检索 triggered “拖动下方拼图完成验证”. Do not retry repeatedly or solve without
the runtime-required user interaction.
Use this platform only when the domestic site is genuinely unreachable or blocked,
after telling the user the observed reason; the two platforms index different
corpora, so counts and full text are not comparable. A region redirect is not
permission to claim domestic-platform acceptance.

For a stalled tab inspect whether a new tab or overlay appeared before retrying.
Retain the current query/selected-record manifest locally; omit credentials,
session query strings and personal account details from any public test record.
