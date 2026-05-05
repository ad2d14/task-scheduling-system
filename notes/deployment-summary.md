# TheCalmCritic v2.0.0 部署清单 — 2026-05-05
# 渐进式完整部署完成状态

---

## 📦 部署总览

| 阶段 | 内容 | 文件数 | 状态 |
|------|------|--------|------|
| 阶段一 | BLIND-SCAN 27项检查清单 | 6 | ✅ 完成 |
| 阶段二 | 三模式提示词 + SHARP + Arbiter | 5 | ✅ 完成 |
| 阶段三 | 认证模板 + 交互命令 + 模型参数 | 4 | ✅ 完成（本章） |

**总文件数：15 个新文件/变更**

---

## ✅ 阶段一：BLIND-SCAN 27项检查清单

| 文件路径 | 内容 |
|---------|------|
| `skills/skill-vetter/references/blind-scan-bias.md` | B维度（偏见检测）5项 |
| `skills/skill-vetter/references/blind-scan-logic.md` | L维度（逻辑验证）6项 |
| `skills/skill-vetter/references/blind-scan-info.md` | I维度（信息审计）6项 |
| `skills/skill-vetter/references/blind-scan-narrative.md` | N维度（叙事解构）5项 |
| `skills/skill-vetter/references/blind-scan-dep.md` | D维度（依赖分析）5项 |
| `skills/skill-vetter/SKILL.md` | 预安装审查协议引用 |

---

## ✅ 阶段二：核心引擎

| 文件路径 | 内容 |
|---------|------|
| `memory/procedural/sharp-scoring.md` | 完整SHARP评分体系（25分制，通过线18分） |
| `notes/arbiter.md` | 裁决矩阵（五规则）+ 状态机 + Escalation模板 |
| `SOUL.md` | 三态自循环工作模式 + EXEC/CRIT/ARBI 提示词 |
| `AGENTS.md` | CRIT行为准则 + 快速自检触发 |
| `HEARTBEAT.md` | 自循环引擎触发 + 迭代计数 |

---

## ✅ 阶段三：输出标准化与交互

| 文件路径 | 内容 |
|---------|------|
| `notes/review-template.md` | BLIND-SCAN 自审评分卡（快速执行工具） |
| `notes/review-log/` | 自审记录存档目录 |
| `notes/three-modes.md` | 完整三模式提示词 + 状态图 |
| `notes/attestation-format.md` | 自审查认证模板（Auto-Review Attestation） |
| `notes/model-params.md` | 分模式温度控制 + 运行安全策略 |
| `AGENTS.md`（更新） | 交互命令 `/critique` `/status` `/escalate` |

---

## 📊 OpenClaw 配置映射

| TheCalmCritic 模块 | OpenClaw 接入文件 | 对应状态 |
|-------------------|------------------|---------|
| 三模式提示词 | `SOUL.md` / `notes/three-modes.md` | ✅ 完全映射 |
| BLIND-SCAN 27项 | `skill-vetter/references/` | ✅ 完全映射 |
| SHARP 25分制 | `memory/procedural/sharp-scoring.md` | ✅ 完全映射 |
| P0-P3 风险分级 | `AGENTS.md` | ✅ 完全映射 |
| 裁决矩阵 | `notes/arbiter.md` | ✅ 完全映射 |
| 自审查模板 | `notes/attestation-format.md` | ✅ 完全映射 |
| 交互命令 | `AGENTS.md` | ✅ 通过对话约定实现 |
| 温度参数 | `notes/model-params.md`（模拟） | ⚠️ 提示词级模拟 |
| 3轮循环上限 | `AGENTS.md` / `HEARTBEAT.md` | ✅ 已记录 |
| 10分钟超时 | `HEARTBEAT.md`（模拟） | ⚠️ 无原生超时 |
| 自一致性规则 | `notes/arbiter.md` | ✅ 已定义 |

---

## 🔄 自循环引擎工作流（已激活）

```
[用户输入]
     ↓
[EXEC 执行模式] ← 温度0.3
  产出：分析 + assumptions_list + confidence_score
     ↓
[CRIT 批判模式] ← 温度0.05（有罪推定）
  BLIND-SCAN 五维审查 + SHARP评分
     ↓
[ARBI 裁决模式] ← 温度0.1（保守裁决）
  五规则判定 → PASS / CONDITIONAL_PASS / REJECT / ESCALATE
     ↓
  ↓
REJECT → [REWORK] → 循环（最多3次）
     ↓
  ≥3次未通过 → ESCALATE（人工接管）
     ↓
PASS → 输出 + 自审查认证（Auto-Review Attestation）
```

---

## 📝 用户交互命令（已定义）

| 命令 | 作用 |
|------|------|
| `/critique` | 强制触发 CRIT 模式自审 |
| `/status` | 查询 SHARP 评分 + 迭代次数 |
| `/escalate` | 手动触发人工接管 |

---

## ⚠️ 当前限制与下一步

### 已实现的（完全对齐）
- BLIND-SCAN 27项 + SHARP 25分 + 裁决矩阵
- 三模式提示词注入 SOUL.md
- 自审查认证输出格式
- P0-P3 风险分级
- 迭代计数逻辑

### 部分实现的（提示词级模拟）
- 分模式温度切换（无原生支持）
- 10分钟超时（无原生超时机制）

### OpenClaw 架构限制说明
OpenClaw 为单 Agent 架构，无法原生实现多 Agent 状态机。
通过 `SOUL.md` + `AGENTS.md` 中的提示词注入，模拟 EXEC/CRIT/ARBI 三态切换。
每次响应前，通过指令「我是EXEC」「我是CRIT」进行模式切换。

### 可选的下一步
1. **完善 identity**：填充 IDENTITY.md + USER.md（在 open loop 中）
2. **WAL 协议对齐**：将 BLIND-SCAN 整合至 HEARTBEAT.md WAL 扫描
3. **proactive-ideas.md**：记录每周主动创意，跟踪反向提示执行情况

---

*部署完成：2026-05-05 | 来源：TheCalmCritic v2.0.0 main-agent.yaml*
