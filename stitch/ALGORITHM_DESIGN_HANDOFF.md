# CSU Date 算法设计交接文档

更新时间：2026-04-01

## 1. 文档目的

这份文档面向算法设计与匹配策略同学。它基于当前仓库中已经实现的完整版问卷和若干需求 prompt，整理出：

- 问卷特征空间
- 哪些字段该做硬过滤，哪些该做软匹配
- 每周一对一匹配的推荐算法流程
- 匹配解释和报告生成方式
- 冷启动、约束、公平性与评估指标

一句话结论：

**当前仓库没有真实算法实现，只有静态页面和硬编码报告；但问卷设计已经足够支撑一个“规则过滤 + 加权打分 + 图匹配”的第一版可上线算法。**

---

## 2. 当前代码对算法的真实输入输出定义

### 2.1 已有输入

`index.html` 已实现 7 模块完整版问卷，字段已经覆盖：

- 基本身份与约束
- 自我特征
- 伴侣偏好
- 重要题加权
- 兴趣爱好
- 核心特质
- 季节性破冰题

### 2.2 尚未实现的部分

以下内容目前都只是前端展示，不是算法产物：

- 本周匹配对象
- 契合度总分
- 分维度得分
- 共同点
- 互补点
- 匹配叙事
- 历史匹配统计

### 2.3 当前前端对算法输出的期望

从 `dashboard.html` 和 `report.html` 看，前端最终需要的不是一个单一 score，而是一整组结构化结果：

- `overall_score`
- `dimension_scores`
- `match_preview`
- `shared_points`
- `complementary_points`
- `narrative`
- `ice_breakers`

因此算法输出要同时满足：

- 排序和分配
- 可解释性
- 文案生成素材供给

---

## 3. 产品目标与算法约束

CSU Date 不是刷卡片产品，而是“每周只遇见一个人”的低频高质量匹配系统。算法目标不能只看“覆盖率”，还要关注：

- 低错配率
- 高可解释性
- 互相可接受
- 周期稳定性
- 小样本条件下的可用性

推荐的总目标函数：

1. 先排除明显不可能或高风险配对
2. 在剩余候选里最大化双边匹配满意度
3. 保证一人一配
4. 对低质量配对宁可不配

---

## 4. 问卷结构拆解

## 4.1 模块一：基础筛选信息

这些题主要用于过滤，不建议直接并入相似度主向量。

| 字段 | 类型 | 说明 | 作用 |
|---|---|---|---|
| `gender` | 单选 | 性别 | 兼容性过滤 |
| `sexuality` | 单选 | 性取向 | 兼容性过滤 |
| `grade` | 单选 | 年级 | 可做弱特征 |
| `campus` | 单选 | 校区 | 过滤或弱约束 |
| `college` | 下拉 | 学院 | 过滤或弱约束 |
| `height` | 数值 | 身高 | 双边范围过滤 |
| `heightPrefMin` | 数值 | 最低可接受身高 | 过滤 |
| `heightPrefMax` | 数值 | 最高可接受身高 | 过滤 |
| `hometown` | 下拉 | 家乡省份 | 弱特征 |
| `crossCampus` | 单选 | 是否接受跨校区 | 双边过滤 |
| `sameCollege` | 单选 | 是否接受同学院 | 过滤或惩罚 |

## 4.2 模块二到五：Likert + 单选题

这些是算法主干特征。

### 模块二：人生观与事业观

- `hustle`：双轨
- `citylife`
- `spending`
- `marriage`
- `goodness`
- `idealism`

### 模块三：性格与价值观

- `family_career`
- `process_result`
- `logic_feel`：双轨
- `novelty`
- `introvert`：双轨
- `conflict`

### 模块四：生活方式

- `sleep`
- `tidy`
- `canteen`
- `spicy`
- `diet`
- `datespot`
- `together`
- `travel`
- `consume`
- `studyspot`

### 模块五：亲密关系观

- `smoke`：双轨
- `drink`：双轨
- `reply_anxiety`
- `ritual`
- `opposite_friend`
- `dominance`
- `caretaker`
- `intimacy_pace`
- `meet_freq`
- `social_pda`

## 4.3 模块六：兴趣爱好

- `interests`：多选，2-5 项
- `interest_overlap`：希望相似还是互补

## 4.4 模块七：外貌气质与核心特质

- `appearance`：双轨
- `grooming`
- `selfTraits`
- `partnerTraits`
- `partnerTraitsImportant`
- `appearance_weight`
- `seasonal`：选填，不建议进入主打分

