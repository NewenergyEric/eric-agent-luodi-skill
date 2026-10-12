# 落地 · luodi 展示影片源码

当前展示为中文：24 秒、1280×720、30 FPS。沿用原 FDE 蓝色、Noto Sans SC 字体、短标题和连续运动的纸卡。主线是新电脑 → 选择系统与 Agent → 检查环境 → 配置 → 第一项工作 → 持续更新。每段明确区分目标流程与当前已验证的本地基础能力。

工具本体仍只用 Python 标准库；媒体重建需要 Node 和锁定的 Remotion 4.0.534 / React 19.2.0，以及 ffmpeg/ffprobe。

```sh
npm ci
node render.mjs qa zh
node render.mjs films zh
python -B pack_zh.py --source out/launch-zh.mp4 --out out/zh-preview
```

`qa` 输出六个章节、边界和结尾的代表帧；`films zh` 输出完整中文影片。`REMOTION_BROWSER_EXECUTABLE` 可指定已安装的 Chromium，`LAUNCH_DEPENDENCIES` 只允许复用依赖版本完全相同的现有工程。

字幕、章节时间和逐帧运动在 `src/LaunchFilm.tsx`；字幕副本位于 `../assets/readme/hero-zh.srt`。字体在渲染前显式等待加载，日志记录常规与加粗字体的检查结果。`src/story.json` 保存各镜头文案及其能力边界。

`pack_zh.py` 调用随项目保留的原版 `tools/package_media.py` 编码函数，以及 `tools/check_media.py` 的 MP4、GIF 和 WebP 检查器。原双语 `check()` 包装要求两种语言，本轮仅制作中文，因此采用对应的中文规格断言。没有修改共享 Skill 脚本，也没有将旧英文素材描述成本次成果。

MP4 为 H.264、yuv420p、faststart；GIF/WebP 为 800×450、20 FPS、24 秒。最终 GIF 为 24 色，首轮 32 色超预算记录保留在媒体清单中；帧率、分辨率和时长未降低。每次编码要求新输出目录，避免覆盖上一版结果。

原版英文影片已从当前展示入口移除，旧媒体及源码保留在本机私有回退快照中。当前英文 README 使用同一中文预览。

上游模板许可证见 `UPSTREAM-LICENSE.txt`，Noto 字体 OFL 见 `public/fonts/OFL.txt`。这些不代表本项目已选择发布许可证。影片中的新电脑部署与第一次工作为目标流程和合成示意，真实 Agent 安装、加载及客户任务均未验证。

本次更名只更新品牌字样，保留蓝色、字体轮廓、分镜与逐帧动作。品牌新增字形已补入同一 Noto Sans SC 来源子集。用户运行命令和配置包来源标识不随品牌更名迁移。
