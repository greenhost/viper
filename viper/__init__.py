# -*- coding: utf-8 -*-
import platform

_system = platform.system()

IS_WIN = True if _system == "Windows" else False
IS_MAC = True if _system == "Darwin" else False
IS_LINUX = True if _system == "Linux" else False
IS_UNIX = IS_MAC or IS_LINUX
