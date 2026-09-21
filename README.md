# CNKI Skills

面向 **Codex、Claude Code 和 WorkBuddy** 的知网文献工作流技能包。对应
ScienceDirect 技能包的 8 个操作模块，增加文献筛选、实证对照与续跑，
基础包共 12 个技能，另附 Claude agent 和 Codex 可安装入口。
新增 **[`cnki-jev` 可选扩展包](skills/cnki-jev/SKILL.md)**：用 Jev 按条件辅助初筛，
复杂判断交回大模型或人工复核，保留现有原文证据链。扩展**单独选装、默认关闭、
调用付费**；不安装也能完整使用基础包。

**默认访问中国知网国内站。** 检索统一从
`https://kns.cnki.net/kns8s/defaultresult/index` 进入（已验证可用：渲染主题
检索与学术期刊筛选，机构登录生效）；`https://www.cnki.net/` 作为备用入口。
不以 oversea.cnki.net、global.cnki.net 等海外镜像作为起始地址 —— 官网会按
网络出口静默跳转到国际版。仅当国内站确实无法访问或被限制时，才在明确告知
用户原因后回退到海外站，并标注结果来自哪个平台。详见
[浏览器配置](docs/browser-adapters.md)。

**状态：实验版。** 离线引用转换有自动化测试；国内站的检索、结果解析与 PDF
下载已完成真实端到端验证（2026-09-11 机构登录下按主题检索并用详情页 PDF下载
取到 5 篇 PDF，逐篇 `%PDF-` 与 `file` 核验通过），原生引用导出与批量下载仍待
验证。结果列表里的「下载」链接不标格式，实际可能给到 CAJ，格式要在详情页确认。
开发早期官网跳转国际版，在国际版进入高级检索遇到拼图验证；国内站详情页也可能
出现拼图验证，需人工完成。请见 [测试记录](docs/validation.md) 与
[浏览器配置](docs/browser-adapters.md)。
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
| cnki-download | 默认 PDF，先建 Downloads/CNKI/日期 文件夹再保存；有界等待与文件核验，CAJ 需明确指定或接受 |
| cnki-export | 原生引用导出，或离线转成 BibTeX |
| cnki-screening | 文献筛选表：纳入、排除、待判断及证据理由 |
| cnki-evidence-table | 实证研究对照表：变量、样本、方法及逐字段原文证据 |
| cnki-resume | 本地事务台账、任务续跑、文件校验、Excel/CSV输出 |
| cnki-researcher | 统筹以上步骤的入口 |
| cnki-jev（可选） | Jev 分层初筛、试运行对比、缓存与预算控制；排除和疑难项复核 |

| 安装选择 | 服务费用说明 |
|---|---|
| 基础包（12 个技能） | 不调用 Jev；原有 AI 模型和知网访问费用另计 |
| 基础包＋cnki-jev | 用户自行配置 TypeSafe API Key，启用后按服务商规则计费 |

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

**WorkBuddy** 安装到 ~/.workbuddy/skills（安装器 1.1 起支持；旧版本可手动复制）：

```sh
python3 scripts/install.py --target workbuddy
# 手动安装时，选择所需目录；cnki-jev 是可选项。
```

WorkBuddy 通过 `browser-skill` 提供的 `bsk` CLI 驱动已登录的真实浏览器：
`bsk session start` → `bsk navigate <url> --session <id>` → `bsk snapshot` →
交互 → `bsk session stop <id>`。

若 `bsk click` 报 `DOM Error while querying`，多为 bsk CLI/daemon 与浏览器扩展
的协议版本漂移：先 `bsk update -y` 并重启会话；若仍失败，改为只读提取页面已
给出的链接再 `bsk navigate`。详见 [浏览器配置](docs/browser-adapters.md)。

## 升级已有安装

```sh
git pull --ff-only
python3 scripts/install.py --target codex --upgrade --dry-run
python3 scripts/install.py --target codex --upgrade
```

`--upgrade` 会在目标配置目录的 `cnki-backups/时间戳/` 保存旧版本，再替换本包
技能；其他技能不动。已有同名技能中的自定义内容保留在备份中，可比对后迁回。
不带 `--upgrade` 仍拒绝覆盖。Claude/WorkBuddy 使用相应 `--target`。
升级后重新打开会话以发现新技能。

