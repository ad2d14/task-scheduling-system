# Self-Improving Agent 技能分析报告

> 生成时间: 2026-05-05 18:34 CST
> 图谱位置: `memory/ontology/graph.jsonl`
> 图谱统计: **187 个实体 + 178 条关系**

---

## 一、技能概述

**Self-Improving Agent** 是一个元技能（meta-skill），通过结构化日志实现持续改进。

| 属性 | 值 |
|------|------|
| 版本 | 1.0.0 |
| 作者 | peterskoett |
| 来源 | ClawhHub |
| 风险等级 | 🟢 LOW |
| 核心功能 | 错误记录、修正捕获、知识缺口检测、最佳实践记录、功能请求跟踪 |

---

## 二、核心能力 (12项)

| # | 能力 | 自动化程度 | 说明 |
|---|------|-----------|------|
| 1 | Error Logging | 自动 | 命令失败、API错误、集成错误记录到ERRORS.md |
| 2 | Correction Capture | 自动 | 用户纠正（"No, that's wrong..."）记录到LEARNINGS.md |
| 3 | Knowledge Gap Detection | 自动 | 未知信息、文档过时、API行为差异检测 |
| 4 | Best Practice Capture | 自动 | 发现更优方案时记录best_practice |
| 5 | Feature Request Tracking | 自动 | 用户请求的不存在能力记录到FEATURE_REQUESTS.md |
| 6 | Learning Promotion | 手动 | 晋升到SOUL.md/AGENTS.md/TOOLS.md永久文件 |
| 7 | Recurring Pattern Detection | 半自动 | 搜索历史、链接See Also、更新Recurrence-Count |
| 8 | Periodic Review | 手动 | 自然断点定期回顾learnings |
| 9 | Skill Extraction | 手动 | 高价值learning提取为独立skill |
| 10 | Inter-Session Communication | 半自动 | sessions_list/history/send跨会话共享 |
| 11 | Recurrence Counter | 自动 | Track Recurrence-Count/First-Seen/Last-Seen |
| 12 | Hook Integration | 可选 | OpenClaw hooks自动提醒（需单独配置） |

---

## 三、日志文件结构

```
.learnings/
├── LEARNINGS.md      # 修正(correction)、知识缺口(knowledge_gap)、最佳实践(best_practice)
├── ERRORS.md          # 命令失败、集成错误
└── FEATURE_REQUESTS.md # 用户请求的不存在能力
```

### 格式标识符

| 类型 | 格式 | 示例 |
|------|------|------|
| Learning | `LRN-YYYYMMDD-XXX` | `LRN-20260505-001` |
| Error | `ERR-YYYYMMDD-XXX` | `ERR-20260505-A3F` |
| Feature | `FEAT-YYYYMMDD-XXX` | `FEAT-20260505-002` |

---

## 四、已知限制与边界 (8项)

| 边界 | 类型 | 严重度 | 说明 |
|------|------|--------|------|
| 手动触发为主 | 策略 | 🟡 警告 | 自动检测触发，但写入仍需Agent主动执行 |
| 仅记录不修复 | 技术 | ⚪ 信息 | 只记录问题，不自动修复 |
| 晋升需人工判断 | 策略 | ⚪ 信息 | 无自动规则判断何时晋升 |
| 多Agent隔离 | 技术 | 🟡 警告 | learnings不自动跨Agent同步 |
| 初始化需创建文件 | 依赖 | 🟡 警告 | 首次使用需创建.learnings/目录 |
| 敏感信息风险 | 安全 | 🟡 警告 | 日志可能包含敏感信息，依赖Agent遵守脱敏 |
| 晋升阈值主观 | 策略 | ⚪ 信息 | Recurrence-Count >= 3 的判断依赖Agent |
| 无自动提醒hook | 技术 | ⚪ 信息 | 未配置hooks时无自动检查 |

---

## 五、核心使用场景 (9个)

