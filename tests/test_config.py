"""
配置模块测试

测试配置管理、数据验证和文件操作功能。
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from pydantic import ValidationError

from mcrcon_tool_plus.config import (
    ServerConfig, UIConfig, LoggingConfig, Config, ConfigManager
)


class TestServerConfig:
    """服务器配置测试"""

    def test_valid_server_config(self):
        """测试有效的服务器配置"""
        config = ServerConfig(
            host="localhost",
            port=25575,
            password="secret123"
        )
        assert config.host == "localhost"
        assert config.port == 25575
        assert config.password == "secret123"
        assert config.timeout == 10.0  # 默认值
        assert config.retry_attempts == 3  # 默认值

    def test_server_config_with_all_fields(self):
        """测试包含所有字段的服务器配置"""
        config = ServerConfig(
            host="example.com",
            port=25580,
            password="mypassword",
            timeout=15.0,
            retry_attempts=5,
            retry_delay=2.0,
            description="测试服务器"
        )
        assert config.host == "example.com"
        assert config.port == 25580
        assert config.password == "mypassword"
        assert config.timeout == 15.0
        assert config.retry_attempts == 5
        assert config.retry_delay == 2.0
        assert config.description == "测试服务器"

    def test_invalid_port_range(self):
        """测试无效端口号范围"""
        with pytest.raises(ValidationError):
            ServerConfig(host="localhost", port=0, password="test")

        with pytest.raises(ValidationError):
            ServerConfig(host="localhost", port=65536, password="test")

    def test_invalid_timeout(self):
        """测试无效超时时间"""
        with pytest.raises(ValidationError):
            ServerConfig(host="localhost", port=25575, password="test", timeout=-1)

    def test_empty_host(self):
        """测试空主机地址"""
        with pytest.raises(ValidationError):
            ServerConfig(host="", port=25575, password="test")

        with pytest.raises(ValidationError):
            ServerConfig(host="   ", port=25575, password="test")

    def test_empty_password(self):
        """测试空密码"""
        with pytest.raises(ValidationError):
            ServerConfig(host="localhost", port=25575, password="")


class TestUIConfig:
    """用户界面配置测试"""

    def test_default_ui_config(self):
        """测试默认 UI 配置"""
        config = UIConfig()
        assert config.theme == "dark"
        assert config.animations is True
        assert config.history_size == 1000
        assert config.auto_complete is True
        assert config.show_timestamps is True
        assert config.color_output is True

    def test_custom_ui_config(self):
        """测试自定义 UI 配置"""
        config = UIConfig(
            theme="light",
            animations=False,
            history_size=500
        )
        assert config.theme == "light"
        assert config.animations is False
        assert config.history_size == 500

    def test_invalid_theme(self):
        """测试无效主题"""
        with pytest.raises(ValidationError):
            UIConfig(theme="invalid")

    def test_invalid_history_size(self):
        """测试无效历史大小"""
        with pytest.raises(ValidationError):
            UIConfig(history_size=5)  # 太小

        with pytest.raises(ValidationError):
            UIConfig(history_size=50000)  # 太大


class TestLoggingConfig:
    """日志配置测试"""

    def test_default_logging_config(self):
        """测试默认日志配置"""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.file is None
        assert config.max_file_size == "10 MB"
        assert config.backup_count == 5
        assert config.console_output is True

    def test_custom_logging_config(self):
        """测试自定义日志配置"""
        config = LoggingConfig(
            level="DEBUG",
            file="app.log",
            max_file_size="5 MB",
            backup_count=3,
            console_output=False
        )
        assert config.level == "DEBUG"
        assert config.file == "app.log"
        assert config.max_file_size == "5 MB"
        assert config.backup_count == 3
        assert config.console_output is False

    def test_invalid_log_level(self):
        """测试无效日志级别"""
        with pytest.raises(ValidationError):
            LoggingConfig(level="INVALID")

    def test_invalid_backup_count(self):
        """测试无效备份数量"""
        with pytest.raises(ValidationError):
            LoggingConfig(backup_count=0)

        with pytest.raises(ValidationError):
            LoggingConfig(backup_count=25)


class TestConfig:
    """主配置测试"""

    def test_empty_config(self):
        """测试空配置"""
        config = Config()
        assert config.servers == {}
        assert isinstance(config.ui, UIConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert config.default_server is None

    def test_config_with_servers(self):
        """测试包含服务器的配置"""
        server1 = ServerConfig(host="localhost", port=25575, password="test1")
        server2 = ServerConfig(host="example.com", port=25580, password="test2")

        config = Config(
            servers={
                "local": server1,
                "remote": server2
            },
            default_server="local"
        )

        assert len(config.servers) == 2
        assert config.get_server_config("local") == server1
        assert config.get_server_config("remote") == server2
        assert config.default_server == "local"

    def test_add_server(self):
        """测试添加服务器"""
        config = Config()
        server = ServerConfig(host="new.com", port=25590, password="newpass")

        config.add_server("new", server)

        assert "new" in config.servers
        assert config.get_server_config("new") == server

    def test_remove_server(self):
        """测试删除服务器"""
        server = ServerConfig(host="test.com", port=25575, password="test")
        config = Config(servers={"test": server}, default_server="test")

        result = config.remove_server("test")

        assert result is True
        assert "test" not in config.servers
        assert config.default_server is None

    def test_remove_nonexistent_server(self):
        """测试删除不存在的服务器"""
        config = Config()
        result = config.remove_server("nonexistent")

        assert result is False

    def test_list_servers(self):
        """测试列出服务器"""
        server1 = ServerConfig(host="host1.com", port=25575, password="pass1")
        server2 = ServerConfig(host="host2.com", port=25580, password="pass2")

        config = Config(servers={
            "server1": server1,
            "server2": server2
        })

        servers = config.list_servers()
        assert set(servers) == {"server1", "server2"}

    def test_get_default_server_config(self):
        """测试获取默认服务器配置"""
        server = ServerConfig(host="default.com", port=25575, password="default")
        config = Config(servers={"default": server}, default_server="default")

        default_server = config.get_default_server_config()
        assert default_server == server

    def test_get_default_server_config_none(self):
        """测试获取默认服务器配置（无默认）"""
        config = Config()

        default_server = config.get_default_server_config()
        assert default_server is None

    def test_invalid_default_server(self):
        """测试无效的默认服务器"""
        with pytest.raises(ValidationError):
            Config(servers={}, default_server="nonexistent")


class TestConfigManager:
    """配置管理器测试"""

    def test_get_default_config_path(self):
        """测试获取默认配置路径"""
        manager = ConfigManager()
        path = manager._get_default_config_path()
        assert isinstance(path, Path)
        assert path.suffix == ".yaml"

    def test_create_default_config(self):
        """测试创建默认配置"""
        manager = ConfigManager()
        config = manager._create_default_config()

        assert isinstance(config, Config)
        assert len(config.servers) == 1
        assert "local" in config.servers
        local_server = config.servers["local"]
        assert local_server.host == "localhost"
        assert local_server.port == 25575
        assert local_server.password == "your_password"

    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"
            manager = ConfigManager(config_path)

            # 创建测试配置
            original_config = manager._create_default_config()
            original_config.servers["test"] = ServerConfig(
                host="test.com",
                port=25590,
                password="testpass",
                description="测试服务器"
            )

            # 保存配置
            manager.config = original_config
            manager.save_config()

            # 验证文件存在
            assert config_path.exists()

            # 加载配置
            loaded_config = manager.load_config()

            # 验证配置内容
            assert len(loaded_config.servers) == 2
            assert "local" in loaded_config.servers
            assert "test" in loaded_config.servers

            test_server = loaded_config.servers["test"]
            assert test_server.host == "test.com"
            assert test_server.port == 25590
            assert test_server.password == "testpass"
            assert test_server.description == "测试服务器"

    def test_load_config_file_not_exists(self):
        """测试加载不存在的配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"
            manager = ConfigManager(config_path)

            # 加载不存在的文件应该创建默认配置
            config = manager.load_config()

            assert isinstance(config, Config)
            assert len(config.servers) >= 1  # 应该有默认服务器

    def test_load_invalid_yaml(self):
        """测试加载无效的 YAML 文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "invalid.yaml"
            manager = ConfigManager(config_path)

            # 写入无效的 YAML
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write("invalid: yaml: content: [")

            # 加载应该失败
            with pytest.raises(yaml.YAMLError):
                manager.load_config()

    def test_ensure_config_exists(self):
        """测试确保配置文件存在"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "ensure_test.yaml"
            manager = ConfigManager(config_path)

            # 文件不存在时调用
            assert not config_path.exists()
            manager.ensure_config_exists()
            assert config_path.exists()

            # 文件存在时再次调用
            manager.ensure_config_exists()  # 不应该抛出错误
            assert config_path.exists()

    def test_get_config(self):
        """测试获取配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "get_test.yaml"
            manager = ConfigManager(config_path)

            # 第一次调用应该加载配置
            config1 = manager.get_config()
            assert isinstance(config1, Config)

            # 第二次调用应该返回缓存的配置
            config2 = manager.get_config()
            assert config1 is config2

    def test_reload_config(self):
        """测试重新加载配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "reload_test.yaml"
            manager = ConfigManager(config_path)

            # 初始加载
            config1 = manager.get_config()
            initial_server_count = len(config1.servers)

            # 手动修改配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump({
                    "servers": {
                        "new_server": {
                            "host": "new.com",
                            "port": 25575,
                            "password": "newpass"
                        }
                    }
                }, f)

            # 重新加载
            config2 = manager.reload_config()

            assert config2 is not config1  # 应该是新的实例
            assert len(config2.servers) != initial_server_count