"""
命令行接口模块

这个模块实现了 McRconToolPlus 的命令行接口功能，包括：
- 命令行参数解析
- 交互式界面
- 单次命令执行
- 配置管理
"""

import asyncio
import sys
from typing import Optional, List
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from loguru import logger

from .rcon_client import RconClient, ConnectionError, AuthenticationError
from .config import ConfigManager, Config, ServerConfig
from .commands import CommandProcessor, CommandResult


class McRconApp:
    """
    McRconToolPlus 应用程序主类
    """

    def __init__(self, config_manager: ConfigManager):
        """
        初始化应用程序

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.config: Optional[Config] = None
        self.rcon_client: Optional[RconClient] = None
        self.command_processor = CommandProcessor()
        self.console = Console()

    async def initialize(self) -> None:
        """
        初始化应用程序
        """
        try:
            # 加载配置
            self.config = self.config_manager.get_config()
            logger.info("应用程序初始化完成")
        except Exception as e:
            self.console.print(f"[red]配置加载失败: {e}[/red]")
            sys.exit(1)

    async def execute_single_command(
        self,
        command: str,
        server_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        password: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> bool:
        """
        执行单个命令

        Args:
            command: 要执行的命令
            server_name: 服务器名称（来自配置文件）
            host: 服务器主机地址
            port: RCON 端口号
            password: RCON 密码
            timeout: 连接超时时间

        Returns:
            执行是否成功
        """
        try:
            # 获取服务器配置
            server_config = self._get_server_config(
                server_name, host, port, password, timeout
            )

            if server_config is None:
                self.console.print("[red]错误: 未指定有效的服务器配置[/red]")
                return False

            # 创建 RCON 客户端
            self.rcon_client = RconClient(
                host=server_config.host,
                port=server_config.port,
                password=server_config.password,
                timeout=server_config.timeout,
                retry_attempts=server_config.retry_attempts,
                retry_delay=server_config.retry_delay
            )

            # 连接并执行命令
            async with self.rcon_client:
                result = await self.command_processor.execute_command(
                    command, self.rcon_client, server_config
                )

                # 显示结果
                self._display_command_result(result)

                return result.success

        except Exception as e:
            self.console.print(f"[red]执行命令时发生错误: {e}[/red]")
            logger.error(f"命令执行失败: {e}")
            return False

    def _get_server_config(
        self,
        server_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        password: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> Optional[ServerConfig]:
        """
        获取服务器配置

        Args:
            server_name: 服务器名称（来自配置文件）
            host: 服务器主机地址
            port: RCON 端口号
            password: RCON 密码
            timeout: 连接超时时间

        Returns:
            服务器配置对象
        """
        # 优先使用命令行参数
        if host and port and password:
            return ServerConfig(
                host=host,
                port=port,
                password=password,
                timeout=timeout or 10.0
            )

        # 其次使用配置文件中的服务器
        if server_name:
            server_config = self.config.get_server_config(server_name)
            if server_config:
                return server_config
            else:
                self.console.print(f"[red]错误: 未找到服务器 '{server_name}'[/red]")
                return None

        # 最后使用默认服务器
        if self.config.default_server:
            server_config = self.config.get_default_server_config()
            if server_config:
                return server_config

        # 没有可用的配置
        self.console.print("[red]错误: 未指定服务器配置[/red]")
        return None

    def _display_command_result(self, result: CommandResult) -> None:
        """
        显示命令执行结果

        Args:
            result: 命令执行结果
        """
        if result.success:
            # 显示成功的结果
            if result.output.strip():
                self.console.print(f"[green]✓ 命令执行成功 ({result.execution_time:.3f}s)[/green]")
                self.console.print(Panel(
                    result.output,
                    title="输出",
                    border_style="green"
                ))
            else:
                self.console.print(f"[green]✓ 命令执行成功 ({result.execution_time:.3f}s)[/green]")
        else:
            # 显示错误信息
            self.console.print(f"[red]✗ 命令执行失败 ({result.execution_time:.3f}s)[/red]")
            if result.error:
                self.console.print(f"[red]错误: {result.error}[/red]")
            if result.output.strip():
                self.console.print(Panel(
                    result.output,
                    title="输出",
                    border_style="red"
                ))

    def _list_servers(self) -> None:
        """
        列出所有配置的服务器
        """
        servers = self.config.list_servers()
        if not servers:
            self.console.print("[yellow]没有配置任何服务器[/yellow]")
            return

        self.console.print("配置的服务器:")
        for i, server_name in enumerate(servers, 1):
            server_config = self.config.get_server_config(server_name)
            is_default = server_name == self.config.default_server
            default_mark = " (默认)" if is_default else ""

            description = server_config.description or "无描述"
            self.console.print(
                f"  {i}. [cyan]{server_name}[/cyan]{default_mark}"
                f" - {server_config.host}:{server_config.port} - {description}"
            )


# CLI 命令定义
@click.group()
@click.version_option(version="0.1.0", prog_name="McRconToolPlus")
@click.option(
    '--config', '-c',
    type=click.Path(exists=True, path_type=Path),
    help='配置文件路径'
)
@click.pass_context
def cli(ctx, config):
    """
    McRconToolPlus - 功能强大的 Minecraft RCON 工具

    一个美观、易用的 Minecraft 服务器远程控制工具。
    """
    ctx.ensure_object(dict)
    ctx.obj['config_manager'] = ConfigManager(config)


@cli.command()
@click.argument('command', required=True)
@click.option(
    '--server', '-s',
    help='服务器名称（来自配置文件）'
)
@click.option(
    '--host',
    help='服务器主机地址'
)
@click.option(
    '--port', type=int,
    help='RCON 端口号'
)
@click.option(
    '--password',
    help='RCON 密码'
)
@click.option(
    '--timeout', type=float, default=10.0,
    help='连接超时时间（秒）'
)
@click.pass_context
def execute(ctx, command, server, host, port, password, timeout):
    """
    执行单个命令

    COMMAND: 要执行的命令字符串
    """
    async def run():
        app = McRconApp(ctx.obj['config_manager'])
        await app.initialize()
        success = await app.execute_single_command(
            command, server, host, port, password, timeout
        )
        sys.exit(0 if success else 1)

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(130)


@cli.command()
@click.pass_context
def interactive(ctx):
    """
    启动交互式界面

    进入交互式命令行界面，支持命令历史和自动补全。
    """
    async def run():
        app = McRconApp(ctx.obj['config_manager'])
        await app.initialize()
        self.console.print("[yellow]交互式界面暂未实现，请使用 execute 命令[/yellow]")
        self.console.print("示例: mcrcon-tool-plus execute \"list\"")

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(130)


@cli.command()
@click.pass_context
def servers(ctx):
    """
    列出所有配置的服务器
    """
    async def run():
        app = McRconApp(ctx.obj['config_manager'])
        await app.initialize()
        app._list_servers()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(130)


@cli.command()
@click.argument('server_name', required=True)
@click.option(
    '--host', required=True,
    help='服务器主机地址'
)
@click.option(
    '--port', type=int, required=True,
    help='RCON 端口号'
)
@click.option(
    '--password', required=True,
    help='RCON 密码'
)
@click.option(
    '--description',
    help='服务器描述'
)
@click.option(
    '--timeout', type=float, default=10.0,
    help='连接超时时间（秒）'
)
@click.option(
    '--default', is_flag=True,
    help='设置为默认服务器'
)
@click.pass_context
def add_server(
    ctx, server_name, host, port, password, description, timeout, default
):
    """
    添加服务器配置

    SERVER_NAME: 服务器名称
    """
    try:
        config_manager = ctx.obj['config_manager']
        config = config_manager.get_config()

        # 创建服务器配置
        server_config = ServerConfig(
            host=host,
            port=port,
            password=password,
            description=description,
            timeout=timeout
        )

        # 添加到配置
        config.add_server(server_name, server_config)

        # 设置为默认服务器
        if default:
            config.default_server = server_name

        # 保存配置
        config_manager.save_config()

        click.echo(f"服务器 '{server_name}' 已添加成功")
        if default:
            click.echo(f"'{server_name}' 已设置为默认服务器")

    except Exception as e:
        click.echo(f"添加服务器失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('server_name', required=True)
@click.pass_context
def remove_server(ctx, server_name):
    """
    删除服务器配置

    SERVER_NAME: 服务器名称
    """
    try:
        config_manager = ctx.obj['config_manager']
        config = config_manager.get_config()

        # 删除服务器配置
        if config.remove_server(server_name):
            config_manager.save_config()
            click.echo(f"服务器 '{server_name}' 已删除")
        else:
            click.echo(f"未找到服务器 '{server_name}'", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"删除服务器失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def ping(ctx):
    """
    测试默认服务器连接
    """
    async def run():
        try:
            config_manager = ctx.obj['config_manager']
            config = config_manager.get_config()

            # 获取默认服务器配置
            if not config.default_server:
                click.echo("未设置默认服务器", err=True)
                sys.exit(1)

            server_config = config.get_default_server_config()
            if not server_config:
                click.echo("默认服务器配置不存在", err=True)
                sys.exit(1)

            # 创建客户端并测试连接
            client = RconClient(
                host=server_config.host,
                port=server_config.port,
                password=server_config.password
            )

            async with client:
                latency = await client.ping()
                click.echo(f"连接成功！延迟: {latency:.2f}ms")

        except Exception as e:
            click.echo(f"Ping 失败: {e}", err=True)
            sys.exit(1)

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        sys.exit(130)


def main():
    """
    主入口函数
    """
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        click.echo(f"程序发生错误: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()