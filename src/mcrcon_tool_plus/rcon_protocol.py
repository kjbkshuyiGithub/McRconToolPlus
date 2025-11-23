"""
RCON 协议实现模块

这个模块实现了 Minecraft RCON 协议的核心功能，包括：
- RCON 数据包的构建和解析
- 不同类型的数据包（认证、命令、响应）
- 协议常量和枚举
"""

import struct
from enum import IntEnum
from typing import Optional, Tuple, Union


class RconPacketType(IntEnum):
    """RCON 数据包类型枚举"""
    # 服务器响应类型
    RESPONSE_VALUE = 0
    # 客户端命令类型
    COMMAND_VALUE = 2
    # 认证类型
    AUTH_VALUE = 3


class RconError(Exception):
    """RCON 相关错误的基类"""
    pass


class PacketParseError(RconError):
    """数据包解析错误"""
    pass


class InvalidPacketTypeError(RconError):
    """无效的数据包类型错误"""
    pass


class RconPacket:
    """
    RCON 数据包类

    这个类实现了 RCON 协议的数据包格式：
    - 4 字节：数据包长度（Little Endian）
    - 4 字节：请求 ID（Little Endian）
    - 4 字节：类型（Little Endian）
    - 变长：载荷（以 null 结尾的字符串）
    - 1 字节：载荷后的 null 终止符
    - 1 字节：额外的 null 终止符
    """

    def __init__(self, packet_id: int, packet_type: RconPacketType, payload: str = ""):
        """
        初始化 RCON 数据包

        Args:
            packet_id: 数据包 ID，用于匹配请求和响应
            packet_type: 数据包类型
            payload: 数据载荷字符串
        """
        self.packet_id = packet_id
        self.packet_type = packet_type
        self.payload = payload

    def to_bytes(self) -> bytes:
        """
        将数据包序列化为字节格式

        Returns:
            序列化后的字节数据

        Raises:
            InvalidPacketTypeError: 当数据包类型无效时
        """
        # 验证数据包类型
        if not isinstance(self.packet_type, RconPacketType):
            raise InvalidPacketTypeError(f"无效的数据包类型: {self.packet_type}")

        # 编码载荷为 UTF-8
        payload_bytes = self.payload.encode('utf-8')

        # 计算数据包总长度
        # 长度 = 4字节(ID) + 4字节(类型) + 载荷字节 + 2字节(null 终止符)
        total_length = 4 + 4 + len(payload_bytes) + 2

        # 构建数据包
        packet_data = bytearray()

        # 添加数据包长度（不包括长度字段本身）
        packet_data.extend(struct.pack('<i', total_length))

        # 添加请求 ID
        packet_data.extend(struct.pack('<i', self.packet_id))

        # 添加数据包类型
        packet_data.extend(struct.pack('<i', int(self.packet_type)))

        # 添加载荷
        packet_data.extend(payload_bytes)

        # 添加两个 null 终止符
        packet_data.extend(b'\x00\x00')

        return bytes(packet_data)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'RconPacket':
        """
        从字节数据解析 RCON 数据包

        Args:
            data: 原始字节数据

        Returns:
            解析后的 RconPacket 实例

        Raises:
            PacketParseError: 当数据包格式无效时
        """
        if len(data) < 12:  # 最小数据包长度
            raise PacketParseError("数据包长度不足")

        try:
            # 解析数据包长度
            packet_length = struct.unpack('<i', data[0:4])[0]

            # 验证实际长度是否与声明长度匹配
            expected_length = len(data)
            if packet_length != expected_length - 4:  # 减去长度字段本身
                raise PacketParseError(f"数据包长度不匹配: 声明={packet_length}, 实际={expected_length - 4}")

            # 解析请求 ID
            packet_id = struct.unpack('<i', data[4:8])[0]

            # 解析数据包类型
            type_value = struct.unpack('<i', data[8:12])[0]

            try:
                packet_type = RconPacketType(type_value)
            except ValueError:
                raise InvalidPacketTypeError(f"未知的数据包类型: {type_value}")

            # 解析载荷（在两个 null 终止符之前）
            payload_end = data.find(b'\x00\x00', 12)
            if payload_end == -1:
                # 如果找不到双 null，查找单个 null
                payload_end = data.find(b'\x00', 12)
                if payload_end == -1:
                    # 都找不到，使用整个剩余数据
                    payload_end = len(data)

            if payload_end > 12:
                payload_bytes = data[12:payload_end]
                payload = payload_bytes.decode('utf-8', errors='replace')
            else:
                payload = ""

            return cls(packet_id, packet_type, payload)

        except struct.error as e:
            raise PacketParseError(f"数据包解析失败: {e}")

    def __repr__(self) -> str:
        """返回数据包的字符串表示"""
        return (f"RconPacket(id={self.packet_id}, type={self.packet_type.name}, "
                f"payload_length={len(self.payload)})")


class AuthPacket(RconPacket):
    """认证数据包"""

    def __init__(self, packet_id: int, password: str):
        """
        初始化认证数据包

        Args:
            packet_id: 数据包 ID
            password: RCON 密码
        """
        super().__init__(packet_id, RconPacketType.AUTH_VALUE, password)


class CommandPacket(RconPacket):
    """命令数据包"""

    def __init__(self, packet_id: int, command: str):
        """
        初始化命令数据包

        Args:
            packet_id: 数据包 ID
            command: 要执行的命令
        """
        super().__init__(packet_id, RconPacketType.COMMAND_VALUE, command)


class ResponsePacket(RconPacket):
    """响应数据包"""

    def __init__(self, packet_id: int, response: str = ""):
        """
        初始化响应数据包

        Args:
            packet_id: 数据包 ID
            response: 响应内容
        """
        super().__init__(packet_id, RconPacketType.RESPONSE_VALUE, response)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'ResponsePacket':
        """从字节数据创建响应数据包"""
        packet = super().from_bytes(data)
        return cls(packet.packet_id, packet.payload)


def create_auth_packet(packet_id: int, password: str) -> AuthPacket:
    """
    创建认证数据包的便捷函数

    Args:
        packet_id: 数据包 ID
        password: RCON 密码

    Returns:
        认证数据包实例
    """
    return AuthPacket(packet_id, password)


def create_command_packet(packet_id: int, command: str) -> CommandPacket:
    """
    创建命令数据包的便捷函数

    Args:
        packet_id: 数据包 ID
        command: 要执行的命令

    Returns:
        命令数据包实例
    """
    return CommandPacket(packet_id, command)


def parse_packet(data: bytes) -> RconPacket:
    """
    解析数据包的便捷函数

    Args:
        data: 原始字节数据

    Returns:
        解析后的数据包实例

    Raises:
        PacketParseError: 解析失败时
    """
    return RconPacket.from_bytes(data)