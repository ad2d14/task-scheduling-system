# 自审查认证格式 — Auto-Review Attestation Template
# TheCalmCritic v2.0.0 输出标准格式
# 每次重要输出必须附带此签名

---

## 标准输出格式（含认证）

```markdown
## [输出标题]

[主体内容]

---

## 自审查认证（Auto-Review Attestation）

本输出已通过内置BLIND-SCAN五维审查：

| 维度 | 评分 | 发现数 | 状态 |
|------|------|--------|------|
| B-Bias（偏见） | X/5 | N | ✓ PASS / ⚠️ P2 / 🔴 P1+ |
| L-Logic（逻辑） | X/5 | N | ✓ / ⚠️ / 🔴 |
| I-Information（信息） | X/5 | N | ✓ / ⚠️ / 🔴 |
| N-Narrative（叙事） | X/5 | N | ✓ / ⚠️ / 🔴 |
| D-Dependency（依赖） | X/5 | N | ✓ / ⚠️ / 🔴 |

**SHARP总评分**：XX / 25（通过线 ≥18）
**裁决结果**：✅ PASS / ⚠️ CONDITIONAL / ❌ REJECT / 🚨 ESCALATE

**风险分级**：P0=N · P1=N · P2=N · P3=N

**最大盲区**：[一句话概括]
**可验证改进建议**：[具体、可执行的验证要求]

*BLIND-SCAN v1.0.0 | TheCalmCritic v2.0.0 | 2026-MM-DD*
```

---

## Escalation 升级通知模板

```markdown
## 🚨 人工接管通知（Escalation Notice）

主Agent [TheCalmCritic] 在 **3轮**自审查循环后仍未达到输出标准，已触发人工接管机制。

**当前状态**：
- SHARP评分：XX/25（阈值：18）
- 未解决 P0：N 项
- 未解决 P1：N 项
- 迭代次数：3 / 3

**当前最优尝试**：
[对应当前最优产出的摘要]

**完整审查记录**：
[每轮 CRIT 审查报告摘要]

**建议人工处理方向**：
[具体建议]

*需人工审查后决定处置方式*
```

---

## 快速使用规则

1. **所有涉及分析、建议、数字结论的输出**，必须附带上方认证块
2. 如果 SHARP < 18，认证中明确显示 `❌ REJECT`，不隐藏
3. 如果存在 P0/P1，在认证中用 🔴 标注
4. 如果是 CONDITIONAL_PASS，用 ⚠️ 并说明需验证的条件
5. 以上模板存于 `notes/attestation-format.md`，每次输出前引用

---

*引入日期：2026-05-05 | 来源：TheCalmCritic v2.0.0 main-agent.yaml*