## cnki-jev 可选扩展包（调用付费）

已经安装基础包的用户，可单独添加扩展；首次安装也可一起选择：

```sh
# 已有基础包，只安装扩展，不覆盖基础技能：
python3 scripts/install.py --target codex --only-jev
# 首次安装基础包和扩展：
python3 scripts/install.py --target codex --with-jev
# 升级扩展，保留旧版备份：
python3 scripts/install.py --target codex --only-jev --upgrade
```

Claude Code / WorkBuddy 替换 `--target` 即可。默认安装命令只安装 12 个基础技能；
基础包升级不会修改已安装扩展。使用 `--with-jev --upgrade` 可以同时升级两者。

**安装不等于启用。** 扩展不附带 API Key，不会创建账户、充值或自动付费调用。
将[默认关闭的示例配置](skills/cnki-jev/references/config.example.json)复制到本地研究目录，
按已授权范围设置题名/摘要发送许可、调用次数、估算预算与当前单价，再通过环境变量
`TYPESAFE_API_KEY` 配置密钥。不要把密钥、真实摘要或研究台账提交到仓库。

三种模式：`off` 使用原流程；`shadow` 付费运行并与独立的原流程判断对比；
`assist` 付费生成辅助筛选建议。每篇文献的多个条件合并为一次请求，明确区分
满足、不满足和证据不足。**第一版不自动写入最终筛选结论**：纳入建议核对原文证据，
排除、不确定和复杂判断交回大模型或人工，最终结果仍由原有 `screen` 命令保存。
无摘要时直接回到原流程，不将信息缺失视为不相关。

调用次数上限严格按本地请求次数控制；美元预算是依据配置单价的保守估算，
不是服务商账单的硬上限。失败和中断保留费用预留，不自动重试；缓存避免重复调用。
服务不可用或预算耗尽时，按配置返回原流程或暂停。默认配置禁止任何付费请求。

示例请求：

> 使用 cnki-jev，对现有 task.sqlite 中的文献按原筛选标准做辅助初筛。
> 使用我配置好的本地费用上限和题名/摘要发送许可；排除和疑难项交回复核，
> 保留原文证据和最终判断记录。

[完整配置、执行命令与证据回写说明](skills/cnki-jev/references/usage.md)。
本版通过模拟响应验证程序行为，尚未完成真实 Jev 付费接口验收或中文文献准确率评测；
不承诺接入后必然更快或更准。

## 文献表格与任务续跑

直接对 AI 说：

> 使用 cnki-researcher，检索“数字化转型与企业创新”，对前20篇结果按中国企业、
> 实证研究、创新产出三个条件生成文献筛选表。对其中能读到全文的5篇生成实证
> 研究对照表，附变量测量、识别策略、机制检验及原文页码。保存任务以便续跑。

中断后说：

> 使用 cnki-resume，继续这个 task.sqlite 中尚未完成的工作，复用已验证的文件。

输出一个 Excel 工作簿，含 **文献筛选表、实证研究对照表、原文证据、任务进度、
检索与筛选规则** 五个工作表，附 CSV 和审计快照。只读到摘要的会明确标识；
缺失字段保留“未提取/证据不足”；排除记录不删除。SQLite 台账保存逐篇进度，
恢复时核验文件是否仍存在且内容未变。运行中的下载先检查，不直接重启。

所有判断由 AI 根据实际读取的材料完成；离线程序验证字段与状态、生成文件，
不会自行抓取知网，也不能代替原文证据核对。真实网站仍需要可用的授权浏览器。

[字段与命令说明](skills/cnki-resume/references/schema.md)。可先运行合成演示：

```sh
python3 scripts/demo_workflow.py --output /tmp/cnki-demo
```

演示会生成三篇**合成**文献的筛选/实证工作簿和可续跑台账，不访问知网。

## 使用

Codex 中显式引用 `$cnki-researcher` 或对应操作技能；Claude Code 中调用
`/cnki-researcher`，也可请求使用 cnki-researcher agent；WorkBuddy 中直接点名
技能使用，例如「使用 cnki-search 检索……」。

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

## 关注我

<p align="center">
  <img src="assets/wechat-channel-qrcode.png" alt="扫一扫二维码，关注我的视频号" width="280">
  <br>
  <sub>扫一扫二维码，关注我的视频号</sub>
</p>
