# LogFlow — Multi-Agent Log Analysis Pipeline

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

**LogFlow** is a multi-agent AI pipeline that orchestrates 4 specialized agents to automatically analyze application logs, detect anomalies, trace root causes, and generate actionable fix recommendations through structured long-chain reasoning.

```
Collector → Analyzer → Diagnoser → Advisor
    │           │           │          │
    ▼           ▼           ▼          ▼
  Parse      Detect      Trace      Generate
  Logs       Patterns    Root Cause Fixes
```

### Architecture

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Collector** | Parses raw logs, extracts structured entries, identifies log format and sources | Raw log files | Structured JSON log report with metrics |
| **Analyzer** | Detects error clusters, anomalies, correlations, and frequency patterns | Collector report | Ranked error clusters with severity |
| **Diagnoser** | Traces root causes, builds evidence chains, assesses blast radius | Analyzer report | Root cause hypotheses with confidence levels |
| **Advisor** | Generates immediate fixes, permanent solutions, prevention strategies | Diagnoser report | Prioritized actionable recommendations |

### Key Features

- **Long-chain reasoning**: Each agent consumes the previous agent's structured output, building a reasoning chain across 4 stages
- **Multi-agent collaboration**: 4 agents with distinct system prompts, roles, and output schemas
- **Structured inter-agent communication**: All agent outputs are JSON-serializable, enabling pipelining and audit trails
- **Root cause tracing**: Diagnoser builds evidence chains from log entries to root causes
- **Actionable output**: Advisor generates specific, implementable fix recommendations with effort estimates

### Quick Start

```bash
# Clone
git clone https://github.com/dongjieliang8-blip/logflow.git
cd logflow

# Install
pip install -r requirements.txt

# Configure (get your key at https://platform.deepseek.com)
cp .env.example .env
# Edit .env: set DEEPSEEK_API_KEY=sk-xxx

# Run full pipeline on log files
python -m src.main run ./demo/sample_logs

# Run collector only (dry run)
python -m src.main collect ./demo/sample_logs

# Check config
python -m src.main config
```

### Demo Output

```
╭──────────────────────────────────────────╮
│ STAGE 1/4: Collector Agent — parsing logs│
╰──────────────────────────────────────────╯
┌─────────────── Collector Results ────────┐
│ Metric           │ Count                 │
│ Total Lines      │ 65                    │
│ Total Entries    │ 48                    │
│ Error Entries    │ 12                    │
│ Unique Sources   │ 6                     │
└──────────────────────────────────────────┘
Levels: {'INFO': 22, 'WARN': 8, 'ERROR': 14, 'FATAL': 1}

╭──────────────────────────────────────────╮
│ STAGE 2/4: Analyzer Agent — detecting    │
│ patterns                                 │
╰──────────────────────────────────────────╯
Error clusters: 3
  C1 [critical] Connection pool exhaustion (×5)
  C2 [high] Payment gateway timeout (×3)
  C3 [medium] Redis connection lost (×1)

... (Stages 3 & 4) ...

Pipeline Complete — Time: 78.5s — Errors: 0
```

### Requirements

- Python 3.10+
- DeepSeek API key ([platform.deepseek.com](https://platform.deepseek.com))
- OpenAI Python SDK (works with DeepSeek's compatible API)

### Token Consumption

A full pipeline run on a typical log set consumes approximately 2-4 million tokens across all 4 agents.

---

<a name="chinese"></a>
## 中文

**LogFlow** 是一个多 Agent 协作的 AI 日志分析流水线，通过 4 个角色分工明确的 Agent 实现日志解析→异常检测→根因追踪→修复建议的完整闭环。

### Agent 职责

| Agent | 核心能力 |
|-------|---------|
| **Collector** | 解析原始日志，提取结构化条目，识别日志格式和来源 |
| **Analyzer** | 检测错误聚类、异常模式、关联关系和频率特征 |
| **Diagnoser** | 追踪根因，构建证据链，评估影响范围 |
| **Advisor** | 生成即时修复、永久方案和预防策略 |

### 核心亮点

- **长链推理**：4 个 Agent 消费上一个 Agent 的结构化输出，形成跨 4 阶段的推理链路
- **多 Agent 协作**：4 个 Agent 拥有独立的系统提示词、角色定义和输出 Schema
- **结构化通信**：所有 Agent 间通信均为 JSON 格式，可追溯、可审计
- **根因追踪**：Diagnoser 从日志条目构建证据链定位根因
- **可执行输出**：Advisor 生成具体可实施的修复建议，含工作量评估

### 技术栈

- **LLM**: DeepSeek API（兼容 OpenAI SDK）
- **CLI**: Click + Rich
- **语言**: Python 3.10+
- **Token 消耗**: 完整流水线运行约消耗 200-400 万 Token

---

## License

MIT
