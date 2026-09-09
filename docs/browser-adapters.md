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

## Observed CNKI entry (2026-09-09)
A visit to https://www.cnki.net/ in the in-app browser redirected to
https://oversea.cnki.net/index/. The English site exposed Switch language,
Subject, search, Advanced Search and Publication Search.
Choosing 简体中文 reached https://oversea.cnki.net/chn/:
- 主题 search field (observed id txt_SearchText)
- 搜索 (observed id search)
- 高级检索 linking to /kns8s/advsearch?language=chs
- 出版物检索 linking to /knavi/?language=chs
- 中国学术期刊全文数据库 linking to /res/category/journal?language=chs

These are observations of the international Chinese page, not assertions about
the domestic KNS page. Re-observe at runtime. Clicking 高级检索 triggered
“拖动下方拼图完成验证”. Do not retry repeatedly or solve without the runtime-required
user interaction. The domestic mainland results/detail DOM remains unverified.
A region redirect is not permission to claim domestic-platform acceptance.

For a stalled tab inspect whether a new tab or overlay appeared before retrying.
Retain the current query/selected-record manifest locally; omit credentials,
session query strings and personal account details from any public test record.
