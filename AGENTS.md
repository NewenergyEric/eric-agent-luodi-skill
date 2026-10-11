# 项目约定

先读 README.md 和 .agents/skills/client-setup/SKILL.md。本机若有 DELIVERY.md 或 OPEN_SOURCE_PREP.md，再读作私有接续记录；公共制品不包含它们。
用户入口仅 configure / check / update；执行仍只支持 Windows、本项目沙箱和合成示例包。--brief 增加 Windows/Mac、本机/另一台的只读引导，不等于支持安装。保留 FDE 定位、蓝色叙事与既有媒体；亲民粉色产品是独立项目。
不读取或复制既有凭据、订阅、cookie、聊天或客户数据；凭据仅引用。
不连接客户机器、全局安装、启停 Agent、改代理/TUN/防火墙/SSH或部署客户目标。本轮已明确授权建立并推送经审核的私有开发仓库；公开开源发布仍须先确定许可证与版权，不代选法律授权。
公共包经源码审核后显式更新 recipe 和 sources.lock.json，禁止运行时自动重新 pin。
客户覆盖只合并用户明确更改的键，不用公共模板重写整个文件。
使用 Python 标准库。修改后运行 `python -B -m unittest discover -s tests -v`；发布准备运行 `python -B tools/release.py check`。
demo.py 只在独立 .demo-runs 中创建合成实例。状态在 .control/latest 和 .control/pending；先 check 再接续，Agent 加载未验证就如实保留。
公开文件必须逐项列入 release-files.json 并审阅；不包含客户、日志、回执、备份。许可证由作者决定。

交付默认包含用户价值、docs/getting-started.html、docs/installation-checklist.md 和当前可用版的隔离安装验证。未接入能力保留未完成状态。
