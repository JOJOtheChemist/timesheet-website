# 项目文件结构设计

## 📁 推荐的项目结构

```
project-root/
├── 📁 frontend/                    # 前端代码
│   ├── 📁 components/              # 组件库
│   │   ├── 📁 ui/                  # 基础UI组件
│   │   │   ├── 📁 button/
│   │   │   │   ├── button.css
│   │   │   │   ├── button.js
│   │   │   │   └── README.md
│   │   │   ├── 📁 modal/
│   │   │   │   ├── modal.css
│   │   │   │   ├── modal.js
│   │   │   │   └── README.md
│   │   │   └── 📁 form/
│   │   │       ├── form.css
│   │   │       ├── form.js
│   │   │       └── README.md
│   │   ├── 📁 business/            # 业务组件
│   │   │   ├── 📁 background-switcher/
│   │   │   │   ├── background-switcher.css
│   │   │   │   ├── background-switcher.js
│   │   │   │   ├── background-switcher.html
│   │   │   │   └── README.md
│   │   │   ├── 📁 schedule-table/
│   │   │   │   ├── schedule-table.css
│   │   │   │   ├── schedule-table.js
│   │   │   │   ├── schedule-table.html
│   │   │   │   └── README.md
│   │   │   └── 📁 data-chart/
│   │   │       ├── data-chart.css
│   │   │       ├── data-chart.js
│   │   │       └── README.md
│   │   └── 📁 api/                 # API相关组件
│   │       ├── 📁 api-client/
│   │       │   ├── api-client.js
│   │       │   ├── api-config.js
│   │       │   └── README.md
│   │       ├── 📁 data-fetcher/
│   │       │   ├── data-fetcher.js
│   │       │   └── README.md
│   │       └── 📁 cache-manager/
│   │           ├── cache-manager.js
│   │           └── README.md
│   ├── 📁 pages/                   # 页面
│   │   ├── daily-schedule.html
│   │   ├── weekly-report.html
│   │   └── settings.html
│   ├── 📁 assets/                  # 静态资源
│   │   ├── 📁 images/
│   │   ├── 📁 icons/
│   │   └── 📁 fonts/
│   ├── 📁 styles/                  # 全局样式
│   │   ├── global.css
│   │   ├── variables.css
│   │   └── utilities.css
│   ├── 📁 scripts/                 # 全局脚本
│   │   ├── app.js
│   │   ├── router.js
│   │   └── utils.js
│   └── 📁 vendor/                  # 第三方库
│       ├── jquery.min.js
│       └── bootstrap.css
├── 📁 backend/                     # 后端代码
│   ├── c
│   ├── 📁 core/                    # 核心配置
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── 📁 models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── schedule.py
│   │   └── user.py
│   ├── 📁 services/                # 业务服务
│   │   ├── __init__.py
│   │   ├── schedule_service.py
│   │   └── user_service.py
│   ├── 📁 utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── validators.py
│   ├── main.py                     # 应用入口
│   ├── requirements.txt            # 依赖
│   └── Dockerfile                  # 容器配置
├── 📁 docs/                        # 文档
│   ├── api-docs.md
│   ├── component-docs.md
│   └── deployment.md
├── 📁 tests/                       # 测试
│   ├── 📁 frontend/
│   │   ├── unit/
│   │   └── integration/
│   └── 📁 backend/
│       ├── unit/
│       └── integration/
├── 📁 scripts/                     # 构建脚本
│   ├── build.sh
│   ├── deploy.sh
│   └── test.sh
├── package.json                    # 前端依赖
├── requirements.txt                # 后端依赖
├── docker-compose.yml              # 容器编排
├── .gitignore
├── README.md
└── .env.example                    # 环境变量示例
```

## 🎯 组件分类说明

### 1. UI组件 (基础组件)
- **特点**: 纯展示，无业务逻辑
- **示例**: Button, Modal, Form, Input
- **复用性**: 极高，可在任何项目中使用

### 2. 业务组件 (功能组件)
- **特点**: 包含特定业务逻辑
- **示例**: BackgroundSwitcher, ScheduleTable
- **复用性**: 中等，可在相似业务中复用

### 3. API组件 (数据组件)
- **特点**: 处理数据获取、缓存、状态管理
- **示例**: ApiClient, DataFetcher, CacheManager
- **复用性**: 高，可在需要相同API的项目中复用

## 🔧 组件开发规范

### 命名规范
```
组件名: kebab-case (background-switcher)
类名: PascalCase (BackgroundSwitcher)
文件名: kebab-case (background-switcher.js)
CSS类名: BEM方法 (background-switcher__button)
```

### 文件结构
```
component-name/
├── component-name.js      # 主要逻辑
├── component-name.css     # 样式
├── component-name.html    # 示例/模板
├── component-name.test.js # 测试文件
└── README.md             # 文档
``` 