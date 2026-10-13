# 项目约定

先读 README.md 和 .agents/skills/eric-agent-luodi-skill/SKILL.md。本机若有 DELIVERY.md 或 OPEN_SOURCE_PREP.md，再读作私有接续记录；公共制品不包含它们。
用户入口仅 configure / check / update；执行仍只支持 Windows、本项目沙箱和合成示例包。--brief 增加 Windows/Mac、本机/另一台的只读引导，不等于支持安装。保留 FDE 定位、蓝色叙事与既有媒体。
不读取或复制既有凭据、订阅、cookie、聊天或客户数据；凭据仅引用。
不连接客户机器、全局安装、启停 Agent、改代理/TUN/防火墙/SSH或部署客户目标。本项目原创内容已由作者确认采用 Apache-2.0 并公开；后续发布继续逐项审核来源、版权与敏感资料，变更许可仍由作者决定。
公共包经源码审核后显式更新 recipe 和 sources.lock.json，禁止运行时自动重新 pin。
客户覆盖只合并用户明确更改的键，不用公共模板重写整个文件。
使用 Python 标准库。修改后运行 `python -B -m unittest discover -s tests -v`；发布准备运行 `python -B tools/release.py check`。
demo.py 只在独立 .demo-runs 中创建合成实例。状态在 .control/latest 和 .control/pending；先 check 再接续，Agent 加载未验证就如实保留。
公开文件必须逐项列入 release-files.json 并审阅；不包含客户、日志、回执、备份。许可证由作者决定。

交付默认包含用户价值、docs/getting-started.html、docs/installation-checklist.md 和当前可用版的隔离安装验证。未接入能力保留未完成状态。

产品名为「落地 · luodi」，项目 Skill 为 `$eric-agent-luodi-skill`，面向 FDE 的客户配置、验收与维护。保留蓝色、现有字体与动效。更名不迁移底层 client_setup.py、实例标识或既有状态路径。

Skill 与 GitHub 仓库标识为 `eric-agent-luodi-skill`，中文品牌与既有媒体名称保持不变。使用引导先说明适合谁、安装入口与第一句话，再展开技术细节；按配置 / 检查 / 更新接续，保留真实能力与授权边界。

对外介绍以本产品的用户与交付路径为主线。按作者要求，可链接 FDE 指南/公开仓库与 FDE Tool，说明业务方法、Agent 准备和任务工具怎样衔接；FDE Tool 仅保留作者确认的非公开入口并标注访问权限，不公开私有仓库地址或内容。不加入无关产品推荐、对照或维护关系说明。许可与版权信息集中在 LICENSE 和 THIRD_PARTY_NOTICES.md，产品正文不追加授权宣言。
