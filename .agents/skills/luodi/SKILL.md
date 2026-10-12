---
name: luodi
description: 在本 Windows 项目内为新客户配置、检查或更新隔离的安全示例 Skill。适用于 FDE 快速配置演示、差异确认、故障恢复和交付接续；尚不支持客户机器或 OpenClaw/Hermes 部署。
---

# 落地 · luodi

面向 FDE 的 Windows / Mac 客户准备流程、验收与持续维护。先把目标与证据对齐，再在当前支持范围内执行。参考搭好已验证的顺序时，仅借鉴文档中的通用做法；不得继承别的目标授权或把 Windows 结果视为 Mac 实测。

先确认目标是 Windows 还是 Mac、当前执行器是否就在目标电脑；用户未提供时只问缺失项。本机无需 SSH，另一台电脑先核实并复用明确授权的连接，没有接入就停在引导。读项目根目录的 docs/computer-guide.md 与 docs/support-matrix.md；用三个原有入口的 `--brief examples/computer-local.json`（或 computer-mac.json / computer-other.json）生成只读分流。该计划不安装、不连接、不能用 --approve 执行。Windows / Mac 均提供七步流程支持。Windows 核对实际运行方式；Mac 核对 macOS、Apple 芯片或 Intel、终端与目录权限。Mac 执行仍未在本项目实测；真实 Agent 部署依旧未接入。只有 Windows 本机示例需求才继续下面的可执行循环。

首次 check 若返回 not_installed，不据此宣称完整身份已核验；在 configure 预览中核对 host、target、customer、instance 后才确认。

将用户需求映射到三个入口：配置 `configure`、检查 `check`、更新 `update`。
以包含 client_setup.py 与 sources.lock.json 的项目根目录为工作目录，先读 README。本机若有 DELIVERY.md 或 OPEN_SOURCE_PREP.md，再读作私有接续记录。文件标签页不等于任务已绑定项目，先核对实际工作目录。

1. 确定客户代号和实例代号（小写字母、数字、短横线，最长 32 位）。缺失时询问，不复用其他客户实例。
2. 运行 `python client_setup.py check --customer <id> --instance <id>`，核对主机指纹、目标目录和实例归属。
3. 将客户设置留在 `customers/<id>/overrides.json`，只允许 currency、minimum_total、credential_refs；仅合并用户明确更改的键，不用公共模板覆盖已有设置。新客户可参考 examples。凭据只写 `env:变量名`，不读取值。机器差异另放 `machines/<主机指纹>.json`，只允许 task_timeout_seconds 和 optional_tools（只能为 clash）。不拷贝既有上下文。
4. 运行 `python client_setup.py configure --customer <id> --instance <id>`；更新用 `update --version 1.1.0`。展示 plan_id、目标身份、add/replace/keep、前后 hash 和设置差异。取得用户对具体计划的确认，再给原命令加 `--approve <plan_id>`。仅在用户明确授权自动化隔离测试/演示时自行确认该次合成计划，不把历史授权套给新客户。
5. 若收到 recovery_required，读 `check` 给出的 action/version/plan_id；以原参数加 `--approve <plan_id> --recover resume` 接续。需要恢复旧版时先说明将恢复哪些文件，再用 `--recover rollback`。发生漂移、身份变化或计划变化就停止，展示代码和原因，重新规划；不强制覆盖。
6. 分别报告 installation、loading.local_harness、loading.agent_runtime 和 business。`agent_runtime=not_verified` 必须如实保留。业务结果只涵盖随包合成订单，不能宣称客户业务或运行器部署成功。
7. 交付 `.control/latest/<客户>--<实例>.json` 回执与下一条 check 命令，下一段对话先读它。

只管理 `sandboxes/<客户>/<实例>` 内明确列出的 5 个包/配置文件和 2 个状态文件。来源与版本固定在 sources.lock.json；不要为绕过错误改 hash。详细步骤见 docs/workflow.md。客户目录、计划、回执不得发布；开源准备仅使用 release-files.json 和 tools/release.py。
不全局安装、不连接客户主机、不启停 Agent、不下载工具、不改代理/TUN/防火墙/SSH、不由运行器创建仓库或部署；维护者的仓库操作另按本次明确授权执行。未知版本只报告待配置。Clash 仅做 PATH/版本元数据探测。

首次上手时主动给出 docs/getting-started.html 和 docs/installation-checklist.md，按清单逐项报告证据与未完成项。当前版本安装验证用新建隔离示例，用户授权后可运行 demo.py；不得把项目示例通过扩展为真实 Agent 已安装。交付或发布材料沿用此清单，执行能力仍以上述范围为准。

安装清单按用户最新选择依次组织：依赖环境 → Clash 等网络通路 → Codex/IDE → 日常 Agent（默认 OpenClaw，可选 Hermes 或用户指定）→ 行为约束文件 → Skills → 验收与接续。清单默认沿用现有环境，只显示选择项与完成条件；本轮不扩展真实安装。行为规则参考 docs/behavior-baseline.md 与 examples/behavior/AGENTS.template.md，不导入 SOUL、USER 或私人资料。
