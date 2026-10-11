# Client Setup · Agent 电脑安装清单

[交互清单](getting-started.html) · [当前示例验证记录](installation-verification.json)

给 FDE：按步骤交付、保留客户定制，下一次能继续维护。

本轮交付完整路线与选择项，保留当前执行范围；真实系统安装与网络修改仍未接入。手动勾选不代表自动验收。默认 OpenClaw，可选 Hermes 或用户指定的 Agent。

## 先选择

- 电脑：Windows / Mac；就在这台 / 另一台。
- 网络：复用可用通路或直连 / Clash Verge Rev / 用户指定工具。
- 准备工具：Codex / VS Code + Agent 扩展 / Cursor / 现有工具。
- 日常 Agent：OpenClaw（默认）/ Hermes / 用户指定。
- Skills：第一件任务所需 / 用户审核清单 / 检查现有 Skills。

选择改变后重新核对完成项。另一台电脑先由当地执行器检查，不自动建立连接。只准备实际需要的依赖，不把所有选项一起安装。

## 1. 依赖环境

- [ ] 核对目标系统、架构、执行位置与现有 Git、Node.js、Python 等版本。
- [ ] 按选定 Agent 发行版的官方要求补齐依赖，记录版本；原生系统或 WSL2 由实际支持和用户选择决定。
- [ ] 在实际执行环境验证所需工具可运行。当前项目示例要求 Python 3.12+，只使用标准库。

来源：[OpenClaw 安装要求](https://docs.openclaw.ai/install)、[Hermes 安装说明](https://hermes-agent.nousresearch.com/docs)。

## 2. Clash 等网络通路

- [ ] 已有网络可用则复用；需要安装时选择维护者发行版与适合的架构。
- [ ] 用户在自己的客户端配置订阅或登录。本清单、项目与聊天均不接收秘密值。
- [ ] 分别验证安装工具及 Agent 所需端点可达；仅浏览器能访问不等于运行器通路已好。

来源：[Clash Verge Rev 维护者下载](https://github.com/clash-verge-rev/clash-verge-rev/releases)、[维护者文档](https://www.clashverge.dev/)。本轮不改系统代理、TUN、防火墙或 SSH。

## 3. Codex / IDE

- [ ] 安装或复用所选工具；由用户完成登录，从正确仓库下载/克隆项目后打开根目录。
- [ ] 读取 `.agents/skills/client-setup/SKILL.md`；核对文件权限与实际工作目录。
- [ ] 完成一个不含私人数据的小任务，确认准备工具可用。

入口：[Codex 官方开始说明](https://developers.openai.com/codex/quickstart)。VS Code / Cursor 从其各自官方站点选择系统对应安装包；选择 IDE 时另外确认所需 Agent 扩展，IDE 本身不等于 Agent 已配置。

## 4. 安装日常 Agent

- [ ] 默认 OpenClaw，或使用明确选定的 Hermes / 其他 Agent，记录官方来源与发行版本。
- [ ] 确定安装位置、工作目录、模型和账号路径；凭据仅在目标工具中配置，项目只记录引用或状态。
- [ ] 实际核对版本与运行状态，完成最小任务。安装文件存在不算可用。

本轮没有调用任何真实 Agent 安装器；官方上游支持某系统，也不表示本项目已有对应执行适配。

## 5. 行为约束文件

- [ ] 审阅 [AGENTS 模板](../examples/behavior/AGENTS.template.md)，按所选运行器实际支持的规则入口适配。
- [ ] 先看原配置差异，仅合并明确选择的工作规则；不覆盖现有有效设置。
- [ ] 分别规定工作流程、工具范围、确认边界、来源/版本、验收、失败恢复和接续。
- [ ] 排除 SOUL、USER、记忆、聊天、个人档案和任何秘密值。
- [ ] 配置实际工具权限与审批，验证规则被加载并通过行为检查；仅有 Markdown 不能证明权限被限制。

见[行为基线与验证方法](behavior-baseline.md)。参考 Cici Foundry 的配置分层方法，不复制它的用户 Profile 或实例数据。

## 6. Skills

- [ ] 先确定第一件真实任务，只选择必要且审核过的 Skills。
- [ ] 核对来源、版本、许可、依赖及工具权限，再按选定 Agent 的加载规则安装。
- [ ] 确认实际发现并调用 Skill，完成相应任务；更新时保留用户覆盖。

当前已支持的 Windows 项目示例：先 check，configure/update 生成差异，审核完整 plan_id 后批准；详见 [工作流](workflow.md)。真实 Agent 的 Skill 安装和加载尚未接入。

## 7. 验收与接续

- [ ] 分别记录文件安装、规则/Skill 实际加载、真实任务结果，附可检查证据。
- [ ] 未验证项明确保留，不用示例成功代替真实用户任务成功。
- [ ] 本地保存版本、回执、未完成项和下一条 check；下次核对目标身份后继续。

## 当前可用版怎样验证

已有 Windows + Python 3.12+，从正确项目根目录，经授权执行 `python -B demo.py`。每次使用新的隔离实例，验证安装 1.0.0、重复执行、升级 1.1.0、覆盖保留及中断恢复。

当前结果：installation=passed，local_harness=passed，agent_runtime=not_verified；仅合成订单 2 笔、CNY 47.50、最大单笔 27.50。完整证据见[独立副本验证](installation-verification.json)。

## 交给 Agent 的话

> 读取本项目 Skill 和安装清单。按我选择的方案逐项检查：依赖环境、网络通路、Codex/IDE、日常 Agent、行为约束文件、Skills 与验收。默认 OpenClaw，保留现有设置；不导入 SOUL、USER 或任何私人资料。只执行当前支持且获授权的步骤，逐项留下证据、待办和下一步，不把勾选当作安装成功。

官方入口核对日期：2026-10-11。实际安装前按选定发行版本重新核对要求；本清单未将实时 latest 固定成项目的可执行配方。