---

## 5. 建议的特征分类

这是落地时最关键的一步。不要把所有题都同等对待。

### 5.1 硬过滤特征

建议优先进入硬过滤的字段：

- `gender`
- `sexuality`
- `height` 与 `heightPrefMin/Max`
- `crossCampus`
- `sameCollege`（如果产品确认是硬条件）
- `diet`（如果产品确认饮食不兼容不可接受）
- 用户状态类条件：
  - 已验证
  - 已完成问卷
  - 当前未暂停
  - 当前周期已 opt-in

### 5.2 软过滤 / 惩罚特征

这些更适合做 penalty，不建议一刀切：

- `grade`
- `campus`
- `college`
- `hometown`
- `studyspot`
- `meet_freq`

### 5.3 主相似度特征

适合进入主相似度或主兼容度计算的：

- 所有 1-7 Likert `self`
- 非 Likert 单选题的映射特征：
  - `spending`
  - `diet`
  - `studyspot`
  - `meet_freq`

### 5.4 偏好满足特征

这部分不该拿相似度做，而应做“我的期待是否被对方满足”：

- `hustle.partner` 对比对方 `hustle.self`
- `logic_feel.partner` 对比对方 `logic_feel.self`
- `introvert.partner` 对比对方 `introvert.self`
- `smoke.partner` 对比对方 `smoke.self`
- `drink.partner` 对比对方 `drink.self`
- `appearance.partner` 对比对方 `appearance.self`
- `partnerTraits` 对比对方 `selfTraits`

### 5.5 展示型特征

不一定进入主排序，但非常适合解释与报告：

- `interests`
- `selfTraits`
- `partnerTraits`
- `seasonal`

---

## 6. 数据预处理建议

## 6.1 Likert 归一化

把 1-7 映射到 `[-1, 1]`：

```text
normalized = (value - 4) / 3
```

好处：

- 便于统一处理不同题目
- 中间值 4 自然对应 0
- 距离和相似度更稳定

## 6.2 双轨题编码

双轨题拆为两个向量：

- `self_vector`
- `partner_pref_vector`

不能简单拼成一个向量后做余弦，因为语义不同。

## 6.3 类别题编码

像 `spending`、`diet`、`studyspot`、`meet_freq` 这类单选题，推荐两种方式：

- MVP：人工定义兼容矩阵
- 进阶：one-hot 或 embedding

第一版更推荐兼容矩阵，因为可解释性更强。

## 6.4 多选题编码

`interests`、`selfTraits`、`partnerTraits` 可以编码为多热向量：

- 交集越大，加分越高
- `partnerTraits` 与对方 `selfTraits` 做包含度或 Jaccard

## 6.5 重要题加权

当前问卷的“设为重要”语义很明确：

- 这是用户主动告诉算法“这一题我很在意”

建议第一版直接使用权重乘数：

```text
base_weight = 1.0
important_weight = 2.0
```

如果双方都把同一维度标重要，可再加一个小幅 bonus。

---

## 7. 候选召回与打分总流程

推荐采用四段式流程：

1. 候选池过滤
2. 双边兼容打分
3. 全局一对一分配
4. 报告与解释生成

### 7.1 候选池过滤

对用户 A，先筛出所有满足以下条件的用户 B：

- 互相满足性别/性取向兼容
- A 的身高在 B 的可接受范围内
- B 的身高在 A 的可接受范围内
- 校区约束不冲突
- 同学院约束不冲突
- 饮食硬约束不冲突
- 当前周期双方都可参与
- 双方不是历史黑名单、投诉禁配对

这一步的目标是宁可严格，也不要把明显不可行的人送进后续评分。

### 7.2 双边兼容打分

建议总分由以下部分组成：

```text
S_total =
  0.35 * S_self_similarity
  0.25 * S_preference_fit
  0.15 * S_lifestyle_categorical
  0.10 * S_interest_overlap
  0.10 * S_trait_match
  0.05 * S_context_bonus
  - penalties
```

#### `S_self_similarity`

比较双方 `self` 向量的一致性。

适用字段：

- 单轨 Likert
- 双轨题中的 `self`

推荐计算：

- 加权 L1/L2 距离转相似度
- 或加权余弦相似度

第一版更建议“距离转分数”，因为更直观。

例如：

```text
sim_i = 1 - abs(a_i - b_i) / 6
```

