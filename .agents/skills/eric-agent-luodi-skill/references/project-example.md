# Windows 项目内示例

仅在用户明确要运行完整仓库中的合成配置示例时阅读本页。Skill 安装目录不包含运行器；先确认用户指定的项目根目录同时存在 client_setup.py 和 sources.lock.json，不猜目录，不下载或连接目标。

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
