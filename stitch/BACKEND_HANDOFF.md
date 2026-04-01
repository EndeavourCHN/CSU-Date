# CSU Date 后端交接文档

更新时间：2026-04-01

## 1. 文档目的

这份文档面向后端开发。它基于当前仓库的全部代码与需求文档梳理：

- 前端原型当前已经表达出的业务流程
- 现在哪些逻辑只是前端假实现
- 后端真正需要承接的数据模型、接口、调度和状态机
- 当前代码中的不一致、风险和上线前必须补齐的部分

一句话结论：

**当前仓库是一个高保真静态原型，不是已接后端的产品。所有业务状态几乎都存在 `localStorage`，匹配、消息、报告、验证码、邮箱、周更调度都还没有服务端实现。**

---

## 2. 审阅范围

本次已审阅以下文件：

- `index.html`
- `login.html`
- `dashboard.html`
- `greet.html`
- `inbox.html`
- `profile.html`
- `report.html`
- `README.md`
- `DESIGN.md`
- `datedrop-frontend-prompt.md`
- `csu-datedrop-improvement-prompt.md`
- `csu-datedrop-improvement-prompt2.md`
- `csu-datedrop-full-questionnaire-prompt.md`
- `vercel.json`

---

## 3. 代码库现状总结

### 3.1 技术形态

当前项目不是前后端分离应用，也不是 SSR 项目，而是多页面静态 HTML 原型：

- 页面之间通过 `*.html` 跳转
- 所有交互逻辑由页面内联 JavaScript 完成
- 所有用户态靠浏览器 `localStorage`
- 没有任何真实 API 调用
- 没有数据库
- 没有鉴权中间件
- 没有任务调度
- 没有邮件/短信/消息基础设施

### 3.2 仓库和文档存在版本漂移

需要注意，仓库里存在明显的“实现已演进，文档未同步”的情况：

- `README.md` 仍写着“全部代码在 `code.html` 一个文件中”
- 实际仓库已经拆成 `index.html`、`login.html`、`dashboard.html` 等多个页面
- `README.md` 中问卷数据结构仍是简版 3 步问卷
- 实际 `index.html` 已经实现为 7 模块完整版问卷

这意味着后端不能只按 `README.md` 理解需求，必须以当前页面代码和完整版 prompt 为准。

---

## 4. 页面级业务流

### 4.1 `index.html`

承担两个角色：

- Landing page
- 7 模块问卷页

Landing page 表达的业务信息：

- 产品定位：中南大学校园匹配平台
- 节奏：每周四匹配
- 入口：开始匹配
- 目标用户：需要登录后填写问卷

问卷页表达的业务信息：

- 问卷共 7 个模块
- 模块 1 为硬过滤基础信息
- 模块 2-7 包含 Likert 量表、单双轨偏好题、兴趣、多选特质
- 支持“设为重要”加权
- 完成后跳转仪表盘

当前前端提交行为：

- 将问卷整体写入 `localStorage.csudate_quiz`
- 将 `csudate_user.quizCompleted` 设为 `true`
- 不做服务端落库

### 4.2 `login.html`

承担登录与注册两种模式。

当前实现是纯模拟：

- 注册验证码是前端随机生成 6 位数字
- “发送验证码”只在控制台打印，不会真正发送邮件
- 登录时没有密码校验
- 存在两个演示账号：
  - `test / test`
  - `test2 / test`
- 成功后把用户对象直接写入 `localStorage.csudate_user`

这说明当前页面更多是在模拟“登录后系统长什么样”，并没有真实身份体系。

### 4.3 `dashboard.html`

这是用户仪表盘。当前页面表达出的核心业务包括：

- 个人欢迎区
- 累计匹配统计
- 本周匹配结果
- 匹配历史
- 匹配洞察
- 下次匹配倒计时
- `Shoot Your Shot`

但其中绝大部分是静态展示或 demo 逻辑：

- 本周匹配对象是固定文案
- 匹配历史固定
- 洞察固定
- 倒计时是真实本地时间计算，但不依赖服务端周期状态
- `weeklyMatch !== false` 就默认有匹配，是前端 demo shortcut