其中 `a_i`、`b_i` 是 1-7 原始值。

#### `S_preference_fit`

这是这份问卷最有价值的部分。

用 A 的 `partner` 去比较 B 的 `self`，再反向比较一次：

```text
fit(A<-B) = avg_i [1 - abs(prefA_i - selfB_i) / 6]
fit(B<-A) = avg_i [1 - abs(prefB_i - selfA_i) / 6]
S_preference_fit = (fit(A<-B) + fit(B<-A)) / 2
```

字段包括：

- `hustle`
- `logic_feel`
- `introvert`
- `smoke`
- `drink`
- `appearance`

#### `S_lifestyle_categorical`

对非连续型题目做兼容矩阵，例如：

- `spending`
- `diet`
- `studyspot`
- `meet_freq`

示例：

- `接近AA制` 和 `看情况灵活处理` 可给中高分
- `接近AA制` 和 `男方多承担` 可能偏低
- `清真` 与 `无特殊要求` 不应简单当低分，而应看另一方是否接受

#### `S_interest_overlap`

适合用 Jaccard 或 overlap coefficient：

```text
S_interest_overlap = |A ∩ B| / |A ∪ B|
```

然后再乘以 `interest_overlap` 偏好修正：

- 如果双方都希望高度重合，共同爱好多时额外加分
- 如果一方偏互补，则不应因重合度低而重罚

#### `S_trait_match`

建议拆两部分：

- `selfTraits` 的交集
- A 的 `partnerTraits` 是否被 B 的 `selfTraits` 覆盖

可计算：

```text
trait_pref_fit(A<-B) = |partnerTraitsA ∩ selfTraitsB| / |partnerTraitsA|
```

如果 `partnerTraitsImportant = true`，则提高该部分权重。

#### `S_context_bonus`

用于轻微加分，不建议主导排序：

- 同校区且对方不排斥
- 年级接近
- 家乡相同或邻近
- 季节题选项相关

### 7.3 权重机制

所有带 `important=true` 的题，建议按维度权重翻倍：

```text
weight_i = base_weight_i * (important ? 2.0 : 1.0)
```

如果双方都标重要，再给一个乘数 `1.15` 左右即可，不宜过高。

---

## 8. 全局一对一匹配

这类产品不是“给每个人排 TopN”就结束，而是必须出最终配对结果。

### 8.1 问题建模

在一个周期内，构建无向带权图：

- 节点：参与用户
- 边：通过硬过滤后的候选配对
- 边权：`S_total`

目标：

- 每个节点最多匹配一次
- 总权重最大
- 低于阈值的边直接舍弃

### 8.2 推荐算法

第一版直接使用最大权匹配：

- 一般图最大权匹配
- Edmonds blossom 或成熟库

原因：

- 一人一配约束天然满足
- 比 greedy 更稳
- 数据规模在校园场景通常可控

### 8.3 低分不硬配

非常重要。

如果某用户所有候选边都低于阈值，推荐“不匹配”而不是强行分配。

建议设置：

- 最低揭晓阈值 `T_reveal`
- 候选保留阈值 `T_candidate`

其中：

- `T_candidate` 稍低，用于图构建
- `T_reveal` 稍高，用于最终发布

---

## 9. 匹配报告生成逻辑

`report.html` 已经把前端需要什么说明白了。算法要输出的不只是 score，而是可消费的解释字段。

### 9.1 解释素材优先级

建议按如下顺序挑选 3-5 条主要解释：

1. 双方都标重要且答案接近的题
2. 一方偏好与对方自我特征高度贴合的双轨题
3. 共同兴趣爱好
4. `partnerTraits` 与对方 `selfTraits` 的命中
5. 可爱但非主导的生活方式共性

### 9.2 共性生成规则

示例：

- “你们都把经世致用看得很重”
- “你们都偏向规律作息”
- “你们都喜欢在长沙城市空间里探索”

### 9.3 互补生成规则

不是所有差异都要写进报告，应该挑“能形成火花且不构成风险”的差异：

- 内向 vs 外向
- 计划型 vs 随性型
- 理性 vs 感性

不建议作为“有趣互补”展示的差异：

- 烟酒接受度严重冲突
- 婚姻观极端冲突
- 亲密节奏明显失配

### 9.4 叙事生成

第一版不必直接上大模型自由生成，建议先做模板化：

- 模板输入：高分维度、共同兴趣、互补维度、校园元素、季节题
- 模板输出：一段 100-180 字叙事

