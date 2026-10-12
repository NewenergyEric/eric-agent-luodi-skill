# 落地 · luodi

**Windows / Mac，把客户需要的 AI 一步步落地。**

[English](README.en.md) · 面向 FDE 的 Agent 配置与交付 Skill

[打开安装清单](docs/getting-started.html) · [文字 checklist](docs/installation-checklist.md) · [24 秒介绍](docs/watch.html)

从电脑准备到第一项工作，落地把交付拆成一张清单：先选系统与工具，复用已有环境，再规划 Agent、行为规则和 Skills。每一步写清要做什么、如何验收，客户的选择单独保留，下一次更新接着做。

Windows 和 Mac 使用同一条路线：**依赖环境 → 网络通路 → Codex / IDE → 日常 Agent → 行为规则 → Skills → 任务与交接**。默认 OpenClaw，也可选择 Hermes 或客户指定的 Agent。

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/readme/hero-zh.png">
  <img src="assets/readme/hero-zh.gif" width="100%" alt="落地的 Windows / Mac 交付流程：选择目标、检查环境、规划配置、完成第一项工作、分层验收并保留客户定制。">
</picture>

[本地播放器](docs/watch.html) · [中文 MP4](assets/readme/hero-zh.mp4?raw=true) · [GIF](assets/readme/hero-zh.gif?raw=true) · [轻量 WebP](assets/readme/hero-zh.webp?raw=true) · [影片文字稿](docs/demo.md)

短片用原创会议纪要示例讲解交付流程。下载 HTML 后用浏览器打开，即可选择方案、保存人工勾选进度、复制清单或打印。

## 从客户的一句话开始

在 Codex 中打开项目，使用 [`$luodi` Skill](.agents/skills/luodi/SKILL.md)：

> $luodi 帮我为客户准备一台 Mac，默认 OpenClaw。先确认执行位置和已有工具，按清单检查依赖、网络、行为规则与 Skills。第一项工作是把会议纪要整理成带负责人和期限的行动清单。先给出具体计划与影响，再按授权推进，留下交接记录。

| 先决定 | 怎样准备 |
|---|---|
| Windows / Mac | Windows 核对系统与实际运行方式；Mac 核对 macOS、Apple 芯片或 Intel、终端与目录权限 |
| 本机 / 另一台 | 已在目标电脑就直接检查；跨电脑先确认目标与接入方式 |
| 网络与准备工具 | 复用已有通路；Clash、Codex、IDE 按实际需要选择 |
| 日常 Agent 与 Skills | 先选 Agent，再选第一件任务所需的少量 Skills |
| 行为规则 | 审阅 AGENTS.md 等规则的差异，只合并客户选择的部分 |

`--brief` 生成只读准备计划，便于审阅与继续开发。它不执行系统安装或远程连接；各执行入口的范围见[支持矩阵](docs/support-matrix.md)。

```powershell
python -B client_setup.py configure --customer sample --brief examples/computer-mac.json
```

Windows 路线使用 `examples/computer-local.json`。[分系统准备说明](docs/computer-guide.md#系统准备与验收)

## 要帮另一台电脑：SSH 小工具在搭好

连接工具随独立的 [`dahao` Skill](https://github.com/NewenergyEric/dahao/tree/main/.agents/skills/dahao) 一起提供；本仓库的 `luodi` 负责交付清单与配置包流程。

- **Windows：** 使用搭好的双击连接小助手，核对目标电脑并交接必要信息。
- **Mac：** 使用系统“远程登录”，按[搭好的连接清单](https://github.com/NewenergyEric/dahao/blob/main/.agents/skills/dahao/references/connection-checklist.md#b-目标是-mac)核对账户、主机指纹与目标身份。
- **已经在目标电脑：** 直接走本机路线，无需额外开启 SSH。

在帮助者的 Codex 中安装搭好 Skill 后，可以说：

> $dahao 帮我给同 Wi-Fi 下的另一台 Mac 准备 AI 助手，默认 OpenClaw。先带我确认目标和远程登录，核对主机指纹，再检查环境。先复用已有工具，按具体授权推进安装、配置、任务验收与交接。

这会进入搭好的连接工作流；目标地址、账户与接入资料只留在本次私有记录中。

## 用一件具体工作验收

以[会议纪要](examples/first-task/meeting-notes.md)整理成[行动清单](examples/first-task/action-list.md)为例，检查输出是否包含行动、负责人、期限，以及需要补充的信息。

- **安装：** 核对文件与版本。
- **加载：** 检查运行器实际识别并使用规则与 Skill。
- **业务：** 查看任务成果是否符合客户要求。

![交付检查：环境、运行器、规则、第一项任务与客户配置](assets/readme/case-board-zh.png)

## 先运行项目内示例

在 Windows + Python 3.12+ 中运行，无需额外 Python 依赖：

```powershell
python -B demo.py
```

示例在独立目录演练配置包安装、重复执行、升级、覆盖保留和中断恢复，并生成分层回执。[示例流程](docs/workflow.md) · [执行记录](docs/installation-verification.json)

## 配置、检查、更新

| 需求 | 项目内示例入口 | 输出 |
|---|---|---|
| 配置 | `python client_setup.py configure --customer sample` | 绑定实例身份的文件差异计划 |
| 检查 | `python client_setup.py check --customer sample` | 当前差异、操作记录与验收状态 |
| 更新 | `python client_setup.py update --customer sample --version 1.1.0` | 保留客户覆盖的新版本差异 |

审阅具体计划后，给原配置或更新命令加 `--approve` 与完整 `plan_id`。公共模板、客户覆盖和机器差异分开保存，只管理明确列出的文件。下一段对话从 `.control/latest` 回执和 `check` 开始。

## 继续开发与贡献

可从一个具体系统、一种 Agent 和一项任务继续扩展适配。执行范围、实现缺口与测试记录集中在[支持矩阵](docs/support-matrix.md)和[验证文档](docs/validation.md)，便于复现与接续。

```powershell
python -B -m unittest discover -s tests -v
python -B tools/release.py check
```

[Skill 使用记录](docs/skill-usage.md) · [视频重建](motion/README.md) · [发布与隐私规则](docs/publishing.md) · [来源与许可](THIRD_PARTY_NOTICES.md)

蓝色 FDE 版本独立维护。公开发布与许可安排以作者公告及许可文件为准。
