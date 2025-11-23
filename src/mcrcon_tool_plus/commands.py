"""
命令处理模块

这个模块实现了命令处理和执行功能，包括：
- 命令注册和调度
- 内置命令实现
- 命令解析和验证
- 命令结果格式化
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass
from loguru import logger

from .rcon_client import RconClient, ConnectionError, AuthenticationError
from .config import ServerConfig


@dataclass
class CommandResult:
    """
    命令执行结果
    """
    success: bool
    output: str
    execution_time: float
    error: Optional[str] = None

    def __str__(self) -> str:
        """返回结果的字符串表示"""
        if self.success:
            return f"执行成功 ({self.execution_time:.3f}s):\n{self.output}"
        else:
            return f"执行失败 ({self.execution_time:.3f}s): {self.error}"


class BaseCommand(ABC):
    """
    命令基类
    """

    def __init__(self, name: str, description: str, aliases: List[str] = None):
        """
        初始化命令

        Args:
            name: 命令名称
            description: 命令描述
            aliases: 命令别名列表
        """
        self.name = name
        self.description = description
        self.aliases = aliases or []

    @abstractmethod
    async def execute(
        self,
        rcon_client: RconClient,
        args: List[str],
        config: Optional[ServerConfig] = None
    ) -> CommandResult:
        """
        执行命令

        Args:
            rcon_client: RCON 客户端
            args: 命令参数
            config: 服务器配置

        Returns:
            命令执行结果
        """
        pass

    def validate_args(self, args: List[str]) -> bool:
        """
        验证命令参数

        Args:
            args: 命令参数

        Returns:
            参数是否有效
        """
        return True

    def get_help(self) -> str:
        """
        获取命令帮助信息

        Returns:
            帮助信息字符串
        """
        aliases_str = f" (别名: {', '.join(self.aliases)})" if self.aliases else ""
        return f"{self.name}{aliases_str} - {self.description}"


class RawCommand(BaseCommand):
    """
    原始命令类 - 直接发送到 Minecraft 服务器
    """

    def __init__(self, command: str):
        """
        初始化原始命令

        Args:
            command: 要发送的命令字符串
        """
        super().__init__(command, f"执行 Minecraft 命令: {command}")
        self.command = command

    async def execute(
        self,
        rcon_client: RconClient,
        args: List[str],
        config: Optional[ServerConfig] = None
    ) -> CommandResult:
        """
        执行原始 Minecraft 命令

        Args:
            rcon_client: RCON 客户端
            args: 命令参数
            config: 服务器配置

        Returns:
            命令执行结果
        """
        start_time = time.time()

        try:
            # 构建完整命令
            full_command = self.command
            if args:
                full_command += " " + " ".join(args)

            logger.debug(f"执行原始命令: {full_command}")

            # 发送命令
            output = await rcon_client.execute_command(full_command)

            execution_time = time.time() - start_time
            return CommandResult(
                success=True,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"命令执行失败: {e}")
            return CommandResult(
                success=False,
                output="",
                execution_time=execution_time,
                error=str(e)
            )


class PingCommand(BaseCommand):
    """
    Ping 命令 - 测试服务器连接延迟
    """

    def __init__(self):
        super().__init__("ping", "测试服务器连接延迟")

    async def execute(
        self,
        rcon_client: RconClient,
        args: List[str],
        config: Optional[ServerConfig] = None
    ) -> CommandResult:
        """
        执行 ping 命令

        Args:
            rcon_client: RCON 客户端
            args: 命令参数
            config: 服务器配置

        Returns:
            命令执行结果
        """
        start_time = time.time()

        try:
            latency = await rcon_client.ping()
            execution_time = time.time() - start_time

            output = f"服务器连接正常，延迟: {latency:.2f}ms"
            return CommandResult(
                success=True,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"服务器连接测试失败: {e}"
            return CommandResult(
                success=False,
                output="",
                execution_time=execution_time,
                error=error_msg
            )


class ListCommand(BaseCommand):
    """
    列表命令 - 显示在线玩家
    """

    def __init__(self):
        super().__init__("list", "显示在线玩家列表")

    async def execute(
        self,
        rcon_client: RconClient,
        args: List[str],
        config: Optional[ServerConfig] = None
    ) -> CommandResult:
        """
        执行列表命令

        Args:
            rcon_client: RCON 客户端
            args: 命令参数
            config: 服务器配置

        Returns:
            命令执行结果
        """
        start_time = time.time()

        try:
            # 发送 list 命令
            output = await rcon_client.execute_command("list")
            execution_time = time.time() - start_time

            return CommandResult(
                success=True,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"获取玩家列表失败: {e}"
            return CommandResult(
                success=False,
                output="",
                execution_time=execution_time,
                error=error_msg
            )


class StatusCommand(BaseCommand):
    """
    状态命令 - 显示服务器状态信息
    """

    def __init__(self):
        super().__init__("status", "显示服务器状态信息")

    async def execute(
        self,
        rcon_client: RconClient,
        args: List[str],
        config: Optional[ServerConfig] = None
    ) -> CommandResult:
        """
        执行状态命令

        Args:
            rcon_client: RCON 客户端
            args: 命令参数
            config: 服务器配置

        Returns:
            命令执行结果
        """
        start_time = time.time()
        output_lines = []

        try:
            # 获取连接信息
            if config:
                output_lines.append(f"服务器: {config.host}:{config.port}")
                if config.description:
                    output_lines.append(f"描述: {config.description}")

            # 测试连接延迟
            try:
                latency = await rcon_client.ping()
                output_lines.append(f"连接状态: 正常 (延迟: {latency:.2f}ms)")
            except:
                output_lines.append("连接状态: 异常")

            # 获取时间信息
            try:
                time_response = await rcon_client.execute_command("time query daytime")
                output_lines.append(f"游戏时间: {time_response.strip()}")
            except:
                pass

            # 获取玩家信息
            try:
                list_response = await rcon_client.execute_command("list")
                output_lines.append(f"玩家信息: {list_response.strip()}")
            except:
                pass

            execution_time = time.time() - start_time
            final_output = "\n".join(output_lines)

            return CommandResult(
                success=True,
                output=final_output,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"获取服务器状态失败: {e}"
            return CommandResult(
                success=False,
                output="",
                execution_time=execution_time,
                error=error_msg
            )


class HelpCommand(BaseCommand):
    """
    帮助命令 - 显示命令帮助信息
    """

    def __init__(self):
        super().__init__("help", "显示帮助信息", ["h", "?"])

    async def execute(
        self,
        rcon_client: RconClient,
        args: List[str],
        config: Optional[ServerConfig] = None
    ) -> CommandResult:
        """
        执行帮助命令

        Args:
            rcon_client: RCON 客户端
            args: 命令参数
            config: 服务器配置

        Returns:
            命令执行结果
        """
        start_time = time.time()

        try:
            # 这个方法需要访问 CommandProcessor 来获取所有命令
            # 在实际使用中，我们会在 CommandProcessor 中重写这个方法
            output = "可用的内置命令:\n"
            output += "  ping - 测试服务器连接延迟\n"
            output += "  list - 显示在线玩家列表\n"
            output += "  status - 显示服务器状态信息\n"
            output += "  help - 显示此帮助信息\n"
            output += "\n其他命令将直接发送到 Minecraft 服务器执行。"

            execution_time = time.time() - start_time
            return CommandResult(
                success=True,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                success=False,
                output="",
                execution_time=execution_time,
                error=str(e)
            )


class CommandProcessor:
    """
    命令处理器

    负责命令的注册、解析和执行
    """

    def __init__(self):
        """初始化命令处理器"""
        self.commands: Dict[str, BaseCommand] = {}
        self._register_builtin_commands()

    def _register_builtin_commands(self) -> None:
        """
        注册内置命令
        """
        builtin_commands = [
            PingCommand(),
            ListCommand(),
            StatusCommand(),
            HelpCommand(),
        ]

        for cmd in builtin_commands:
            self.register_command(cmd)
            for alias in cmd.aliases:
                self.commands[alias] = cmd

        logger.debug(f"已注册 {len(builtin_commands)} 个内置命令")

    def register_command(self, command: BaseCommand) -> None:
        """
        注册命令

        Args:
            command: 要注册的命令
        """
        self.commands[command.name] = command
        logger.debug(f"已注册命令: {command.name}")

    def unregister_command(self, name: str) -> bool:
        """
        注销命令

        Args:
            name: 命令名称

        Returns:
            是否成功注销
        """
        if name in self.commands:
            del self.commands[name]
            logger.debug(f"已注销命令: {name}")
            return True
        return False

    def list_commands(self) -> List[BaseCommand]:
        """
        列出所有命令

        Returns:
            命令列表
        """
        # 去重，避免别名重复显示
        seen_names = set()
        unique_commands = []

        for command in self.commands.values():
            if command.name not in seen_names:
                seen_names.add(command.name)
                unique_commands.append(command)

        return unique_commands

    def get_command(self, name: str) -> Optional[BaseCommand]:
        """
        获取指定名称的命令

        Args:
            name: 命令名称

        Returns:
            命令对象，如果不存在则返回 None
        """
        return self.commands.get(name)

    def parse_command(self, input_line: str) -> Tuple[Optional[BaseCommand], List[str]]:
        """
        解析命令行

        Args:
            input_line: 输入的命令行

        Returns:
            (命令对象, 参数列表) 的元组
        """
        if not input_line or not input_line.strip():
            return None, []

        # 分割命令和参数
        parts = input_line.strip().split()
        command_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # 查找命令
        command = self.get_command(command_name)
        if command:
            return command, args

        # 如果不是内置命令，创建原始命令
        return RawCommand(command_name), args

    async def execute_command(
        self,
        input_line: str,
        rcon_client: RconClient,
        config: Optional[ServerConfig] = None
    ) -> CommandResult:
        """
        执行命令

        Args:
            input_line: 输入的命令行
            rcon_client: RCON 客户端
            config: 服务器配置

        Returns:
            命令执行结果
        """
        command, args = self.parse_command(input_line)

        if command is None:
            return CommandResult(
                success=False,
                output="",
                execution_time=0.0,
                error="命令为空"
            )

        logger.debug(f"执行命令: {command.name}, 参数: {args}")

        try:
            # 验证参数
            if not command.validate_args(args):
                return CommandResult(
                    success=False,
                    output="",
                    execution_time=0.0,
                    error=f"命令参数无效: {args}"
                )

            # 执行命令
            result = await command.execute(rcon_client, args, config)
            logger.debug(f"命令执行完成，成功: {result.success}")
            return result

        except Exception as e:
            logger.error(f"命令执行过程中发生错误: {e}")
            return CommandResult(
                success=False,
                output="",
                execution_time=0.0,
                error=f"命令执行错误: {e}"
            )

    def get_help_text(self) -> str:
        """
        获取帮助文本

        Returns:
            格式化的帮助文本
        """
        help_lines = ["可用的命令:"]

        for command in self.list_commands():
            help_lines.append(f"  {command.get_help()}")

        help_lines.extend([
            "",
            "其他命令将直接发送到 Minecraft 服务器执行。",
            "使用 help [命令名] 获取特定命令的详细帮助。"
        ])

        return "\n".join(help_lines)