这样更稳定，也更容易做审核。

---

## 10. Shoot Your Shot 的算法处理

这是独立于常规每周匹配的特殊通道。

推荐规则：

- 它不是直接覆盖主算法
- 它先建立一条“显式意向边”
- 如果双方互相 shoot，则可：
  - 立即触发特殊匹配
  - 或在本周期图里给极高优先级

建议第一版采用“图里加大权重但仍检查硬过滤”，避免明显不合适的 pair 被强行推出。

---

## 11. 风险控制与公平性

### 11.1 不要让高活跃用户反复霸榜

如果只按最高分做局部排序，容易出现：

- 少数高兼容用户成为很多人的 top candidate
- 最终图匹配牺牲整体公平性

最大权匹配可以缓解，但仍建议加入轻度多样性或历史惩罚。

### 11.2 历史重复惩罚

建议避免短期内重复匹配同一对。

可以加入：

```text
repeat_penalty = 0.1 ~ 0.3
```

取决于：

- 是否曾匹配过
- 是否曾互发招呼
- 是否已交换联系方式

### 11.3 小众群体保护

校园数据中，某些性取向/校区/饮食约束组合可能样本很小。

建议：

- 不把低覆盖率误判为算法失败
- 对小池子做单独监控
- 报告中不要暴露任何会反推群体规模的信息

### 11.4 安全过滤

算法前置必须支持禁配规则：

- 举报后隔离
- 拉黑
- 管理员手工禁配

---

## 12. 评估指标

校园匹配算法不能只看离线相似度。

建议分三层指标：

### 12.1 过程指标

- 问卷完成率
- 当前周期 opt-in 率
- 候选覆盖率
- 实际匹配率
- 平均候选边数量

### 12.2 关系建立指标

- 打招呼发送率
- 双向打招呼率
- 首周回复率
- 微信号填写率
- 微信号互惠解锁率

### 12.3 质量指标

- 匹配后满意度
- 匹配后次周留存
- 报告点击率
- 举报率
- “宁愿不匹配”的触发比例

### 12.4 离线评估

如果后续积累了行为数据，可以回头做：

- 互发招呼作为正反馈标签
- 回复/交换微信作为更强正反馈
- 基于历史 pair 的 AUC / PR / calibration

但在冷启动阶段，不建议等有监督学习再上线，规则系统先跑最合理。

---

## 13. 推荐的算法迭代路线

### Phase 1：规则系统

特征：

- 双边硬过滤
- 人工权重
- 偏好满足 + 相似度混合打分
- 最大权匹配
- 模板化报告

这是最适合当前代码库与数据阶段的方案。

### Phase 2：权重校准

基于真实行为反馈，调优：

- 各模块权重
- 重要题乘数
- 阈值
- 类别题兼容矩阵

### Phase 3：学习排序

当积累足够反馈后，可考虑：

- pairwise learning to rank
- representation learning
- report 文案生成增强

但前提是：

- 问卷 schema 稳定
- 周期数据量足够
- 标签质量足够

---

## 14. 与后端的数据接口约定

算法服务或算法模块的最小输入建议是：

```json
{
  "cycleId": "2026w14",
  "algorithmVersion": "v1.0.0",
  "participants": [
    {
      "userId": "u_123",
      "hardFilters": {},
      "features": {},
      "preferences": {},
      "displayFeatures": {}
    }
  ]
}
```

最小输出建议是：

```json
{
  "cycleId": "2026w14",
  "algorithmVersion": "v1.0.0",
  "matches": [
    {
      "userA": "u_123",
      "userB": "u_456",
      "scoreTotal": 0.86,
      "scoreBreakdown": {},
      "reasons": [],
      "reportPayload": {}
    }
  ],
  "unmatched": [
    {
      "userId": "u_789",
      "reason": "below_threshold"
    }
  ]
}
```

---

## 15. 给算法设计同学的结论

当前问卷设计最有价值的，不是题目数量多，而是三点：

- 有双轨题，能做“我想要什么”与“你是什么样”的双边拟合
- 有重要题，能让用户主动告诉算法权重
- 有兴趣/特质/季节题，能支撑报告解释与破冰

所以第一版最合理的策略不是复杂模型，而是：

**双边硬过滤 + 加权兼容打分 + 最大权匹配 + 结构化解释生成。**

只要把这一版做好，就已经能明显超过“只看相似度”的校园匹配系统，并且和当前前端原型的产品叙事完全对齐。
