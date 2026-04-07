# CSU-Date

中南大学校园 Date Drop 平台。产品核心理念是：

**不刷屏，每周只遇见一个人，然后认真了解 TA。**

本项目包含前端静态原型和后端服务实现，提供完整的用户流程体验，包括问卷填写、匹配算法、报告生成和消息系统。

## 项目现状

### 前端原型
当前前端实现已经覆盖：

- 首页 Landing Page
- 登录 / 注册页
- 7 模块完整版问卷
- 用户仪表盘
- 本周匹配报告页
- 打招呼页
- 信箱页
- 个人主页
- ……

### 后端服务
后端实现包括：

- 用户注册和登录（支持邮箱验证码）
- 数据库持久化（SQLite/PostgreSQL）
- 精确匹配引擎（基于问卷答案和权重）
- 邮件服务（注册验证码、匹配通知）
- LLM 报告生成（契合度分析、维度分析）
- 消息系统（打招呼、信箱管理）
- 批处理匹配任务

## 功能说明

### 核心功能
- **问卷系统**：7 模块完整问卷，包括基本信息、人生观、性格价值观、生活方式、亲密关系观、兴趣爱好、外貌气质
- **匹配算法**：每周精确匹配一人，基于问卷权重和兼容性计算
- **报告生成**：AI 生成的个性化匹配报告，包括契合度、共同点、互补点
- **消息系统**：打招呼、双向匹配、过期消息管理
- **用户管理**：资料完善、暂停匹配、统计信息

### 技术特性
- **前端**：纯静态 HTML/CSS/JS，无框架依赖
- **后端**：FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **匹配引擎**：自定义精确匹配算法，支持权重和多维度评分
- **报告生成**：集成 LLM（GPT）生成叙事化报告
- **邮件服务**：SMTP 邮件发送，支持验证码和通知

## Linux 系统部署

### 环境要求
- Ubuntu/Debian Linux
- Python 3.9+
- Nginx
- systemd

### 一键部署
在服务器上克隆仓库后，执行部署脚本：

```bash
cd /opt/csudate
# 注意：请先编辑 deploy.sh 中的 DOMAIN 变量，设置为您的域名
sudo bash deploy.sh
```

部署脚本将自动：
1. 安装系统依赖（Python, Nginx, Certbot）
2. 创建 Python 虚拟环境并安装依赖
3. 初始化数据库
4. 配置 systemd 服务（后端运行在 127.0.0.1:8888）
5. 配置 Nginx（前端静态文件 + API 反代）
6. 设置防火墙
7. 申请 SSL 证书

### 手动部署步骤
如果需要手动部署：

1. **安装依赖**：
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx
   ```

2. **后端设置**：
   ```bash
   cd csu-datedrop-backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
   ```

3. **运行后端**：
   ```bash
   # 开发模式
   uvicorn main:app --reload --host 0.0.0.0 --port 8888

   # 生产模式（使用 systemd）
   sudo systemctl enable csudate
   sudo systemctl start csudate
   ```

4. **前端部署**：
   将 `stitch/` 目录静态文件部署到 Nginx 或其他 Web 服务器。

5. **Nginx 配置**：
   配置反代到后端 API：
   ```
   location /api/ {
       proxy_pass http://127.0.0.1:8888;
   }
   ```

## 调试方法

### 后端调试
- **查看日志**：
  ```bash
  sudo journalctl -u csudate -f
  ```

- **重启服务**：
  ```bash
  sudo systemctl restart csudate
  ```

- **测试 API**：
  ```bash
  curl http://127.0.0.1:8888/api/stats
  ```

- **数据库检查**：
  ```bash
  sqlite3 csu-datedrop-backend/datedrop.db
  ```

- **运行测试**：
  ```bash
  cd csu-datedrop-backend
  source venv/bin/activate
  python batch_test.py
  ```

### 前后端联调
为了在本地同时调试前后端，确保它们能正确交互：

1. **检查端口冲突**（如果之前运行过部署脚本）：
   ```bash
   sudo systemctl stop csudate  # 停止生产服务
   # 或检查进程：lsof -i :8888 或 netstat -tlnp | grep :8888
   # 如有冲突，杀死进程：sudo kill -9 <PID>
   ```

2. **启动后端**（在新终端）：
   ```bash
   cd csu-datedrop-backend
   source venv/bin/activate
   uvicorn main:app --reload --host 127.0.0.1 --port 8888
   ```

3. **启动前端**（在另一个终端）：
   ```bash
   cd stitch
   npx serve .
   ```

4. **访问前端**：打开 `http://localhost:3000/index.html`

前端会自动调用后端 API（默认 `http://127.0.0.1:8888`），支持热重载调试。后端已配置 CORS，允许跨域请求。