### 4.4 `report.html`

这是匹配报告页。

当前页面表达出的业务需求非常重要：

- 后端/算法最终要给前端一份“结构化可解释报告”
- 报告至少包括：
  - 总契合度
  - 分维度契合度
  - 共同点
  - 互补点
  - 一段匹配叙事

但当前所有数据都是硬编码：

- 总分固定 `86%`
- 各维度固定
- 共性/差异/叙事都是写死文本

### 4.5 `greet.html`

这是“打个招呼”页。

当前前端表达出的消息规则：

- 用户给本周匹配对象发一条 200 字以内的招呼消息
- 只有对方也打招呼后，双方才可见消息
- 发送后跳到“已送出”状态

当前实现问题：

- 消息没有落库
- 发送后不会出现在真实消息列表中
- 页面切换后状态丢失

### 4.6 `inbox.html`

这是信箱页。

当前页面表达出的消息状态机：

- `mutual`: 双向打招呼成功
- `waiting`: 我发了，对方未发
- `expired`: 周期结束未形成双向

另一个很关键的业务规则是微信号披露：

- 双方都填微信时，可显示对方微信
- 对方填了、我没填时，不给我看，提示先补自己的微信
- 我填了、对方没填时，提示对方暂未分享
- 双方都没填时，提示双方均未分享

这说明产品希望联系方式交换是“互惠解锁”，而不是单边查看。

### 4.7 `profile.html`

这是个人页。

当前页面表达出的业务包括：

- 基本资料展示
- 价值观标签展示
- 微信号填写/修改/清除
- 账户设置入口
- 暂停匹配
- 退出登录

当前限制：

- 价值观不是从问卷实时映射，而是依赖 `user.values`
- 只有微信号和暂停状态被实际写回 `localStorage`
- 编辑资料、通知设置、偏好设置都还只是占位

---

## 5. 当前前端状态模型

### 5.1 `localStorage.csudate_user`

当前前端的用户状态是一个松散对象，不同页面会读写不同字段。综合代码后，实际可能出现的字段如下：

```ts
interface FrontendUserState {
  id: string;
  email: string;
  name: string;
  campus: string;
  grade: string;
  major: string;
  bio: string;
  values: string[];
  wechat?: string;

  stats?: {
    matches: number;
    bestScore: number;
    weeks: number;
  };

  loggedIn: boolean;
  loginTime: number;

  quizCompleted: boolean;
  quizCompletedAt?: number;

  weeklyMatch?: boolean;
  paused?: boolean;
}
```

问题：

- 这是 UI 状态，不是稳定的后端领域模型
- 统计字段、匹配字段和用户主资料混在一起
- 没有 schema version
- 没有更新时间
- 没有服务端真值来源

### 5.2 `localStorage.csudate_quiz`

当前问卷存储结构如下：

```ts
interface FrontendQuizStorage {
  responses: FullQuestionnaireLike;
  importance: Record<string, boolean>;
  completedAt: number;
}
```

其中 `responses` 基本等同于一个完整版问卷对象，包含：

- `school`
- `gender`
- `sexuality`
- `grade`
- `campus`
- `college`
- `height`
- `heightPrefMin`
- `heightPrefMax`
- `hometown`
- `crossCampus`
- `sameCollege`
- `likert`
- `spending`
- `diet`
- `studyspot`
- `meet_freq`
- `interests`
- `selfTraits`
- `partnerTraits`
- `partnerTraitsImportant`
- `seasonal`

问题：

- `importance` 与 `likert[key].important` 存在重复表达
- 后端不应直接照搬浏览器结构落库
- 问卷没有版本号和题目 schema 版本

---

## 6. 从前端原型可推导出的后端核心领域

后端至少需要承接以下领域：

1. 用户与身份验证
2. 学校邮箱验证码发送与校验
3. 用户主资料
4. 问卷版本管理与问卷提交
5. 每周匹配周期
6. 用户每周参与状态（opt-in / pause / 已匹配 / 未参与）
7. 匹配结果与匹配报告
8. 打招呼消息与信箱
9. 联系方式互惠解锁
10. `Shoot Your Shot`
11. 邮件/站内通知
12. 风控、申诉、审计

