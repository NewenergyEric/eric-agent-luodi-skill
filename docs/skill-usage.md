# Windows / Mac 流程介绍更新 · 2026-10-12

用户确认搭好最近实测为 Windows，Mac 先写流程支持。本次沿用 github-product-launch 与 skill-launch-studio，突出双系统准备路线，补充 Mac 芯片、终端和权限检查；文案、七步清单、中文视频、字幕与证据说明同步更新。执行范围仍为 Windows 本项目合成包；Mac 实机及真实 Agent 安装与加载待接入。保留原蓝色、字体与逐帧动效。

以下为历史记录，当前材料以上方范围为准。

---

# 落地 · luodi 更名记录 · 2026-10-12

用户已选定蓝色 FDE 产品名「落地 · luodi」，项目 Skill `$luodi`。本轮沿用 github-product-launch 与 skill-launch-studio 的更名、媒体复核和私有发布流程，只更新品牌及受影响入口，保留蓝色视觉和现有运行范围。价值说明、七步清单、行为模板和隔离验证继续交付；真实 Agent 安装与加载仍未接入。

以下为此前过程记录，旧名称按历史理解。

---

# 本轮实际 Skill 使用：新电脑 → Agent 工作机

- skill-launch-studio：重新读取 copy-and-page.md、visual-direction.md、motion-and-media.md；按其“用户问题 → 操作 → 输出 → 下一步”方法重写主文案，保留蓝色参考，先代表帧后成片。实际使用原 package_media 的编码函数和 check_media 的媒体解析函数；中文单语言范围在 motion/pack_zh.py 中明确。
- skill-productization：重新核对 evidence-contract.md；将整机部署标为 planned，将已通过的本地配置包与只读分流标为 verified。会议纪要/行动清单为 authored illustration，不列作 Agent 执行证据。实际运行 audit_package.py。
- remotion-best-practices：重新读取 local-fonts.md，沿用已读 timing 与按帧运动方法；固定原字体源、检查新文案字形、等待字体加载，再检查代表帧及完整影片。没有 CSS 动画或幻灯片自动切换。

实际执行命令、哈希、渲染和播放记录保存在本机私有修订记录；公开测量与结果见 docs/validation.md。共享 Skills 与 Agent Gift 均未修改。

下方为此前工作记录，保留历史范围。

# 实际 Skill 使用记录

本次没有新造展示流程代替用户既有 Skill，也没有修改这两个复用 Skill。

| Skill | 本次用途 | 实际执行 |
|---|---|---|
| skill-launch-studio / Skill 上市制作人 | GitHub 装修、文案、分镜、MP4/GIF/WebP | 读取全部相关参考；改编 Remotion starter；双语代表帧、成片；原始 package_media.py 和 check_media.py |
| skill-productization / Skill 产品架构师 | 已实现能力、案例与限制核对 | 工作底稿、真实成功/失败案例、证据契约及 audit_package.py |
| remotion-best-practices | 动画与渲染规则 | 所有运动按帧计算；先代表帧后全片 |

来源是作者游戏团队项目的 reusable-skills；已安装版本与该目录当前 SKILL.md 哈希一致。Skill 未声明当前语义版本，旧 installed-baseline-0.1.0 已落后，因此用当前文件哈希标识：

- skill-launch-studio SKILL.md：`15b3c4592e5adb66f106a4720e4013af2f20c48144477bb314e5f13bd6eba4e6`
- skill-productization SKILL.md：`57f1a163733ecff98f00d98caf520befd3783884bb6f492d729a9c3be252586f`
- Remotion starter package：2.0.0；Remotion 4.0.534、React 19.2.0，依赖锁文件一同保留。

模板许可另见 motion/UPSTREAM-LICENSE.txt；不等同于项目许可证。安装绝对路径与调用日志仅保存在本机私有工作记录，不进入公开包。

## 这次复用的摩擦

结构可直接复用：文案先对齐实际输出，打包脚本直接检查双语媒体和预算。需要手工处理：旧版本基线没有覆盖当前更新；模板字体是特定文案的子集，新字必须重新子集化并验证；模板的示例工作面必须替换为本项目真实计划与回执。已有依赖可以复用，但浏览器路径需显式选择。

这些是本次观察，未计时，不转换成效率提升百分比。未擅自改造原 Skill。

## 中文视觉修正版的实际纠正

先前虽读取Skill并执行编码检查，但没有充分落实已选参考的字重、纸卡和连续动作，这是执行偏差。此次查看四个项目实际MP4/GIF，固定字体来源，先交并审查修正关键帧，再修复遮挡和转场；整片只渲染中文。字体加载及字形覆盖有实际记录，编码仍使用原脚本函数和检查器。共享Skill未修改。

## 双项目分离与系统选择

最新指令将粉色 Agent Gift 独立为另一项目。Client Setup 保留 FDE 定位及蓝色媒体，只补 Windows/Mac、本机/另一台的只读引导与明确支持矩阵。复用 skill-productization 的目标/证据分离、skill-creator 的入口与元数据检查。原蓝色影片未改色、未重新渲染；粉色文案和关键帧仅属于 Agent Gift。