如果需要自定义 API 地址，在浏览器控制台运行：
```javascript
localStorage.setItem('csudate_api_base', 'http://your-custom-url:port');
```

### 常见问题
- **后端启动失败**：检查端口 8888 是否被占用，查看 systemd 日志
- **API 调用失败**：确认 Nginx 配置正确，后端服务运行正常
- **邮件发送失败**：检查 SMTP 配置和网络连接
- **匹配算法问题**：运行 `example_usage_precision_engine.py` 测试匹配逻辑

## 体验流程

1. 访问首页 `index.html`
2. 注册/登录（支持邮箱验证码）
3. 完成 7 模块问卷
4. 查看仪表盘和匹配报告
5. 发送消息和查看信箱

## 技术栈

- **前端**：HTML5, CSS3, JavaScript (ES6+)
- **后端**：FastAPI, SQLAlchemy, Uvicorn
- **数据库**：SQLite (开发) / PostgreSQL (生产)
- **邮件**：smtplib / Resend 服务
- **AI**：OpenAI GPT API
- **部署**：Nginx, systemd, Certbot

## 仓库结构

```
csudate/
├── stitch/                            # 前端静态原型
│   ├── index.html                     # 首页
│   ├── login.html                     # 登录页面
│   ├── dashboard.html                 # 匹配页面
│   ├── greet.html                     # 打招呼页
│   ├── inbox.html                     # 信箱页
│   ├── profile.html                   # 用户仪表盘
│   ├── report.html                    # 匹配报告页
│   └── ...
├── csu-datedrop-backend/              # 后端服务
│   ├── main.py                        # FastAPI 应用入口
│   ├── database.py                    # 数据库配置
│   ├── models.py                      # 数据模型
│   ├── schemas.py                     # Pydantic 模式
│   ├── email_service.py               # 邮件服务
│   ├── matcher_service.py             # 匹配服务
│   ├── precision_matching_engine.py   # 匹配引擎
│   ├── llm_report.py                  # LLM 报告生成
│   ├── requirements.txt               # Python 依赖
│   └── ...
├── deploy.sh                          # 一键部署脚本
└── README.md
```

## 配套文档

- `DESIGN.md` - 设计系统说明
- `BACKEND_HANDOFF.md` - 后端设计文档
- `ALGORITHM_DESIGN_HANDOFF.md` - 算法设计文档

## 当前限制

尽管后端核心功能已实现，但在投入生产环境前仍需注意以下限制和优化空间：

- **前端交互细节**：部分前端页面仍保留原型阶段的硬编码数据或模拟逻辑，需进一步与后端 API 深度集成以确保数据实时性。
- **并发与性能**：当前的匹配算法和 LLM 报告生成为同步或基础异步实现，在高并发场景下可能需要引入任务队列（如 Celery/RQ）进行解耦。
- **安全性加固**：虽然实现了基础的身份验证，但生产环境需进一步加固 JWT 策略、速率限制（Rate Limiting）及敏感数据加密存储。
- **问卷版本管理**：目前问卷结构相对固定，未来若需调整问卷题目，需完善版本迁移和数据兼容机制。
- **测试覆盖**：单元测试和集成测试覆盖率有待提升，特别是匹配算法的边缘情况测试。

## 下一步建议

为了将本项目推进为稳定可用的生产级产品，建议优先执行以下任务：

1. **前端重构与联调**：
   - 清理前端 `localStorage` 模拟逻辑，全面对接后端 RESTful API。
   - 优化用户体验（UX），增加加载状态、错误提示和表单验证反馈。

2. **异步任务队列集成**：
   - 引入 Redis + Celery/RQ，将耗时的 LLM 报告生成和批量匹配任务移至后台异步执行，提升 API 响应速度。

3. **安全与运维增强**：
   - 配置完善的 HTTPS 强制跳转、HSTS 及安全头信息。
   - 实施更严格的输入验证和 SQL 注入防护。
   - 设置自动化备份策略用于数据库（尤其是 PostgreSQL 生产库）。

4. **监控与日志系统**：
   - 集成结构化日志（如 JSON 格式）并接入监控平台（如 Prometheus/Grafana 或 Sentry），以便追踪错误和性能瓶颈。

5. **功能迭代**：
   - 实现更灵活的问卷版本管理系统。
   - 优化匹配算法的可解释性，为用户提供更直观的匹配理由。
   - 完善消息系统的实时性（可选：引入 WebSocket 支持实时聊天）。

6. **文档与合规**：
   - 补充详细的 API 文档（Swagger/OpenAPI 已自动生成，需补充业务层面说明）。
   - 完善用户隐私协议和数据删除机制，符合相关法律法规要求。

## 说明

本项目为学生自主开发原型，非学校官方项目。
