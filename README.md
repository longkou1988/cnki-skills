# CNKI Skills

面向 **Codex 和 Claude Code** 的知网文献工作流技能包。对应 ScienceDirect
技能包的 8 个操作模块，另附 Claude agent 和 Codex 可安装入口。

**状态：实验版。** 离线引用转换有自动化测试；中国知网国内站的检索、翻页、
详情、下载和原生引用导出尚未完成端到端验证。开发时官网跳转国际版，
进入高级检索遇到拼图验证。请见 [测试记录](docs/validation.md)。
本包是由 AI 按实时页面执行的技能说明，不是固定选择器爬虫或知网官方 API。

[English](README.en.md) · [浏览器配置](docs/browser-adapters.md) · [来源声明](NOTICE.md)

## 功能

| 技能 | 用途 |
|---|---|
| cnki-search | 基础关键词检索 |
| cnki-advanced-search | 主题、篇名、作者、机构、来源与日期筛选 |
| cnki-parse-results | 提取结果、去重、保留原始排序 |
| cnki-navigate-pages | 翻页、每页条数、日期排序 |
| cnki-paper-detail | 完整题录、摘要、可访问全文分析 |
| cnki-journal-browse | 期刊导航及卷期浏览 |
| cnki-download | 授权范围内的 PDF/CAJ 下载与文件核验 |
| cnki-export | 原生引用导出，或离线转成 BibTeX |
| cnki-researcher | 统筹以上步骤的入口 |

## 安装

Python 3.9+；先自行配置所在环境支持的浏览器连接。
克隆后可预览安装目标，安装器拒绝覆盖已有同名技能：

```sh
git clone https://github.com/longkou1988/cnki-skills.git
cd cnki-skills
python3 scripts/install.py --target codex --dry-run
python3 scripts/install.py --target codex
# Claude Code 用户：
python3 scripts/install.py --target claude
```

Codex 默认安装到 CODEX_HOME/skills（未设置时 ~/.codex/skills）；
Claude 默认安装到 ~/.claude/skills，并安装 ~/.claude/agents/cnki-researcher.md。
如需项目级安装，添加 `--project /path/to/project`：
Codex 使用 .agents/skills，Claude 使用 .claude/skills 和 .claude/agents。
刷新/重新打开会话后确认技能可见。不会更改 MCP、账号或浏览器设置。

## 使用

Codex 中显式引用 `$cnki-researcher` 或对应操作技能；Claude Code 中调用
`/cnki-researcher`，也可请求使用 cnki-researcher agent。

> 使用 cnki-researcher，在知网期刊库查找 2023 年以来“生成式人工智能”与
> “企业创新”的文献，按发表时间倒序列出前 20 篇，分析其中最相关的 5 篇，
> 导出全部题录和入选 5 篇的 BibTeX。

默认使用当前已授权的知网入口；记录实际日期口径和词扩展设置。
若只能取得摘要，会标注“摘要分析”；不会把摘要当作全文精读。
登录、验证码或缺少订阅时返回明确进度。不会自动购买论文、绕过验证或
复制浏览器凭据。Zotero 可在用户明确要求时通过已有工具导入生成的 .bib，
本包不包含 Cookie 推送。

## 离线转换

```sh
python3 skills/cnki-export/scripts/convert.py records.json --format json --output references.bib
python3 skills/cnki-export/scripts/convert.py export.ris --format ris --output references-ris.bib
python3 skills/cnki-export/scripts/convert.py export.enw --format endnote --output references-endnote.bib
```

无运行时第三方依赖。支持 JSON、RIS、EndNote tagged 的期刊题录；
[输入格式](skills/cnki-export/references/formats.md)。
保留中文姓名、处理特殊字符、合并一致重复项；作者不全、重复冲突会报错。
不会覆盖已有文件。知网原生导出格式以实际页面为准；
转换结果明确标为“离线转换”，不能冒充原生导出。

## 测试

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
```

MIT；独立实现，功能结构受 cookjohn/sd-skills 启发，详见来源声明。
