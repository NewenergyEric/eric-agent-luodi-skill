# 来源与许可状态

client-setup 的项目许可证尚待作者选择。下面只记录第三方材料自身的来源与许可，不替本项目选择授权条款。

## 运行器与设计参考

运行器使用 CPython 标准库，不分发 Python 安装包或 FoundryAPI 服务。实现时只读参考过 CiciStudio 的 Recipe 校验、计划与前镜像 hash、Skill 快照和交付回执原则。

本次核对固定提交 [`ca2cbcdc9054cf1fe48e60171578209971ac0d38`](https://github.com/NewenergyEric/CiciStudio/tree/ca2cbcdc9054cf1fe48e60171578209971ac0d38) 的 [recipes.py](https://github.com/NewenergyEric/CiciStudio/blob/ca2cbcdc9054cf1fe48e60171578209971ac0d38/cici_foundry/recipes.py)、[change_plans.py](https://github.com/NewenergyEric/CiciStudio/blob/ca2cbcdc9054cf1fe48e60171578209971ac0d38/cici_foundry/change_plans.py) 与 [product_delivery.py](https://github.com/NewenergyEric/CiciStudio/blob/ca2cbcdc9054cf1fe48e60171578209971ac0d38/cici_foundry/product_delivery.py)。该提交根目录未见 LICENSE，GitHub 元数据没有检测到许可证。

本项目没有复制或分发这些模块，也不将公开可见视为可再授权。当前本地运行器与三个模块的规范化非空行最长连续匹配分别为 2、2、3 行，为通用 import 等短片段；结合实现来源记录完成此次非纳入依赖的范围核对。这不是对任意后续复制的授权。

## 展示制作

- `motion/` 模板和部分逐帧结构改编自作者已安装的 skill-launch-studio。原模板声明 MIT；原声明完整保留于 `motion/UPSTREAM-LICENSE.txt`。其原始媒体打包、验收脚本在本次制作中执行，副本仅作为制作工具分发于 `motion/tools/`。
- Noto Sans SC 字体子集用于本次视频文字。保留 SIL OFL 1.1 原文于 `motion/public/fonts/OFL.txt`。字体源名称和版权信息保留。
- 可编辑视频工程固定 Remotion 4.0.534 和 React 19.2.0 等版本，详见 `motion/package-lock.json`。不分发 node_modules；使用者安装或运行媒体制作依赖前需遵守各自许可，Remotion 的适用条款见 [官方许可说明](https://www.remotion.dev/docs/license)。
- FFmpeg/FFprobe 仅用于本机生成和检查媒体，不分发二进制。
- 视频内容、三条合成订单、客户代号和结果展示均为本项目原创合成示例，不包含真实客户素材。

运行时包来源仍固定为 `bundled://safe-order-summary`，第三方归属链接不是运行时下载源。
