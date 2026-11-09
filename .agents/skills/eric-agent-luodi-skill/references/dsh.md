# DeepSeek Harness（DSH）：复用与接续

## 来源和版本

以 [DeepSeek 官方 Harness 页面](https://www.deepseek.com/en/harness/) 和 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) 为来源。2026-11-09 核对官方 README、Web 引导和桌面文档；后续部署仍按实际安装版本重新核对。不要把社区同名封装当作官方发行版。

先区分已安装的桌面版、npm CLI 或源码运行方式。桌面版检查应用元数据和打开入口；CLI 已存在时用其无秘密版本信息检查。桌面版菜单的 **Manage dsh Command…** 可安装或修复命令入口，命令注册是可选项；不要因 PATH 中没有 `dsh` 就重装用户的桌面应用。参考[官方桌面说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/desktop/README.md)。

官方 README 提供 npm 启动方式 `npx @deepseek-ai/dsh web`。这是来源说明，不是自动执行指令；未安装时先核对所选版本、Node 要求和安装授权，形成固定版本方案，复用已有依赖，不直接以未固定的 latest 改写现有环境。

## 给用户的模型卡

> 操作位置：目标电脑的 DSH 界面。  
> 打开 **Settings → Models（设置 → 模型）**，选择实际版本提供的 DeepSeek 配置入口，在应用中输入 API Key 并保存。不要把 Key 发到聊天。  
> 已配置：直接保留，回复“已配置”即可。  
> 下一步：选择一个空白测试工作区，用公开示例任务验证；在验证前仍标记“用户已配置，调用待验证”。

此路径来自[官方 Web 引导](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/index.md)，实际桌面版或语言版本不同则以当前界面为准，不臆造按钮。Web 界面还需选择工作区，不能因会话输入框不可用就认定 Key 无效。模型配置的更多选项见[官方提供商说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/providers.md)。

## 本机与远程打开

按官方 README，Web 默认入口为 `http://127.0.0.1:3080`；实际以启动输出为准，桌面版可使用动态端口。SSH 启动不保证自动打开浏览器。控制端浏览器里的 127.0.0.1 是控制端自身，不能当成远端 Mac；优先由用户在目标电脑打开，或在已有授权范围内安排仅本机监听的 SSH 转发。不要为了打开页面把服务绑定到所有网络接口。

## 不混用模型配置

DSH、OpenClaw 和 Codex 的模型配置分别验收。用户在 DSH 或其中一个程序中配置 DeepSeek Key，不代表其他程序自动可用；不复制 Key 或读取值来同步。只记录提供商名称、由用户配置、验证状态和下一步；实际模型请求可能计费，须在本次授权范围内执行。

示例验收：在新建的空白工作区中让用户发送“把以下三条公开示例待办整理成表格”，核对结果和权限范围。没有实际结果就保留待验证，不把启动成功或端点 HTTP 401 当成模型可用。
