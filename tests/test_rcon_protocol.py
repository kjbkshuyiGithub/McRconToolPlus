"""
RCON 协议模块测试

测试 RCON 协议的数据包构建、解析和错误处理功能。
"""

import pytest
from mcrcon_tool_plus.rcon_protocol import (
    RconPacket, RconPacketType, AuthPacket, CommandPacket, ResponsePacket,
    create_auth_packet, create_command_packet, parse_packet,
    RconError, PacketParseError, InvalidPacketTypeError
)


class TestRconPacket:
    """RCON 数据包测试"""

    def test_basic_packet_creation(self):
        """测试基本数据包创建"""
        packet = RconPacket(123, RconPacketType.COMMAND_VALUE, "test command")
        assert packet.packet_id == 123
        assert packet.packet_type == RconPacketType.COMMAND_VALUE
        assert packet.payload == "test command"

    def test_empty_packet_creation(self):
        """测试空数据包创建"""
        packet = RconPacket(1, RconPacketType.RESPONSE_VALUE)
        assert packet.packet_id == 1
        assert packet.packet_type == RconPacketType.RESPONSE_VALUE
        assert packet.payload == ""

    def test_packet_serialization(self):
        """测试数据包序列化"""
        packet = RconPacket(42, RconPacketType.COMMAND_VALUE, "list")
        data = packet.to_bytes()

        # 检查数据长度
        assert len(data) == 4 + 4 + 4 + 4 + 2 + 2  # 长度 + ID + 类型 + "list" + null + null

    def test_packet_serialization_with_chinese(self):
        """测试包含中文字符的数据包序列化"""
        packet = RconPacket(1, RconPacketType.COMMAND_VALUE, "测试命令")
        data = packet.to_bytes()

        # 验证序列化不会出错
        assert len(data) > 0

    def test_packet_serialization_invalid_type(self):
        """测试无效数据包类型"""
        packet = RconPacket(1, 999, "test")  # 999 不是有效的类型
        with pytest.raises(InvalidPacketTypeError):
            packet.to_bytes()

    def test_packet_deserialization(self):
        """测试数据包反序列化"""
        # 创建原始数据包
        original = RconPacket(123, RconPacketType.COMMAND_VALUE, "test payload")

        # 序列化和反序列化
        data = original.to_bytes()
        parsed = RconPacket.from_bytes(data)

        # 验证结果
        assert parsed.packet_id == original.packet_id
        assert parsed.packet_type == original.packet_type
        assert parsed.payload == original.payload

    def test_packet_deserialization_empty_payload(self):
        """测试空载荷数据包反序列化"""
        original = RconPacket(1, RconPacketType.RESPONSE_VALUE)
        data = original.to_bytes()
        parsed = RconPacket.from_bytes(data)

        assert parsed.packet_id == 1
        assert parsed.packet_type == RconPacketType.RESPONSE_VALUE
        assert parsed.payload == ""

    def test_packet_deserialization_invalid_length(self):
        """测试无效长度数据包"""
        # 数据太短
        with pytest.raises(PacketParseError):
            RconPacket.from_bytes(b"short")

    def test_packet_deserialization_mismatched_length(self):
        """测试长度不匹配的数据包"""
        # 手动构造错误的数据包
        data = b"\x0a\x00\x00\x00"  # 声明长度为 10
        data += b"\x01\x00\x00\x00"  # ID = 1
        data += b"\x03\x00\x00\x00"  # Type = 3 (AUTH)
        # 只添加很少的数据，使实际长度与声明长度不匹配

        with pytest.raises(PacketParseError):
            RconPacket.from_bytes(data)


class TestSpecializedPackets:
    """专用数据包测试"""

    def test_auth_packet(self):
        """测试认证数据包"""
        packet = AuthPacket(123, "password123")
        assert packet.packet_id == 123
        assert packet.packet_type == RconPacketType.AUTH_VALUE
        assert packet.payload == "password123"

    def test_command_packet(self):
        """测试命令数据包"""
        packet = CommandPacket(456, "say hello")
        assert packet.packet_id == 456
        assert packet.packet_type == RconPacketType.COMMAND_VALUE
        assert packet.payload == "say hello"

    def test_response_packet(self):
        """测试响应数据包"""
        packet = ResponsePacket(789, "OK")
        assert packet.packet_id == 789
        assert packet.packet_type == RconPacketType.RESPONSE_VALUE
        assert packet.payload == "OK"

    def test_response_packet_empty(self):
        """测试空响应数据包"""
        packet = ResponsePacket(1)
        assert packet.packet_id == 1
        assert packet.packet_type == RconPacketType.RESPONSE_VALUE
        assert packet.payload == ""


class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_create_auth_packet(self):
        """测试创建认证数据包便捷函数"""
        packet = create_auth_packet(42, "secret")
        assert isinstance(packet, AuthPacket)
        assert packet.packet_id == 42
        assert packet.payload == "secret"

    def test_create_command_packet(self):
        """测试创建命令数据包便捷函数"""
        packet = create_command_packet(100, "help")
        assert isinstance(packet, CommandPacket)
        assert packet.packet_id == 100
        assert packet.payload == "help"

    def test_parse_packet(self):
        """测试解析数据包便捷函数"""
        # 创建原始数据包
        original = RconPacket(5, RconPacketType.COMMAND_VALUE, "status")
        data = original.to_bytes()

        # 使用便捷函数解析
        parsed = parse_packet(data)

        assert parsed.packet_id == original.packet_id
        assert parsed.packet_type == original.packet_type
        assert parsed.payload == original.payload


class TestPacketRepresentation:
    """数据包表示测试"""

    def test_packet_repr(self):
        """测试数据包字符串表示"""
        packet = RconPacket(123, RconPacketType.COMMAND_VALUE, "test command")
        repr_str = repr(packet)

        assert "RconPacket" in repr_str
        assert "id=123" in repr_str
        assert "type=COMMAND_VALUE" in repr_str
        assert "payload_length=" in repr_str

    def test_auth_packet_repr(self):
        """测试认证数据包字符串表示"""
        packet = AuthPacket(1, "password")
        repr_str = repr(packet)

        assert "RconPacket" in repr_str
        assert "id=1" in repr_str
        assert "type=AUTH_VALUE" in repr_str


class TestEdgeCases:
    """边界情况测试"""

    def test_large_payload(self):
        """测试大载荷数据包"""
        # 创建一个很大的载荷
        large_payload = "x" * 10000
        packet = RconPacket(1, RconPacketType.COMMAND_VALUE, large_payload)

        # 序列化和反序列化
        data = packet.to_bytes()
        parsed = RconPacket.from_bytes(data)

        assert parsed.payload == large_payload

    def test_unicode_characters(self):
        """测试 Unicode 字符"""
        unicode_payload = "测试 🎮 Minecraft"
        packet = RconPacket(1, RconPacketType.COMMAND_VALUE, unicode_payload)

        data = packet.to_bytes()
        parsed = RconPacket.from_bytes(data)

        assert parsed.payload == unicode_payload

    def test_zero_packet_id(self):
        """测试零数据包 ID"""
        packet = RconPacket(0, RconPacketType.COMMAND_VALUE, "test")
        data = packet.to_bytes()
        parsed = RconPacket.from_bytes(data)

        assert parsed.packet_id == 0

    def test_negative_packet_id(self):
        """测试负数据包 ID"""
        packet = RconPacket(-1, RconPacketType.COMMAND_VALUE, "test")
        data = packet.to_bytes()
        parsed = RconPacket.from_bytes(data)

        assert parsed.packet_id == -1