---

## 7. 推荐后端领域模型

以下不是唯一方案，但基本满足当前原型和未来演进。

### 7.1 用户与身份

#### `users`

- `id`
- `school`
- `student_no`
- `email`
- `email_domain`
- `password_hash`
- `status`：`active / disabled / banned`
- `is_verified`
- `created_at`
- `updated_at`

#### `user_profiles`

- `user_id`
- `display_name`
- `campus`
- `grade`
- `major`
- `college`
- `bio`
- `avatar_url`
- `wechat_id`
- `wechat_visibility_mode`
- `paused`
- `paused_at`
- `updated_at`

#### `email_verification_codes`

- `id`
- `email`
- `code_hash`
- `purpose`：`register / login / reset_password`
- `expires_at`
- `consumed_at`
- `send_ip`
- `attempt_count`

### 7.2 问卷

#### `questionnaire_versions`

- `id`
- `version_code`
- `title`
- `status`：`draft / active / retired`
- `schema_json`
- `created_at`

#### `questionnaire_submissions`

- `id`
- `user_id`
- `questionnaire_version_id`
- `answers_json`
- `normalized_features_json`
- `completed_at`
- `is_current`

建议：

- 原始答案与归一化特征分开存
- 要支持问卷升级后重新计算特征

### 7.3 匹配周期

#### `match_cycles`

- `id`
- `cycle_code`
- `school_scope`
- `questionnaire_version_id`
- `signup_deadline_at`
- `freeze_at`
- `match_run_at`
- `reveal_at`
- `status`：`upcoming / open / frozen / matching / revealed / closed`

#### `cycle_participations`

- `id`
- `cycle_id`
- `user_id`
- `status`：`opted_in / opted_out / paused / matched / unmatched / skipped`
- `source`：`manual / auto_optin / carry_over`
- `questionnaire_submission_id`
- `created_at`
- `updated_at`

### 7.4 匹配结果

#### `matches`

- `id`
- `cycle_id`
- `user_a_id`
- `user_b_id`
- `score_total`
- `score_breakdown_json`
- `algorithm_version`
- `status`：`revealed / expired / archived / blocked`
- `revealed_at`

#### `match_reports`

- `id`
- `match_id`
- `report_json`
- `generated_by`
- `generated_at`

`report_json` 建议至少包含：

- `overall_score`
- `dimension_scores`
- `shared_points`
- `complementary_points`
- `narrative`
- `ice_breakers`
- `seasonal_hook`

### 7.5 消息与互惠解锁

#### `match_greetings`

- `id`
- `match_id`
- `sender_user_id`
- `content`
- `sent_at`
- `status`：`visible / pending_reciprocal / expired`

#### `contact_reveal_states`

- `id`
- `match_id`
- `channel`：`wechat`
- `user_a_shared`
- `user_b_shared`
- `user_a_can_view`
- `user_b_can_view`
- `updated_at`

### 7.6 Shoot Your Shot

#### `shoot_requests`

- `id`
- `cycle_id`
- `sender_user_id`
- `target_email`
- `target_user_id`
- `message`
- `status`：`pending / reciprocal / expired / invalid_target / rate_limited`
- `created_at`

### 7.7 通知

#### `notification_jobs`

- `id`
- `user_id`
- `type`
- `channel`：`email / in_app`
- `payload_json`
- `scheduled_at`
- `sent_at`
- `status`

---

## 8. 推荐 API 边界

以下按前端页面需求逆推。

### 8.1 认证

#### `POST /api/auth/send-code`

用途：

- 注册验证码
- 登录验证码
- 找回密码验证码

请求：

```json
{
  "email": "8209190101@csu.edu.cn",
  "purpose": "register"
}
```

#### `POST /api/auth/register`

请求：

