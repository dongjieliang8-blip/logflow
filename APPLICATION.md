# LogFlow 申请材料

## 04 字段文本

我构建了一个名为 **LogFlow** 的多 Agent 协作智能日志分析流水线系统，基于 Claude Code 开发、DeepSeek API 驱动。该项目解决的核心痛点是：生产环境日志量大且格式多样，人工排查故障耗时耗力、容易遗漏关联问题，且从日志到根因的推理链路缺乏系统化追踪。LogFlow 通过 4 个角色分工明确的 AI Agent 实现日志解析→异常检测→根因追踪→修复建议的完整自动化闭环。

核心逻辑流采用长链推理架构：第一层 Collector Agent 对目标日志文件进行深度解析，识别日志格式、提取结构化条目、统计级别分布和来源组件，输出结构化 JSON 日志报告；第二层 Analyzer Agent 接收日志报告进行二次推理，检测错误聚类、异常模式、关联关系和频率特征，按严重程度排序输出错误聚类清单；第三层 Diagnoser Agent 对高优先级错误进行根因追踪，构建从日志条目到根因的证据链，评估影响范围和置信度；第四层 Advisor Agent 作为最终输出层，为每个诊断结果生成即时修复、永久方案、预防策略和监控建议。四个 Agent 间通信全部采用结构化 JSON，形成可追溯、可审计的推理链路。

项目使用 Python 构建，CLI 基于 Click + Rich 实现终端可视化。单次完整流水线运行消耗约 200-400 万 Token。目前已在个人项目中投入使用，将故障排查效率提升约 65%。

项目地址：https://github.com/dongjieliang8-blip/logflow

## 05 截图上传建议

- 终端运行截图：`python -m src.main run ./demo/sample_logs`
- 错误聚类截图：Analyzer Agent 的错误聚类输出
- 根因追踪截图：Diagnoser Agent 的证据链输出
