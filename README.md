# 落地 · luodi

**让新电脑里，有一个能干活的 Agent。**

[English](README.en.md) · FDE 本地验证版

[用户价值与 HTML 流程](docs/getting-started.html) · [安装 checklist](docs/installation-checklist.md) · [当前版本独立验证](docs/installation-verification.json)

HTML 下载后用浏览器打开，可保存勾选进度、复制命令和打印。

落地是面向 FDE 的 Agent 电脑配置与交付 Skill。从一台新 Mac 或 Windows 电脑开始，确定客户要用的 Agent，检查环境与依赖，按可审查的计划配置运行器和 Skills，再用第一项具体工作验收。交付后继续添加、更新技能，保留客户的定制，并让下一段对话接着维护。

这是完整交付的产品目标。**当前已验证 Windows 项目内配置包、更新恢复和只读目标分流；Mac 执行、依赖自动安装、真实 Agent 安装与加载尚未接入。**

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/readme/hero-zh.png">
  <img src="assets/readme/hero-zh.gif" width="100%" alt="24秒蓝色流程演示：选择新电脑与Agent、检查环境、规划部署、演示第一项工作、分层验收、保留定制继续更新。未实现的部署步骤明确标注。">
</picture>

[本地播放器](docs/watch.html) · [中文 MP4](assets/readme/hero-zh.mp4?raw=true) · [GIF](assets/readme/hero-zh.gif?raw=true) · [轻量 WebP](assets/readme/hero-zh.webp?raw=true) · [分镜与证据边界](docs/demo.md)

影片展示目标流程和已有验证基础。会议纪要转行动清单是原创合成任务示意，尚未由真实运行器执行；没有把计划或回复包装成部署成功。

## 打开项目，从客户的一句话开始

在 Codex 中打开项目并使用 [`$luodi` Skill](.agents/skills/luodi/SKILL.md)。已有本机执行器时直接检查本机；另一台电脑先核实系统和已授权的接入方式。

> 帮我给客户的新电脑配置 Agent。先确认是 Mac 还是 Windows、这次在哪台电脑执行，再检查环境与依赖。第一项工作是把会议纪要整理成带负责人和截止时间的行动清单。先给我看计划、缺口和影响，确认后再执行；安装、加载和工作结果分别验收。

现在得到的是只读准备计划、已支持范围和明确缺口。选择 Windows 本机示例后，可以继续执行配置包的差异确认、写入、检查、更新与恢复。尚未实现的运行器安装不会被替换成猜测命令。

## 先选系统，再确定执行位置

| 选择 | 当前可做的事 |
|---|---|
| Windows 本机 | 已实测项目内配置包的配置、检查、更新与恢复 |
| Mac | 可生成只读引导计划；执行适配未实现，也未在 Mac 实测 |
| 执行器就在目标电脑 | 使用本地执行器，无需为了配置额外启用 SSH |
| 另一台电脑 | 区分已有授权接入与缺少接入；当前不建立连接、不假定远端已检查 |
| Codex / OpenClaw / Hermes | 本机只读版本探测；真实安装、配置及 Skill 加载仍待接入 |

```powershell
python -B client_setup.py configure --customer sample --brief examples/computer-local.json
```

Mac 分支使用 `examples/computer-mac.json`。`--brief` 在配置、检查、更新三个入口下都只读，不安装依赖或连接目标。[支持矩阵](docs/support-matrix.md)列出每一步的实际状态。

## 第一项工作，要有看得见的成果

部署的终点应是一件客户真正需要做成的事。例如，把会议纪要整理成行动清单，逐项列出负责人、截止时间和待确认信息。

这次影片使用[合成会议纪要](examples/first-task/meeting-notes.md)与[对应行动清单](examples/first-task/action-list.md)说明验收目标。它们是可阅读的示意素材，**不是当前工具通过真实 Agent 生成的执行结果**。

验收分开报告：

- **安装：** 文件与版本是否到位。
- **加载：** 运行器是否实际识别并使用了 Skill。
- **业务：** 这项工作是否产出符合要求的结果。

## 当前已实现的基础，直接跑一次

已有 Windows + Python 3.12+ 时，无需安装 Python 依赖：

```powershell
python -B demo.py
```

独立沙箱验证配置包安装、重复执行、升级差异、客户覆盖保留、中断恢复及回执。它证明配置机制可运行；真实 Agent 加载仍显示 `not_verified`。底层合成测试保留在源码中，不作为产品宣传的业务承诺。

![当前能力与验收边界](assets/readme/case-board-zh.png)

[配置与恢复流程](docs/workflow.md) · [只读分流与测试证据](docs/system-guide-evidence.json)

## 配置、检查、更新，继续用同一套入口

| 用户需求 | 当前示例入口 | 输出 |
|---|---|---|
| 配置 | `python client_setup.py configure --customer sample` | 绑定实例身份的文件差异计划 |
| 检查 | `python client_setup.py check --customer sample` | 漂移、未完成操作与验收状态 |
| 更新 | `python client_setup.py update --customer sample --version 1.1.0` | 保留客户覆盖的新版本差异 |

审核后给原配置/更新命令加 `--approve` 与完整 `plan_id`。目标、输入或文件发生变化时重新规划；中断时按原计划恢复。

公共模板、客户覆盖、机器差异分开保存。只管理明确列出的文件，固定来源、版本与 hash，更新不会用公共模板重写客户所有设置。

下一段对话可以说：

> 读取本项目的 luodi Skill 和该实例的 `.control/latest` 回执。先核对目标并 check，再分别报告安装、加载和业务状态，继续未完成的工作。

## 边界与下一步

当前没有依赖自动安装、网络配置、远程接入、真实 Agent 部署或服务控制；Clash 仅可选版本探测。工具不读取凭据值、代理订阅、cookie、聊天或客户数据，不修改系统代理、TUN、防火墙或 SSH。

下一条实现路径是确定一个目标系统、一个固定版本的 Agent 和一项真实任务，依次接入预检、依赖配方、运行器安装、Skill 加载及业务验收。详细缺口见[电脑准备引导](docs/computer-guide.md)。

<details>
<summary>验证、源码与维护</summary>

```powershell
python -B -m unittest discover -s tests -v
python -B tools/release.py check
```

[能力与媒体验证](docs/validation.md) · [Skill 使用记录](docs/skill-usage.md) · [视频重建](motion/README.md) · [发布与隐私边界](docs/publishing.md) · [来源与许可](THIRD_PARTY_NOTICES.md)

蓝色 FDE 版本独立维护。当前按作者授权交付私有开发仓库；未作公开开源发布，许可证与版权选择待作者确认。

</details>