```json
{
  "email": "8209190101@csu.edu.cn",
  "code": "123456",
  "password": "plain-text-from-client",
  "displayName": "林晓霜",
  "campus": "岳麓山校区",
  "grade": "大三",
  "major": "计算机科学与技术"
}
```

#### `POST /api/auth/login`

支持密码登录，必要时后续可扩展邮箱验证码登录。

#### `POST /api/auth/logout`

#### `GET /api/me`

返回前端组装 dashboard/profile 所需的当前用户视图。

### 8.2 问卷

#### `GET /api/questionnaire/current`

返回当前激活问卷 schema 和版本号。

#### `POST /api/questionnaire/submissions`

提交当前问卷答案。

建议请求体：

```json
{
  "questionnaireVersion": "csu-v1-full",
  "answers": {
    "...": "..."
  }
}
```

#### `GET /api/questionnaire/me/latest`

取用户最近一次有效问卷，用于“重填问卷”和资料回显。

### 8.3 周期参与

#### `GET /api/cycles/current`

返回：

- 当前周期状态
- 截止时间
- 是否可 opt-in
- 是否已参与
- 是否已揭晓

#### `POST /api/cycles/current/opt-in`

#### `POST /api/cycles/current/opt-out`

### 8.4 仪表盘

#### `GET /api/dashboard`

建议由后端聚合返回：

- `userSummary`
- `stats`
- `currentCycle`
- `currentMatchPreview`
- `historyPreview`
- `insights`
- `shootQuota`

### 8.5 匹配与报告

#### `GET /api/matches/current`

#### `GET /api/matches/history`

#### `GET /api/matches/{matchId}/report`

### 8.6 打招呼与信箱

#### `POST /api/matches/{matchId}/greetings`

#### `GET /api/inbox`

返回消息列表及其状态：

- 双向成功
- 等待回应
- 过期

#### `GET /api/inbox/{threadId}`

如未来引入更长对话，可扩展为 thread 模型。

### 8.7 个人资料与设置

#### `PATCH /api/profile`

#### `PATCH /api/profile/wechat`

#### `POST /api/profile/pause`

#### `POST /api/profile/resume`

### 8.8 Shoot Your Shot

#### `POST /api/shoot`

#### `GET /api/shoot/quota`

---

## 9. 关键业务规则

### 9.1 学校身份验证

前端所有文案都假设只有中南学生能注册，但现在并未真正验证。

生产规则建议：

- 仅允许 `@csu.edu.cn` 和 `@mail.csu.edu.cn`
- 同一学号/邮箱只能绑定一个有效账号
- 验证码要限频、限 IP、限设备

### 9.2 问卷版本化

当前问卷已经是完整版，后续必然会改题。

因此后端必须支持：

- 同时保留历史提交
- 标记当前生效问卷
- 旧版本答案可回溯
- 新版本上线后重新归一化特征

### 9.3 匹配周期真值必须在服务端

现在前端只会按本地时间算“下一个周四 21:00”。这不够。

服务端需要作为唯一真值管理：

- 当前周期 ID
- opt-in 截止时间
- 冻结时间
- 算法跑批时间
- 揭晓时间

### 9.4 用户是否进入匹配池

只有同时满足下列条件的用户才应进入候选池：

- 已验证邮箱
- 已完成问卷
- 当前未暂停
- 当前周期已 opt-in
- 当前没有被封禁
- 当前问卷版本有效

### 9.5 消息可见性

当前原型明确表达了：

- 单边打招呼后，消息不直接公开
- 只有双方都发过招呼，双方才能看到完整内容

这个规则需要后端在消息读取 API 层执行，而不是只靠前端控制展示。

### 9.6 微信号互惠解锁

当前原型表达的不是“只要对方填了我就能看”，而是：

- 只有我也分享了微信，才解锁查看对方微信

这意味着联系方式查看权限也必须由后端计算。

### 9.7 Shoot Your Shot

前端文案给出的规则是：

- 对方也 shoot 了你才触发
- 否则静默失败
- 每月限一次

这类规则必须服务端落地，不能相信前端。

---

## 10. 当前代码中的主要缺口与风险

