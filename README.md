l# McRconToolPlus

<div align="center">

![McRconToolPlus Logo](https://via.placeholder.com/200x80/1e1e2e/cdd6f4?text=McRconToolPlus)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Build Status](https://github.com/your-username/McRconToolPlus/workflows/CI/badge.svg)](https://github.com/your-username/McRconToolPlus/actions)

一个功能强大、界面美观的 Minecraft RCON 工具，支持动画效果和完善的服务器控制台功能。

</div>

## ✨ 特性

- 🎮 **完整 RCON 支持** - 支持所有标准的 Minecraft RCON 命令
- 🎨 **美观界面** - 基于 Rich 库的现代化终端界面，支持动画效果
- 🔧 **配置管理** - 灵活的服务器连接配置和用户偏好设置
- 📝 **命令历史** - 智能的命令历史记录和自动补全功能
- 🚀 **高性能** - 基于 asyncio 的异步架构，响应迅速
- 🔒 **安全可靠** - 完善的错误处理和连接状态管理
- 📱 **跨平台** - 支持 Windows、macOS 和 Linux

## 🚀 快速开始

### 安装

#### 通过 pip 安装（推荐）

```bash
pip install mcrcon-tool-plus
```

#### 从源码安装

```bash
git clone https://github.com/your-username/McRconToolPlus.git
cd McRconToolPlus
pip install -e .
```

### 基本使用

```bash
# 启动交互式界面
mcrcon-tool-plus

# 直接执行命令
mcrcon-tool-plus --host localhost --port 25575 --password your_password "list"

# 使用配置文件
mcrcon-tool-plus --config config.yaml
```

### 配置服务器

创建配置文件 `config.yaml`：

```yaml
servers:
  main:
    host: "localhost"
    port: 25575
    password: "your_password"
    timeout: 10
  creative:
    host: "creative.example.com"
    port: 25575
    password: "creative_password"
    timeout: 15

ui:
  theme: "dark"
  animations: true
  history_size: 1000

logging:
  level: "INFO"
  file: "mcrcon.log"
```

## 📖 详细文档

### 命令行选项

```bash
mcrcon-tool-plus [OPTIONS] [COMMAND]

选项：
  -h, --help            显示帮助信息
  -c, --config PATH     配置文件路径
  -s, --server TEXT     服务器名称（来自配置文件）
  --host TEXT           服务器主机地址
  --port INTEGER        RCON 端口号
  --password TEXT       RCON 密码
  --timeout INTEGER     连接超时时间（秒）
  --no-animations       禁用界面动画
  --version             显示版本信息
```

### 交互式界面

启动后，您将看到美观的交互式界面，包含：

- **服务器连接状态** - 实时显示连接状态和延迟
- **命令输入区域** - 支持历史记录和自动补全
- **输出显示区域** - 格式化的命令输出，支持颜色和进度条
- **状态栏** - 显示当前服务器、时间等信息

### 支持的命令

所有标准的 Minecraft 服务器命令都支持，包括：

- `list` - 显示在线玩家列表
- `gamemode` - 更改游戏模式
- `tp` - 传送玩家
- `give` - 给予物品
- `time` - 设置世界时间
- `weather` - 设置天气
- 以及更多...

## 🛠️ 开发

### 环境设置

```bash
# 克隆项目
git clone https://github.com/your-username/McRconToolPlus.git
cd McRconToolPlus

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 开发工具

项目使用以下工具来保证代码质量：

- **Black** - 代码格式化
- **isort** - 导入排序
- **flake8** - 代码检查
- **mypy** - 类型检查
- **pytest** - 测试框架

### 运行测试

```bash
# 运行所有测试
pytest

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 代码风格检查

```bash
# 格式化代码
black src/ tests/
isort src/ tests/

# 检查代码质量
flake8 src/ tests/
mypy src/
```

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。

### 快速贡献

1. Fork 这个项目
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'feat: 添加某个很酷的功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📋 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本更新信息。

## ❓ 常见问题

### Q: 如何连接到 Minecraft 服务器？

A: 确保服务器的 `server.properties` 文件中启用了 RCON：

```properties
enable-rcon=true
rcon.port=25575
rcon.password=your_password
```

### Q: 支持哪些 Minecraft 版本？

A: 支持 Java 版 1.8+ 的所有版本，只要启用了 RCON 功能。

### Q: 如何自定义界面主题？

A: 在配置文件中设置 `ui.theme`，支持 `dark`、`light` 和自定义颜色方案。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Rich](https://github.com/Textualize/rich) - 美观的终端界面库
- [Click](https://github.com/pallets/click) - 优秀的命令行界面框架
- [Minecraft](https://www.minecraft.net/) - 感谢 Mojang 提供的 RCON 协议

## 📞 联系

- 项目主页: https://github.com/your-username/McRconToolPlus
- 问题反馈: https://github.com/your-username/McRconToolPlus/issues
- 讨论区: https://github.com/your-username/McRconToolPlus/discussions

---

<div align="center">
Made with ❤️ by the McRconToolPlus team
</div>