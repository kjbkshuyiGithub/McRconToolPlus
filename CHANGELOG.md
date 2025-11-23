# 更新日志

本文档记录了 McRconToolPlus 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 初始化项目结构
- 实现基础 RCON 协议支持
- 添加配置管理功能
- 创建命令行界面框架

### 变更
- 更新 Python 版本要求为 3.13+

## [0.1.0] - 2024-01-XX

### 新增
- 🎮 完整的 Minecraft RCON 协议实现
- 🎨 基于 Rich 库的美观终端界面
- 📝 命令历史记录和自动补全功能
- 🔧 灵活的配置管理系统
- 🚀 异步架构，高性能响应
- 🔒 完善的错误处理和连接状态管理
- 📱 跨平台支持（Windows、macOS、Linux）

### 技术栈
- Python 3.13+
- Rich - 终端界面和动画
- Click - 命令行界面框架
- Pydantic - 数据验证
- asyncio - 异步编程支持

### 文档
- 完整的 README.md
- 详细的贡献指南
- GitHub Issue 模板
- 开发环境配置说明

### 开发工具
- Black - 代码格式化
- isort - 导入排序
- flake8 - 代码检查
- mypy - 类型检查
- pytest - 测试框架

---

## 版本说明

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正