### 10.1 登录注册是假的

- 验证码不发邮件
- 登录密码不校验
- 账号状态只存在本地
- demo 账号绕过真实认证

### 10.2 匹配是假的

- 没有候选池
- 没有跑批
- 没有分数计算
- `weeklyMatch` 字段只决定展示哪张卡片

### 10.3 报告是假的

- `report.html` 完全硬编码
- 无法根据真实问卷生成

### 10.4 信箱是假的

- `greet.html` 发送不落库
- `inbox.html` 列表是写死的
- 双向可见规则只是一层 UI 表达

### 10.5 问卷提交没有后端约束

- 无服务端参数校验
- 无版本号
- 无幂等提交保护
- 无 draft/正式提交区分

### 10.6 多页面之间数据并不一致

例如：

- Profile 页展示的价值观来源于 `user.values`
- 问卷真实答案存放在 `csudate_quiz.responses`
- 两者目前没有同步机制

也就是说，即使前端本地看起来能跑，页面之间的数据语义也并未统一。

### 10.7 域名规则与表单不完全一致

代码中的“学校邮箱”输入方式是：

- 用户输入学号
- 前端再拼接 `@csu.edu.cn`

但文档又写支持 `@mail.csu.edu.cn`。这在后端设计时要统一。

---

## 11. 建议后端架构拆分

如果团队规模不大，建议先做单体服务，但按领域分模块：

- `auth`
- `user-profile`
- `questionnaire`
- `cycle`
- `matching`
- `report`
- `messaging`
- `notification`
- `admin`

如果后续规模扩大，再拆服务。

基础设施建议：

- 应用服务：Node.js / Go / Java 任一熟悉栈均可
- DB：PostgreSQL
- 缓存：Redis
- 异步任务：Redis Queue / RabbitMQ / Kafka 任选一
- 定时任务：Cron + queue worker
- 文件存储：对象存储，用于头像和导出报告

---

## 12. 推荐上线顺序

### Phase 1：可闭环 MVP

目标：真实注册、真实问卷、真实每周匹配、真实揭晓。

必须包含：

- 邮箱验证码注册登录
- 问卷提交与版本化
- 周期管理
- 规则匹配/基础打分
- 仪表盘真实数据
- 报告生成

### Phase 2：关系建立闭环

- 打招呼消息落库
- 双向可见
- 信箱真实化
- 微信号互惠解锁

### Phase 3：高级功能

- Shoot Your Shot
- 通知设置
- 管理后台
- 风控与举报
- 长沙高校扩校

---

## 13. 后端启动前必须先和产品/算法对齐的问题

以下问题在当前原型中并未完全收敛，后端需要尽早拉齐：

1. 周期规则的唯一版本到底是什么？
   - 文案稳定出现“周四 21:00 揭晓”
   - 但“opt-in 截止时间”“修改截止时间”在不同文档里还不完全一致

2. `sameCollege` 是硬过滤还是软偏好？
   - 当前前端文案像偏好
   - 但算法文档可将其视为硬过滤

3. `diet` 是否进入硬过滤？
   - 完整 prompt 中建议作为硬过滤
   - 当前前端只是普通单选题

4. `Shoot Your Shot` 是立即触发匹配，还是优先进入下一周期？

5. 微信号是否只在双向打招呼成功后才有资格进入解锁流程？

6. 一个周期里未匹配到的人，下周期是否自动继承参与状态？

---

## 14. 给后端的结论

不要把当前仓库当成“只差接接口”的前端成品。它更准确地说是：

**一套已经把产品叙事、主要页面、问卷结构和部分业务规则表达清楚的静态原型。**

后端真正需要做的不是“把 localStorage 搬到数据库”，而是：

- 定义稳定的领域模型
- 把周期、匹配、消息、联系方式解锁这些核心状态收归服务端
- 形成可供前端消费的聚合视图 API
- 给算法提供稳定、可版本化的数据输入和产出落点

如果按本文档拆分，后端可以先把“认证 + 问卷 + 周期 + 匹配 + 报告”打通，再处理消息与高级玩法。
