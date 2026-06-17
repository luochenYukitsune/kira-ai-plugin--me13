# δ-me13.exe — 翁法罗斯模拟世界控制台

**δ-me13** 是一个科幻主题的 LLM 驱动的多智能体模拟世界控制台，同时也是 **KiraAI** 平台的功能插件。它融合了沉浸式科幻 UI、AI Agent 模拟系统与 KiraAI 管理面板，构建出一个虚实交织的交互体验。

---

## 项目架构

```
delta-me13-main/
├── me13/               # Vue 3 + TypeScript 前端 SPA
│   └── src/
│       ├── components/    # UI 组件（科幻风格）
│       ├── core/          # 模拟核心（Agent 系统、世界状态、记忆系统）
│       ├── stores/        # Pinia 状态管理
│       ├── api/           # KiraAI 后端 API 客户端
│       ├── views/         # KiraAI 管理视图
│       ├── services/      # 通信与通知服务
│       └── i18n/          # 国际化（中/英）
├── me13-plugin/        # KiraAI 插件（Python）
│   ├── main.py            # 插件入口：页面注册、Omphalos 工具
│   ├── manifest.json      # 插件清单
│   └── schema.json        # 插件配置字段定义
└── KiraAI-2.23.0/      # KiraAI 后端参考副本
```

---

## 核心功能

### 🎮 翁法罗斯模拟世界

LLM 驱动的多智能体（Multi-Agent）文明模拟系统：

- **12 位黄金裔** — 各自拥有独特命途、原动力和背景故事，在翁法罗斯世界中自主决策
- **12 位泰坦** — 各守护一枚火种，是世界封印的核心
- **10+ NPC** — 商人、守卫、学者等，构成丰富的社交生态
- **世界引擎** — 每日循环驱动：智能体决策 → LLM 调用 → 状态变更 → 事件触发
- **记忆系统** — 短期记忆（缓冲区）+ 长期记忆（向量存储），实现上下文感知推理
- **20+ 行动类型** — 移动、对话、交易、战斗、建造、净化等

### 🤖 KiraAI 集成

作为 KiraAI 插件嵌入平台生态：

- **插件注册** — 以 `me13_plugin` 身份注册到 KiraAI 侧边栏
- **管理面板** — 概览、模型提供商、适配器、人设、插件、贴纸、配置、会话、日志、设置
- **Bot 工具** — 5 个 Omphalos 交互工具（状态查询、移动、探索、对话、推进时间），LLM 可直接调用
- **插件配置** — 通过 KiraAI 插件配置界面管理 LLM 连接与显示选项
- **独立运行** — 也支持独立模式，通过菜单中的"KiraAI管理→连接配置"手动连接

### ✏️ 可视化文案编辑

所有用户可见文本均可直接编辑：

- **点击编辑** — 双击或点击图标即可编辑标题、状态、文件夹名、文件名
- **实时保存** — 修改自动持久化到 `localStorage`，刷新后保留
- **一键恢复** — 恢复默认文案

### 🎨 科幻主题 UI

- 动态粒子背景与扫描线效果
- 加载封面动画
- 全息风格面板与 3D 变换交互
- 背景音乐（BGM）
- 全响应式布局

---

## 技术栈

| 层 | 技术 |
|---|---|
| **前端框架** | Vue 3 (Composition API + `<script setup>`) |
| **语言** | TypeScript |
| **状态管理** | Pinia |
| **构建工具** | Vite 5 |
| **UI 组件** | Element Plus |
| **图标** | lucide-vue-next, @element-plus/icons-vue |
| **AI SDK** | OpenAI SDK (browser mode) |
| **插件后端** | Python (KiraAI BasePlugin) |
| **样式** | 自定义 CSS (科幻主题) |

---

## 快速开始

### 前端开发

```bash
cd me13
npm install
npm run dev        # 启动 Vite 开发服务器
```

### 构建（部署到插件）

```bash
cd me13
npm run build      # 输出到 me13-plugin/web/
```

构建产物会自动输出到 `me13-plugin/web/` 目录，由 KiraAI 插件作为静态文件提供服务。

### 插件部署

将 `me13-plugin/` 目录放置到 KiraAI 的 `plugins/` 目录下，重启 KiraAI 即可在侧边栏看到 "δ-me13 控制台"。

---

## 插件配置

通过 KiraAI 插件管理界面配置：

| 字段 | 说明 |
|---|---|
| **LLM API Key** | OpenAI 兼容的 API 密钥 |
| **Base URL** | API 端点地址 |
| **Model** | 模型 ID（如 gpt-4o-mini） |
| **Temperature** | 生成温度（0-2） |
| **后端地址** | 留空使用 KiraAI 后端，填入可独立运行 |
| **背景音乐** | 开关科幻主题 BGM |

---

## 模拟世界

### 世界设定

翁法罗斯（Omphalos）是一个被泰坦封印的模拟世界。十二位泰坦各自守护一枚火种，而十二位黄金裔则踏上了收集火种、对抗黑暗潮汐的旅程。

### 智能体架构

所有智能体（Agent）继承自 `BaseAgent`，通过 LLM 函数调用进行决策：

1. **收集** — 获取当前世界状态与记忆
2. **决策** — LLM 根据角色设定、世界上下文生成行动 JSON
3. **执行** — 环境引擎执行行动，变更世界状态
4. **记录** — 行动结果存入记忆系统

### Bot 工具（5个）

注册为 KiraAI 平台工具，LLM 可直接调用：

| 工具 | 功能 |
|---|---|
| `omphalos_status` | 查看世界状态（天数、地点、火种、黑暗潮汐） |
| `omphalos_move` | 移动到其他地区 |
| `omphalos_explore` | 探索当前地区，发现资源 |
| `omphalos_interact` | 与 NPC 交谈互动 |
| `omphalos_advance` | 推进世界时间 |

---

## 现有 README 存档

原项目 README 已迁移至 [me13/CLAUDE.md](./me13/CLAUDE.md)，包含详细的模拟核心架构说明、Agent 层级关系、数据流和关键实现细节。

---

## 友情链接

- [Rorical/delta-me13](https://github.com/Rorical/delta-me13) — 原始项目，本项目基于此分支进行二次开发

## 许可

[LICENSE](./LICENSE)