| 场景 | 触发时机 | 优先级 |
|------|----------|--------|
| 命令失败记录 | 命令返回非零退出码 | 🔴 高 |
| 用户纠正记录 | "No, that's wrong..." | 🔴 高 |
| 知识缺口补录 | 发现未知信息 | 🔴 高 |
| 更好方案记录 | 发现更优方法 | 🟡 中 |
| 功能请求记录 | 用户请求不存在能力 | 🟡 中 |
| 定期回顾 | 任务前/后/每周 | 🟡 中 |
| 晋升决策 | 评估learnings是否晋升 | 🟡 中 |
| 重复检查 | 遇到问题时检查历史 | 🟡 中 |
| 技能提取候选 | 高质量learning评估 | ⚪ 低 |

---

## 六、联动架构分析

### 6.1 与其他技能的深度集成

| # | 集成组合 | 模式 | 说明 |
|---|----------|------|------|
| 1 | **Self-Improving + Elite Memory** | 状态→反思 | Elite WAL保证实时状态，Self-Improving负责事后反思。重要learning晋升到MEMORY.md |
| 2 | **Self-Improving + Ontology** | 原始→结构化 | .learnings/作为原始素材，Ontology作为知识图谱索引层。定期将高频条目转存为实体 |
| 3 | **Self-Improving + Skill Vetter** | 审计追踪 | 审查失败经验→ERRORS.md，安全模式→LEARNINGS.md。形成安全知识库 |
| 4 | **Self-Improving + Memory Manager** | 学习→记忆 | 经过提炼的重要learning存入MM的semantic（知识）或procedural（流程）层 |
| 5 | **Self-Improving + Baidu Search** | 缺口→填补 | 发现知识缺口时先搜索正确答案，再记录已修复的knowledge_gap |
| 6 | **Self-Improving + Agent Workflow** | 上下文传播 | spawn前传递相关learnings，完成后记录best_practice |

### 6.2 晋升决策树

```
Learning是否通用？
├── Yes → 是行为/风格相关？
│   ├── Yes → Promote to SOUL.md
│   └── No → 是工具相关？
│       ├── Yes → Promote to TOOLS.md
│       └── No → Promote to AGENTS.md
└── No → 保留在.learnings/
```

---

## 七、最佳实践 (8条)

| # | 实践 | 分类 | 说明 |
|---|------|------|------|
| 1 | **立即记录** | 质量 | 问题解决后立即记录，上下文最完整 |
| 2 | **具体明确** | 质量 | 避免模糊描述，包含具体错误信息、正确做法、步骤 |
| 3 | **包含复现步骤** | 质量 | 包含环境、输入参数、命令序列 |
| 4 | **建议具体修复** | 可操作性 | 不只说有问题，给出具体修复方向 |
| 5 | **链接相关条目** | 效率 | 相似问题添加See Also，避免重复 |
| 6 | **积极晋升** | 记忆 | 不确定时就晋升，.learnings/作草稿，永久文件作定稿 |
| 7 | **定期回顾** | 维护 | 自然断点检查learnings，保持活跃 |
| 8 | **简短摘要优先** | 安全 | 用脱敏摘要而非完整命令输出 |

---

## 八、与 Elite Memory 的互补关系

**Self-Improving Agent vs Elite Longterm Memory：**

| 维度 | Self-Improving Agent | Elite Longterm Memory |
|------|---------------------|----------------------|
| 触发时机 | 错误/纠正/发现时 | 任何状态变更时 |
| 内容性质 | 反思性（事后） | 实时性（当下） |
| 格式 | 结构化日志条目 | 分层文件存储 |
| 目标 | 持续改进 | 上下文保持 |

**组合效果：** Elite Memory 保证实时状态不丢失，Self-Improving 保证从经验中学习改进。

---

## 九、图谱统计

| 实体类型 | 数量 |
|----------|------|
| Skill | 6 |
| Capability | 50 |
| Boundary | 40 |
| UseCase | 37 |
| Integration | 23 |
| BestPractice | 31 |
| **总计** | **187** |

| 关系类型 | 数量 |
|----------|------|
| has_capability | 50 |
| has_boundary | 40 |
| has_use_case | 37 |
| integration_pattern | 14 |
| integrates_with | 11 |
| follows_practice | 11 |
| constrained_by | 10 |
| enhances | 5 |
| **总计** | **178** |