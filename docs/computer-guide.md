# 电脑准备引导

用户入口只保留配置、检查、更新。先判断需求与目标，按缺口给出下一步；不要把用户变成安装工程师。

## 先选系统与执行位置

只追问当前缺失的决定：给谁用、第一件要做成的事、Windows 还是 Mac、当前执行器是否就在目标电脑上。系统不清楚时让用户查看“设置 → 系统 → 关于”（Windows）或“关于本机”（Mac），不能从聊天所在设备推断目标设备。

本地执行器已在目标电脑：确认主机身份、工作目录、实例归属、可写目录与权限；无需额外启用 SSH。另一台电脑：先核实系统及用户已授权的连接，优先复用已有会话。没有接入时可引导用户在目标电脑打开项目/执行器；需要 SSH、远程桌面或新的安全设置时，说明具体动作与影响，等待该目标的具体授权。不要读取现有密钥、订阅、cookie 或聊天上下文来“自动接入”。

## 系统准备与验收

两种系统沿用同一张七步清单，逐项确认依赖、网络通路、Codex/IDE、日常 Agent、行为规则、Skills 与任务结果。这里只提供流程支持，不自动安装或修改系统。

| 先核对什么 | Windows | Mac |
|---|---|---|
| 目标电脑 | 系统版本、架构、当前账户与实际工作目录 | macOS 版本、Apple 芯片或 Intel、当前账户与实际工作目录 |
| 执行环境 | 确认选定 Agent 使用原生 Windows 还是其他受支持环境，不擅自启用 WSL2 | 确认终端、所需工具版本、安装位置与目录权限，不默认要求管理员权限 |
| 已有工具 | 保留能用的 Python、Node、IDE 与 Agent，只补计划中确认的缺口 | 同样先复用；下载与架构要匹配，已有包管理器能用才考虑沿用 |
| 通路与登录 | 由用户在目标客户端完成，清单只保存选择和勾选 | 同样不接收订阅、token、cookie 或账号凭据 |
| 第一项任务 | 在实际运行器中观察结果，再验证规则与 Skill 是否加载 | 采用同样的验收方法；Mac 实机当前仍待验证 |

执行器就在目标电脑时直接检查，无需另开 SSH。执行器在另一台电脑时，先核实目标与已有具体授权；没有接入就让目标用户在本机继续检查。该介绍不新增远程连接或系统设置权限。

## SSH 与 Mac 尝试入口

SSH 连接工具在独立的 [dahao Skill](https://github.com/NewenergyEric/dahao/tree/main/.agents/skills/dahao) 中，随 Skill 安装提供。本仓库不捆绑该工具，也不通过 `--brief` 建立远程连接。

| 场景 | 入口 |
|---|---|
| 另一台 Windows | 搭好的双击连接小助手：`assets/windows-connect/` 源码与 `scripts/build_windows_connect.py` 构建脚本 |
| 另一台 Mac | 系统“远程登录”，按搭好的 [Windows / Mac 连接清单](https://github.com/NewenergyEric/dahao/blob/main/.agents/skills/dahao/references/connection-checklist.md#b-目标是-mac)推进 |
| 控制端发现目标 | 搭好的 `scripts/discover_target.py`：读取已有候选；确认后仅检查选定目标的 SSH 标识 |
| 已在目标本机 | 使用本机 Agent，直接核对系统、账户与工作目录 |

Mac 尝试时先安装搭好 Skill，在对话中说明“另一台 Mac，默认 OpenClaw”。确认目标和具体权限后，依次核对远程登录、主机公钥指纹、账户与系统身份，再推进依赖、工具、规则、Skills 和首项任务。Windows 双击程序不用于 Mac。密码与私钥留在用户设备，地址和账户只进入私有接续记录。

## 借鉴搭好的范围

独立项目「搭好」的[脱敏 Windows 实测记录](https://github.com/NewenergyEric/dahao/blob/46f764d85209544f291dd4c24b0cccfcd13f9659/docs/live-connection-verification.json)记录了目标确认、临时授权、SSH 接入、复用既有 OpenClaw 完成合成小任务和撤销访问。落地借鉴这个先确认、再验证、最后交接的顺序，不复制真实目标资料或凭据。

该记录针对 Windows 与已有运行器，不是 Mac 实测，也不是全新安装证明。落地的执行器和权限边界维持原状；Windows 示例通过和 Mac 流程支持分别报告，不能把其他项目的结果写成本项目已完成的安装。

## 可执行的只读分流

Agent 将已确认的选择写为项目内简报，再调用原有三个入口之一：

```powershell
python -B client_setup.py configure --customer sample --brief examples/computer-local.json
python -B client_setup.py check --customer sample --brief examples/computer-mac.json
python -B client_setup.py update --customer sample --brief examples/computer-other.json
```

`--brief` 仅生成引导计划，不实例化配置引擎、不探测远端、不写目标。可接受 Windows/Mac 分支不等于已在两个系统验证安装。返回 `guidance_only`、`deployment_ready=false`，阻塞项明确列出未实现部分；不能给这个计划加 `--approve` 来执行整机安装。

简报只允许 schema、target(location/os/access)、agent 和 first_task 这些固定字段，不保存主机地址、口令、任意命令或自由文本。原始需求可以留在用户对话中；后续交付摘要不应包含秘密。示例只是合成输入，不能当成实际设备证明。

## 从计划到真实可用

1. **环境与依赖：** 识别 OS、架构、权限、已有版本和磁盘/目录条件。当前脚本仅验证 Windows 沙箱与版本元数据；Python/Node/系统包安装配方尚未实现。没有 Python 的空机不能直接跑本工具，先由现有 Agent 引导准备执行环境。
2. **网络：** 确定所选运行器及模型需要的官方端点后，再设计 DNS/TLS/下载可达性检查。当前没有真实网络诊断适配。Clash 仅可选版本探测，不读订阅、不设置代理或 TUN。
3. **Agent：** 先选运行器和明确版本，再查官方安装文档、固定来源与 hash。当前没有 Codex/OpenClaw/Hermes 的安装适配，未知版本不拼命令。凭据仅引用，不求用户在对话里粘贴值。
4. **Skills：** 已实现示例包的公共版本、用户覆盖、机器差异分层。先展示目标身份、文件差异和恢复方式；具体计划获得确认后执行。真实运行器的安装目录与加载协议必须单独适配。
5. **验收：** 安装检查文件和版本；加载检查运行器实际识别并使用 Skill 的证据；业务检查用户真实任务的可观察结果。回复了“完成”或本地 Python 脚本成功都不能代替加载验证。
6. **接续：** 交付记录含实例身份、来源/version/hash、已做动作、覆盖差异、三层验收、未完成项及下一条检查命令。当前示例回执已实现，真实运行器回执仍需适配。新对话先 check 再修改。

## 当前执行边界

Windows、本机、项目沙箱示例明确选中时，使用[已有配置与恢复流程](workflow.md)。Mac 或真实运行器需求停在可检查计划与缺口上，不运行示例后宣称整机完成。示例首次 `check` 的 `not_installed` 尚不带完整实例身份；完整身份在 `configure` 预览里，必须在批准前核对。

出现漂移、错误 hash、跨实例或越界路径时停止，不能重新 pin 或强制覆盖。中断时读取原计划，resume/rollback 都仍在原配置或更新入口下。当前不连接其他电脑，不建立持久访问，不启动/停止已有 Agent，不改全局 Skill、代理、SSH、防火墙或安全设置。
