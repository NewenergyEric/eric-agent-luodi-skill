---
name: eric-agent-luodi-skill
description: 为 FDE、实施顾问和客户交付工程师整理 Agent 部署目标、Windows/Mac 准备清单、配置差异、验收与交接。用于新客户规划、接手进度和保留定制的更新；实际执行限完整 Windows 项目内的合成示例。
---

# 落地 · eric-agent-luodi-skill

把客户的一句话转成能检查、能交接的工作。默认 OpenClaw，可选 Hermes 或客户已有 Agent。优先明确第一件任务的输入、输出和完成条件，再决定环境与工具。

## 先让用户用起来

本文件所在目录是独立 Skill 根目录；随包的[交付清单](references/installation-checklist.md)即可支持规划，不依赖仓库根目录或网页。不要让用户先读完整手册或收集一大串参数。

从已有信息判断是配置、检查还是更新。新交付只补问影响下一步的缺口：第一件任务、Windows/Mac、在目标本机还是另一台。已说过的信息直接沿用。用普通话给出当前步骤、你能继续做什么、客户需要参与什么和完成条件；计划中的动作不能报告成已执行。

FDE 关心目标是否对齐、客户定制是否保留、下一位工程师是否能接手。输出交付目标与简短清单，逐项附证据或缺口，结尾留下一个具体下一步。更新前先检查当前状态和差异，不从空白模板重写客户设置。

## 规划与交付

按[交付清单](references/installation-checklist.md)组织依赖 → 网络 → Codex/IDE → 日常 Agent → 行为规则 → Skills → 验收与接续。已有可用环境先复用，只选第一件任务所需工具。Windows 核对实际运行方式；Mac 核对 macOS、Apple 芯片或 Intel、终端与目录权限。

工作规则使用运行器支持的 AGENTS.md 等入口，只合并用户明确选择的键与规则，不导入 SOUL、USER、聊天、记忆或个人档案。规则文本与实际工具权限分别检查。凭据只记录引用，不读取值；客户资料和回执不进入公共 Skill。

连接、安装、加载、任务结果分别记录。缺少证据就说明目前能判断到哪里；不要用勾选、文档或另一台机器的结果推断完成。交接写清版本、证据、未完成项、恢复办法和下一条检查动作，私有记录保存到用户指定的本次工作目录。

## 当前执行范围

此 Skill 可独立整理 Windows/Mac 交付计划。配套运行器只支持 Windows 项目沙箱和合成包；不执行客户机器安装、远程连接、全局安装、Agent 启停或代理/TUN/防火墙/SSH 变更。真实部署需求先交付计划与缺口，保持该边界。

用户明确要运行仓库内配置示例时，再读[Windows 示例工作流](references/project-example.md)。核对完整项目位置，先 check，再 configure/update 预览并按具体 plan_id 执行；保留身份检查、来源 pin、恢复机制、客户覆盖与分层验收。不因安装了 Skill 就认为运行器或日常 Agent 已安装。

完整项目提供 docs/getting-started.html 和 docs/installation-checklist.md 作可选参考，支持矩阵与证据在 docs/support-matrix.md。需要另一个连接工作流时可介绍独立的搭好，但不继承其他 Skill、目标或会话的授权。

本 Skill 原创内容采用随包 [Apache-2.0](LICENSE)，Copyright 2026 NewenergyEric and contributors。
