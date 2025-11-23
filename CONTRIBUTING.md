# 贡献指南

感谢您对 McRconToolPlus 项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告 Bug
- ✨ 提出新功能建议
- 📝 改进文档
- 💻 提交代码
- 🔍 代码审查

## 🚀 快速开始

### 环境准备

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 这个项目
   # 然后克隆您的 Fork
   git clone https://github.com/kjbkshuyiGithub/McRconToolPlus.git
   cd McRconToolPlus
   ```

2. **设置开发环境**
   ```bash
   # 创建虚拟环境
   python -m venv venv

   # 激活虚拟环境
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate

   # 安装依赖
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **配置开发工具**
   ```bash
   # 安装 pre-commit hooks
   pre-commit install
   ```

### 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **编写代码**
   - 遵循项目的代码风格
   - 添加必要的测试
   - 更新相关文档

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

4. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   # 然后在 GitHub 上创建 Pull Request
   ```

## 📝 代码规范

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 规范：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(rcon): 添加批量命令执行功能

- 支持从文件读取命令列表
- 添加执行进度显示
- 实现错误恢复机制

Closes #123
```

### 代码风格

我们使用以下工具来保证代码质量：

1. **Black** - 代码格式化
2. **isort** - 导入排序
3. **flake8** - 代码检查
4. **mypy** - 类型检查

### 文档规范

- 所有函数和类必须包含完整的中文文档字符串
- 使用 Google 风格的文档字符串格式
- 更新 README 和相关文档

```python
def connect_to_server(host: str, port: int, password: str) -> bool:
    """连接到 Minecraft 服务器

    Args:
        host: 服务器主机地址
        port: RCON 端口号
        password: RCON 密码

    Returns:
        连接是否成功

    Raises:
        ConnectionError: 连接失败时抛出
        AuthenticationError: 认证失败时抛出
    """
    pass
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_rcon_client.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 编写测试

- 为新功能编写单元测试
- 测试文件命名为 `test_*.py`
- 使用 `pytest` 框架
- 保持测试的独立性和可重复性

## 🐛 报告 Bug

在报告 Bug 之前，请：

1. 检查是否已有相关的 Issue
2. 确保使用的是最新版本
3. 提供详细的复现步骤
4. 包含环境信息和错误日志

使用我们的 [Bug Report 模板](.github/ISSUE_TEMPLATE/bug_report.md) 来报告 Bug。

## ✨ 提出新功能

在提出新功能之前，请：

1. 检查是否已有相关的 Issue 或讨论
2. 详细描述功能的使用场景
3. 考虑实现方案和可能的影响

使用我们的 [Feature Request 模板](.github/ISSUE_TEMPLATE/feature_request.md) 来提出新功能。

## 📋 Pull Request 指南

### PR 检查清单

提交 PR 前请确保：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 通过了所有 CI 检查
- [ ] 没有合并冲突
- [ ] 提交信息符合规范

### PR 流程

1. **创建 PR**
   - 使用清晰的标题和描述
   - 关联相关的 Issue
   - 添加适当的标签

2. **代码审查**
   - 响应审查意见
   - 根据反馈修改代码
   - 保持友好的讨论

3. **合并**
   - 得到维护者批准后合并
   - 删除功能分支

## 🏷️ 发布流程

项目使用语义化版本控制：

- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

发布流程：

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 手动创建 GitHub Release 和发布到 PyPI

## 🤝 社区

- 保持友好和尊重的交流
- 帮助新贡献者
- 参与讨论和代码审查
- 分享使用经验

## 📞 联系方式

- GitHub Issues: [项目 Issues 页面](https://github.com/kjbkshuyiGithub/McRconToolPlus/issues)
- GitHub Discussions: [项目讨论区](https://github.com/kjbkshuyiGithub/McRconToolPlus/discussions)

---

感谢您的贡献！🎉