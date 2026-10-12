# 发布与隐私

三个用户业务入口不变。维护者运行：

```powershell
python -B -m unittest discover -s tests -v
python -B tools/release.py check
python -B tools/release.py build
```

check 读取 release-files.json 明确列出的文件；build 将同一份已检查字节生成确定性 ZIP，不连接 GitHub。没有通配符打包。运行器的包与 recipe hash 保持原值。

## 公开范围

文字源码、文档、合成样例、测试、CI 和可编辑视频工程逐项列在 release-files.json。媒体仅允许两个语言的指定 MP4/GIF/WebP/PNG、两张案例板，以及一个 OFL 字体子集；每个二进制必须匹配 showcase-files.json 中的字节数/hash，并通过类型头检查。单个二进制不超过 8 MiB，总包不超过 64 MiB。

文本扫描不等于图片或视频内容检查。媒体由本次原创合成素材生成，另外执行完整解码和可见内容检查。字体许可、模板许可、Node 依赖锁与重建说明随包保留。node_modules、原始渲染 out、浏览器数据均不纳入。

## 私有数据

customers、machines、sandboxes、.control、.demo-runs、.test-runs、validation、.private、.release 及 DELIVERY、OPEN_SOURCE_PREP、DEMO-LATEST 保留本机，不删除、不改写恢复数据。配置值只使用合成公开样例。docs/evidence.json 是单独生成的字段投影，不是复制实际回执后仅删除姓名。

检查拒绝私有目录、密钥/凭据文件、路径越界、链接、重复路径、额外 ZIP 成员和未经列出的媒体。扫描常见 token、私钥头、订阅链接、认证 URL、邮箱、内网 IPv4、本机用户名/主机标识和绝对路径。发现时只显示文件/行/规则，不回显匹配值。

扫描无法认识所有格式与私人信息；仍需逐项审阅文件、图片、视频与 Git 历史。

## Git 与授权

初始化前先检查既有仓库/remote。只暂存白名单，逐项对比索引字节与已审核文件，检查不存在私有路径后提交。不要把未经审查的工作目录历史推送到公开仓库。.gitignore 不会删除已经被跟踪的数据。

有历史时 release.py 将 git_history_review_required 列为人工审查项；不因此自动删历史或重写提交。首次公开前对提交树的文件清单、blob 哈希和消息单独审核，记录确切提交。

license_status 与 upstream_review 表示当前授权/来源核对状态。作者已确认原创内容授权并选择 Apache-2.0；第三方材料保留原许可。公开前还要检查远端所有分支、标签、提交元数据、GitHub 发行资产与 CI 日志。只有当前提交与审查字节一致且获作者授权，才改变仓库可见性。

更多来源与各自许可见 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。

## 默认交付

每次当前版本交付附用户价值说明、HTML 使用流程、可勾选安装清单和独立导出副本的安装验证，分别记录安装、本地加载、真实 Agent 加载与业务范围。入口为 getting-started.html、installation-checklist.md 与 installation-verification.json。只更新证据中实际复测的内容；未实现的安装步骤保留待办。

私有或公开仓库都只提交 release-files.json 列出的已审字节。每次发布检查完整暂存树、文件 hash、提交身份与消息，保留本地审阅记录。离线工具保留 git_history_review_required 人工关口；独立审查记录将该关口与确切提交绑定，不通过修改工具或删除历史来绕过。
