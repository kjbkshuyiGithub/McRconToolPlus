"""
配置管理模块

这个模块实现了项目的配置管理功能，包括：
- 配置文件加载和保存
- 配置数据验证
- 默认配置值
- 多种配置格式支持（YAML、JSON）
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
import yaml
from loguru import logger


class ServerConfig(BaseModel):
    """
    服务器配置模型
    """
    host: str = Field(..., description="服务器主机地址")
    port: int = Field(25575, ge=1, le=65535, description="RCON 端口号")
    password: str = Field(..., min_length=1, description="RCON 密码")
    timeout: float = Field(10.0, gt=0, description="连接超时时间（秒）")
    retry_attempts: int = Field(3, ge=0, description="连接失败重试次数")
    retry_delay: float = Field(1.0, ge=0, description="重试之间的延迟时间（秒）")
    description: Optional[str] = Field(None, description="服务器描述")

    @validator('host')
    def validate_host(cls, v):
        """验证主机地址"""
        if not v or not v.strip():
            raise ValueError('主机地址不能为空')
        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        """验证密码"""
        if not v:
            raise ValueError('密码不能为空')
        return v


class UIConfig(BaseModel):
    """
    用户界面配置模型
    """
    theme: str = Field("dark", description="界面主题 (dark/light)")
    animations: bool = Field(True, description="是否启用动画效果")
    history_size: int = Field(1000, ge=10, le=10000, description="命令历史记录大小")
    auto_complete: bool = Field(True, description="是否启用自动补全")
    show_timestamps: bool = Field(True, description="是否显示时间戳")
    color_output: bool = Field(True, description="是否启用彩色输出")

    @validator('theme')
    def validate_theme(cls, v):
        """验证主题设置"""
        if v.lower() not in ['dark', 'light']:
            raise ValueError('主题必须是 "dark" 或 "light"')
        return v.lower()


class LoggingConfig(BaseModel):
    """
    日志配置模型
    """
    level: str = Field("INFO", description="日志级别")
    file: Optional[str] = Field(None, description="日志文件路径")
    max_file_size: str = Field("10 MB", description="日志文件最大大小")
    backup_count: int = Field(5, ge=1, le=20, description="日志文件备份数量")
    console_output: bool = Field(True, description="是否输出到控制台")

    @validator('level')
    def validate_level(cls, v):
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'日志级别必须是: {", ".join(valid_levels)}')
        return v.upper()


class Config(BaseModel):
    """
    主配置模型
    """
    servers: Dict[str, ServerConfig] = Field(default_factory=dict, description="服务器配置列表")
    ui: UIConfig = Field(default_factory=UIConfig, description="界面配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")
    default_server: Optional[str] = Field(None, description="默认服务器名称")

    @validator('default_server')
    def validate_default_server(cls, v, values):
        """验证默认服务器"""
        if v is not None and 'servers' in values and v not in values['servers']:
            raise ValueError(f'默认服务器 "{v}" 未在服务器配置中定义')
        return v

    def get_server_config(self, name: str) -> Optional[ServerConfig]:
        """
        获取指定名称的服务器配置

        Args:
            name: 服务器名称

        Returns:
            服务器配置，如果不存在则返回 None
        """
        return self.servers.get(name)

    def add_server(self, name: str, config: ServerConfig) -> None:
        """
        添加服务器配置

        Args:
            name: 服务器名称
            config: 服务器配置
        """
        self.servers[name] = config
        logger.info(f"已添加服务器配置: {name}")

    def remove_server(self, name: str) -> bool:
        """
        删除服务器配置

        Args:
            name: 服务器名称

        Returns:
            是否成功删除
        """
        if name in self.servers:
            del self.servers[name]

            # 如果删除的是默认服务器，清除默认设置
            if self.default_server == name:
                self.default_server = None

            logger.info(f"已删除服务器配置: {name}")
            return True
        return False

    def list_servers(self) -> List[str]:
        """
        列出所有服务器名称

        Returns:
            服务器名称列表
        """
        return list(self.servers.keys())

    def get_default_server_config(self) -> Optional[ServerConfig]:
        """
        获取默认服务器配置

        Returns:
            默认服务器配置，如果未设置则返回 None
        """
        if self.default_server:
            return self.get_server_config(self.default_server)
        return None


class ConfigManager:
    """
    配置管理器

    负责配置文件的加载、保存和管理
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
        """
        if config_path is None:
            config_path = self._get_default_config_path()

        self.config_path = Path(config_path)
        self.config: Optional[Config] = None

    @staticmethod
    def _get_default_config_path() -> Path:
        """
        获取默认配置文件路径

        Returns:
            默认配置文件路径
        """
        # 优先级：当前目录 > 用户目录 > 系统配置目录
        current_dir = Path.cwd() / "mcrcon_config.yaml"
        if current_dir.exists():
            return current_dir

        user_dir = Path.home() / ".mcrcon_tool_plus" / "config.yaml"
        user_dir.parent.mkdir(parents=True, exist_ok=True)
        return user_dir

    def load_config(self) -> Config:
        """
        加载配置文件

        Returns:
            配置对象

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 解析错误
            pydantic.ValidationError: 配置验证错误
        """
        if not self.config_path.exists():
            logger.info(f"配置文件不存在，将创建默认配置: {self.config_path}")
            self.config = self._create_default_config()
            self.save_config()
            return self.config

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}

            logger.debug(f"加载配置文件: {self.config_path}")
            self.config = Config(**config_data)
            logger.info(f"配置加载成功，共 {len(self.config.servers)} 个服务器")
            return self.config

        except yaml.YAMLError as e:
            logger.error(f"配置文件解析失败: {e}")
            raise
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise

    def save_config(self) -> None:
        """
        保存配置文件

        Raises:
            yaml.YAMLError: YAML 序列化错误
            OSError: 文件写入错误
        """
        if self.config is None:
            raise ValueError("没有可保存的配置")

        try:
            # 确保配置目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.config.dict(exclude_none=True),
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                    sort_keys=False
                )

            logger.info(f"配置已保存到: {self.config_path}")

        except yaml.YAMLError as e:
            logger.error(f"配置文件序列化失败: {e}")
            raise
        except Exception as e:
            logger.error(f"配置文件保存失败: {e}")
            raise

    def _create_default_config(self) -> Config:
        """
        创建默认配置

        Returns:
            默认配置对象
        """
        return Config(
            servers={
                "local": ServerConfig(
                    host="localhost",
                    port=25575,
                    password="your_password",
                    description="本地测试服务器"
                )
            },
            ui=UIConfig(),
            logging=LoggingConfig()
        )

    def get_config(self) -> Config:
        """
        获取当前配置

        Returns:
            当前配置对象
        """
        if self.config is None:
            self.config = self.load_config()
        return self.config

    def reload_config(self) -> Config:
        """
        重新加载配置文件

        Returns:
            重新加载的配置对象
        """
        self.config = None
        return self.load_config()

    def ensure_config_exists(self) -> None:
        """
        确保配置文件存在，如果不存在则创建默认配置
        """
        if not self.config_path.exists():
            logger.info("创建默认配置文件")
            self.config = self._create_default_config()
            self.save_config()
        elif self.config is None:
            self.load_config()