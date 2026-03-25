#
# SPDX-FileCopyrightText: 2025, FANUC America Corporation
# SPDX-FileCopyrightText: 2025, FANUC CORPORATION
#
# SPDX-License-Identifier: Apache-2.0
#
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class LibraryConstants:
    # constants based on paint circuit limits
    MAX_SYSTEM_COLOR_NO: ClassVar[int] = 30
    MAX_JOB_NO: ClassVar[int] = 250
    MAX_PRESETS_PER_COLOR: ClassVar[int] = 20
    MAX_CONTROLLER_PRESETS: ClassVar[int] = 5
    MAX_PRESET_OFFSET: ClassVar[int] = 1000

    PRESET_TYPE_BELL: ClassVar[str] = 'BELL'
    PRESET_TYPE_GUN: ClassVar[str] = 'GUN'

    PRESET_NAME_TABLES: ClassVar[dict[str, list[str]]] = {
        PRESET_TYPE_BELL: ['fluid_rate', 'bell_speed', 'shape_air1', 'estat_KV', 'shape_air2'],
        PRESET_TYPE_GUN: ['fluid_rate', 'atom_air', 'fan_air', 'estat_KV'],
    }
