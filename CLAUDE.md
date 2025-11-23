# CLAUDE.md

这个文件为 Claude Code (claude.ai/code) 在此代码库中工作提供指导。

## 项目概述

McRconToolPlus 是一个用 Python 开发的 Minecraft RCON 工具，提供美观的界面动画和完善的服务器控制台连接功能。

## 项目架构

项目目前正在初始化阶段，使用 Python 3.13 开发环境。

### 建议的项目结构
```
McRconToolPlus/
├── src/
│   └── mcrcon_tool_plus/
│       ├── __init__.py
│       ├── main.py              # 主入口文件
│       ├── rcon_client.py       # RCON 客户端核心功能
│       ├── ui/                  # 用户界面模块
│       │   ├── __init__.py
│       │   ├── terminal.py      # 终端界面
│       │   └── animations.py    # 界面动画
│       ├── commands.py          # 命令处理
│       ├── config.py            # 配置管理
│       └── utils.py             # 工具函数
├── tests/                       # 测试目录
├── requirements.txt             # 依赖列表
├── pyproject.toml              # 项目配置
├── README.md                   # 项目说明
└── .gitignore                  # Git 忽略规则
```

## 开发环境设置

### 运行配置
- 主脚本: `main.py`
- 工作目录: 项目根目录
- 环境变量: `PYTHONUNBUFFERED=1`

### IDE 配置
项目已配置 PyCharm/IntelliJ IDEA 开发环境，使用 Python 3.13 SDK。

## 核心技术栈

### 主要依赖
- `mcrcon`: Minecraft RCON 协议实现
- `rich`: 美观的终端界面和动画
- `click`: 命令行界面框架
- `pydantic`: 数据验证和配置管理
- `asyncio`: 异步编程支持

### 可选依赖
- `aioconsole`: 异步控制台 I/O
- `configparser`: 配置文件处理
- `loguru`: 日志记录

## 开发工作流程

### 1. 环境初始化
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行项目
```bash
# 运行主程序
python main.py

# 或使用模块方式
python -m mcrcon_tool_plus
```

### 3. 测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_rcon_client.py
```

## 核心功能模块

### RCON 客户端 (rcon_client.py)
- 实现 Minecraft RCON 协议
- 处理服务器连接和认证
- 命令发送和响应接收
- 连接状态管理

### 用户界面 (ui/)
- 基于 Rich 的终端界面
- 动画效果和进度显示
- 命令历史和自动补全
- 实时输出显示

### 配置管理 (config.py)
- 服务器连接配置
- 用户偏好设置
- 配置文件验证和加载

### 命令处理 (commands.py)
- 命令解析和验证
- 内置命令支持
- 插件系统架构

## 代码规范

### 编码风格
- 遵循 PEP 8 规范
- 使用中文注释，注释完善
- 函数和类必须有完整的文档字符串

### 提交规范
- 使用中文提交信息
- 保持提交原子性
- 代码审查通过后才能合并

## 注意事项

- 所有用户界面文本使用中文
- 注释必须使用中文且完善
- 代码错误处理要完整
- 界面动画要美观流畅
- 支持配置文件的热重载