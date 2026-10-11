# 配置、检查、更新和恢复

## 一次配置的全过程

| 步骤 | 实际代码与行为 | 解决的问题 |
|---|---|---|
| 整理需求 | Skill 将自然语言转成客户/实例代号、版本和允许的覆盖字段 | Codex 理解自然语言；Python 不需要模型服务 |
| 环境/归属 | probe 读取 Python、主机指纹、PATH/EXE 元数据；guard_identity 核对实例 | 避免误用另一客户或机器的目录 |
| 可信输入 | package 校验配方/文件 hash；desired 合成分层设置 | 固定来源，不把公共模板与定制混在一起 |
| 差异计划 | build_plan 检查漂移，列出 add/replace/keep、前后 hash、设置前后值 | 写实例前知道改什么 |
| 具体确认 | preview 保存计划；apply 重算并核对 --approve | 输入/身份变化后旧确认失效 |
| 执行 | Windows 文件锁、快照、pending 日志、逐文件原子替换 | 避免重复写入，给中断留下恢复依据 |
| 验收 | acceptance 核对文件，以隔离 Python 子进程运行合成订单任务 | 不把文件存在或一句回复当作生效 |
| 接续 | save_receipt 记录结果与 continue 命令 | 下一段对话可从本地事实继续 |

目标固定为 `sandboxes/<customer>/<instance>`，不接受任意安装路径或远程地址。代号限小写字母开头、数字/短横线，最长 32 位。

## 三层设置

| 层 | 位置 | 规则 |
|---|---|---|
| 公共包 | packages、recipes、sources.lock.json | 只允许 1.0.0/1.1.0 的明确文件，来源 bundled://safe-order-summary；不下载 |
| 客户覆盖 | customers/<customer>/overrides.json | 可以缺省；脚本读取但不重写。新客户参考 examples，不覆盖已有文件 |
| 机器差异 | machines/<host_fingerprint>.json | 可以缺省；只设样例超时及可选工具要求，不改系统设置 |

覆盖只允许 currency=CNY/USD/EUR、minimum_total=0–10000 整数，以及最多 8 个 env:大写变量名的 credential_refs。引用不解析为秘密值；回执仅含数量和覆盖文件 hash。未知字段被拒绝。

机器设置为 task_timeout_seconds（1–60，默认 10）、optional_tools（空或仅 clash）。当前 probe 固定检查 Codex/OpenClaw/Hermes/Clash 的 PATH/EXE 元数据；optional_tools 不触发安装。找不到或版本未知时如实报告，不执行推测命令。

## 首次配置

```powershell
python client_setup.py check --customer sample --instance local
python client_setup.py configure --customer sample --instance local
```

新实例 check 返回 not_installed、退出码 2，属于待配置状态。configure 返回 confirmation_required、退出码 0，在 .control 写计划/锁文件，但不在目标实例安装 Skill。

审核 identity（客户、实例、主机指纹、目标目录）、version、files、settings_before/settings、release_change。文件差异是状态/hash 比较，不是全文 diff。确认后执行：

```powershell
python client_setup.py configure --customer sample --instance local --approve "替换为已确认的完整plan_id"
```

原批准命令重跑会验证已完成结果，返回 replayed=true，不重写相同文件，但仍执行本地样例验收。--approve 表示操作确认，不是账户认证或数字签名。

## 检查与更新

check 核对受管文件；输入变化返回 configuration_update_available，受管文件偏离状态 hash 则拒绝。健康状态会实际运行只读样例脚本，不生成新回执。

`update --version 1.1.0` 新增最大合格订单结果，保留客户覆盖。审核新 plan_id 后再加 --approve。只改覆盖/机器设置时可用 `update --version 1.0.0` 指定当前版本。configure 不跨版本覆盖。

## 中断、接续和取消

写入前保存 `.control/pending/<customer>--<instance>.json`，快照在 `.control/objects`。Windows 锁由进程持有，进程退出即释放。异常后先 check，使用它给出的原 action/version/plan_id。

例如原 action=update、version=1.1.0：

```powershell
python client_setup.py update --customer sample --version 1.1.0 --approve "原plan_id" --recover resume
```

resume 只接受当前文件仍为事务原始 hash 或目标 hash，并重新核对包、覆盖和机器输入。第三种内容表示漂移，保留现场停止。

需要取消该 pending 时，先审核恢复范围，再执行：

```powershell
python client_setup.py update --customer sample --version 1.1.0 --approve "原plan_id" --recover rollback
```

rollback 恢复本次待完成事务的原字节，删除其新增受管文件，只尝试删除空的受管父目录；不递归删除客户目录，不提供任意历史回滚。

## 验收必须分开报告

| 字段 | 含义 |
|---|---|
| installation=passed | 文件符合配方/状态 hash |
| loading.local_harness=passed | 验收器读取 Skill 契约，脚本运行成功 |
| loading.agent_runtime=not_verified | 尚无 Codex/OpenClaw/Hermes 实际加载的独立证据 |
| business.status=passed | 随包三条合成订单与预期一致，不涵盖客户业务 |

Python 子进程用 -I -S -B，仅传递系统目录环境变量，不继承凭据；超时、退出码、输出 schema 或结果不符都阻止完成状态。

成功回执为 `.control/latest/<customer>--<instance>.json`，包含 continue 命令。真实回执也含本地路径、主机指纹、客户代号和时间，必须留在本地。公共示例见 [匿名回执](../examples/receipt.example.json)，它不能作为恢复状态使用。

## 失败处理与实际边界

| 错误 | 处理 |
|---|---|
| plan_changed_reconfirm | 重建并审核计划 |
| managed_file_drift / recovery_drift | 保留现场，核对修改；不强制覆盖 |
| instance_identity_mismatch | 核对客户/目录/主机，不跨实例复制状态 |
| unowned_target_not_empty | 换新实例代号，不接管陌生目录 |
| recipe_hash_mismatch / payload_hash_mismatch | 核对来源，不能重算 hash 绕过 |
| recovery_inputs_changed | 恢复原输入后接续，或 rollback |
| instance_busy | 等该实例现有操作结束 |

退出码：0=生成计划/完成，2=待处理或边界拒绝，1=本地异常；参数语法错误也返回 2。

本版管理 5 个包/配置文件和 identity/state，拒绝越界、ADS、保留名、链接、junction、hardlink。hash 保护完整性，信任根是代码与锁文件；不抵抗有权限同时改它们的攻击者。主机名指纹不是硬件证明；逐文件原子替换不是整目录断电事务；文件锁不防其他恶意进程竞态改写。

32 项初版测试及 demo 证明的是这条 Windows 本地闭环。真实运行器、远程机器、全局安装、代理/SSH 修改、Agent 启停和真实客户业务都未实现，需要后续具体设计与授权。
