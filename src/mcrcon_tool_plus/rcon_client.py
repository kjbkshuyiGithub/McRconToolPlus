"""
RCON 客户端模块

这个模块实现了异步 RCON 客户端，提供与 Minecraft 服务器的 RCON 连接功能。
包括：
- 异步连接管理
- 认证功能
- 命令执行和响应处理
- 连接状态管理
- 错误处理和重连机制
"""

import asyncio
import socket
import time
from typing import Optional, Union, Callable, Awaitable
from loguru import logger

from .rcon_protocol import (
    RconPacket, RconPacketType, AuthPacket, CommandPacket, ResponsePacket,
    RconError, PacketParseError, create_auth_packet, create_command_packet, parse_packet
)


class AuthenticationError(RconError):
    """认证失败错误"""
    pass


class ConnectionError(RconError):
    """连接错误"""
    pass


class DisconnectedError(RconError):
    """连接已断开错误"""
    pass


class RconClient:
    """
    异步 RCON 客户端

    提供与 Minecraft 服务器 RCON 接口的异步通信功能。
    """

    def __init__(
        self,
        host: str,
        port: int,
        password: str,
        timeout: float = 10.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """
        初始化 RCON 客户端

        Args:
            host: 服务器主机地址
            port: RCON 端口号
            password: RCON 密码
            timeout: 连接超时时间（秒）
            retry_attempts: 连接失败时的重试次数
            retry_delay: 重试之间的延迟时间（秒）
        """
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._packet_id = 0
        self._authenticated = False
        self._connection_lock = asyncio.Lock()
        self._packet_lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return (
            self._reader is not None and
            self._writer is not None and
            not self._writer.is_closing()
        )

    @property
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self._authenticated and self.is_connected

    def _get_next_packet_id(self) -> int:
        """
        获取下一个数据包 ID

        Returns:
            唯一的数据包 ID
        """
        self._packet_id += 1
        return self._packet_id

    async def connect(self) -> None:
        """
        连接到 RCON 服务器并进行认证

        Raises:
            ConnectionError: 连接失败时
            AuthenticationError: 认证失败时
            asyncio.TimeoutError: 连接超时时
        """
        async with self._connection_lock:
            if self.is_connected and self.is_authenticated:
                logger.debug("RCON 客户端已连接且已认证")
                return

            # 关闭现有连接
            await self._close_connection()

            logger.info(f"正在连接到 RCON 服务器 {self.host}:{self.port}")

            # 尝试连接，支持重试
            last_exception = None
            for attempt in range(self.retry_attempts + 1):
                try:
                    # 建立连接
                    self._reader, self._writer = await asyncio.wait_for(
                        asyncio.open_connection(self.host, self.port),
                        timeout=self.timeout
                    )
                    logger.debug("TCP 连接已建立")
                    break

                except (socket.timeout, ConnectionRefusedError, OSError) as e:
                    last_exception = e
                    if attempt < self.retry_attempts:
                        logger.warning(f"连接失败，{self.retry_delay}秒后重试 ({attempt + 1}/{self.retry_attempts + 1}): {e}")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        logger.error(f"连接失败，已达到最大重试次数: {e}")
                        break

            if not self.is_connected:
                raise ConnectionError(f"无法连接到 {self.host}:{self.port}: {last_exception}")

            # 进行认证
            await self._authenticate()

    async def _authenticate(self) -> None:
        """
        执行 RCON 认证

        Raises:
            AuthenticationError: 认证失败时
            asyncio.TimeoutError: 认证超时时
        """
        if not self.is_connected:
            raise ConnectionError("未连接到服务器，无法进行认证")

        packet_id = self._get_next_packet_id()
        auth_packet = create_auth_packet(packet_id, self.password)

        logger.debug("发送认证数据包")

        try:
            # 发送认证数据包
            response_packet = await self._send_packet_and_wait_response(auth_packet)

            # 检查认证结果
            if response_packet.packet_id == -1:
                logger.error("RCON 认证失败：密码错误")
                raise AuthenticationError("RCON 密码错误")

            if response_packet.packet_id != packet_id:
                logger.error(f"RCON 认证失败：数据包 ID 不匹配 (期望: {packet_id}, 收到: {response_packet.packet_id})")
                raise AuthenticationError("认证响应 ID 不匹配")

            self._authenticated = True
            logger.info("RCON 认证成功")

        except asyncio.TimeoutError:
            logger.error("RCON 认证超时")
            await self._close_connection()
            raise
        except Exception as e:
            logger.error(f"RCON 认证过程中发生错误: {e}")
            await self._close_connection()
            raise

    async def execute_command(self, command: str) -> str:
        """
        执行 RCON 命令

        Args:
            command: 要执行的命令

        Returns:
            命令执行结果

        Raises:
            ConnectionError: 连接问题时
            DisconnectedError: 连接已断开时
            asyncio.TimeoutError: 命令执行超时时
        """
        if not self.is_authenticated:
            await self.connect()

        packet_id = self._get_next_packet_id()
        command_packet = create_command_packet(packet_id, command)

        logger.debug(f"执行 RCON 命令: {command}")

        try:
            response_packet = await self._send_packet_and_wait_response(command_packet)

            # 检查响应 ID
            if response_packet.packet_id != packet_id:
                logger.warning(f"响应数据包 ID 不匹配 (期望: {packet_id}, 收到: {response_packet.packet_id})")

            logger.debug(f"命令执行成功，响应长度: {len(response_packet.payload)}")
            return response_packet.payload

        except asyncio.TimeoutError:
            logger.error(f"命令执行超时: {command}")
            await self._close_connection()
            raise
        except Exception as e:
            logger.error(f"命令执行过程中发生错误: {command}, 错误: {e}")
            await self._close_connection()
            raise

    async def _send_packet_and_wait_response(self, packet: RconPacket) -> ResponsePacket:
        """
        发送数据包并等待响应

        Args:
            packet: 要发送的数据包

        Returns:
            响应数据包

        Raises:
            ConnectionError: 连接问题时
            asyncio.TimeoutError: 超时时
        """
        if not self.is_connected:
            raise ConnectionError("未连接到服务器")

        async with self._packet_lock:
            try:
                # 发送数据包
                packet_data = packet.to_bytes()
                self._writer.write(packet_data)
                await self._writer.drain()
                logger.debug(f"数据包已发送，大小: {len(packet_data)} 字节")

                # 读取响应
                response_data = await asyncio.wait_for(
                    self._read_packet_data(),
                    timeout=self.timeout
                )

                # 解析响应
                response_packet = parse_packet(response_data)
                logger.debug(f"收到响应数据包: {response_packet}")
                return ResponsePacket(response_packet.packet_id, response_packet.payload)

            except ConnectionResetError:
                logger.error("连接被服务器重置")
                await self._close_connection()
                raise ConnectionError("连接被服务器重置")
            except OSError as e:
                logger.error(f"网络错误: {e}")
                await self._close_connection()
                raise ConnectionError(f"网络错误: {e}")

    async def _read_packet_data(self) -> bytes:
        """
        读取数据包数据

        Returns:
            完整的数据包字节数据

        Raises:
            ConnectionError: 连接问题时
            PacketParseError: 数据包解析失败时
        """
        if not self.is_connected:
            raise ConnectionError("未连接到服务器")

        # 读取数据包长度（4字节）
        length_data = await self._reader.readexactly(4)
        if len(length_data) != 4:
            raise ConnectionError("无法读取数据包长度")

        packet_length = int.from_bytes(length_data, byteorder='little', signed=True)
        if packet_length < 0:
            raise PacketParseError(f"无效的数据包长度: {packet_length}")

        # 读取剩余数据
        remaining_data = await self._reader.readexactly(packet_length)

        # 组合完整数据包
        return length_data + remaining_data

    async def ping(self) -> float:
        """
        测试连接延迟

        Returns:
            延迟时间（毫秒）

        Raises:
            ConnectionError: 连接问题时
        """
        if not self.is_authenticated:
            await self.connect()

        start_time = time.time()
        try:
            await self.execute_command("time query daytime")
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # 转换为毫秒
            logger.debug(f"RCON ping 成功，延迟: {latency:.2f}ms")
            return latency
        except Exception as e:
            logger.error(f"RCON ping 失败: {e}")
            raise ConnectionError(f"Ping 失败: {e}")

    async def disconnect(self) -> None:
        """
        断开连接
        """
        async with self._connection_lock:
            await self._close_connection()
            logger.info("RCON 连接已断开")

    async def _close_connection(self) -> None:
        """
        关闭内部连接
        """
        self._authenticated = False

        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as e:
                logger.warning(f"关闭写入器时发生错误: {e}")
            finally:
                self._writer = None

        if self._reader:
            try:
                # 不需要显式关闭读取器
                self._reader = None
            except Exception as e:
                logger.warning(f"关闭读取器时发生错误: {e}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()

    def __repr__(self) -> str:
        """返回客户端的字符串表示"""
        status = "已认证" if self.is_authenticated else ("已连接" if self.is_connected else "未连接")
        return f"RconClient({self.host}:{self.port}, status={status})"