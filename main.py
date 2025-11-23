#!/usr/bin/env python3
"""
McRconToolPlus 主入口文件

这个文件是 McRconToolPlus 的主入口，提供命令行接口。
"""

import asyncio
import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from mcrcon_tool_plus.cli import main

if __name__ == "__main__":
    # 运行主程序
    main()