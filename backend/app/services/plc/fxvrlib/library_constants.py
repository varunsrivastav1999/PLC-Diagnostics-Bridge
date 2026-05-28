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
    PRESET_TYPE_DISK: ClassVar[str] = 'DISK'
    PRESET_TYPE_APPL: ClassVar[str] = 'APPL'
    PRESET_TYPE_SEALER: ClassVar[str] = 'SEALER'

    PRESET_NAME_TABLES: ClassVar[dict[str, list[str]]] = {
        PRESET_TYPE_BELL: ['fluid_rate', 'bell_speed', 'shape_air1', 'estat_KV', 'shape_air2'],
        PRESET_TYPE_GUN: ['fluid_rate', 'atom_air', 'fan_air', 'estat_KV'],
        PRESET_TYPE_DISK: ['fluid_rate', 'disk_speed', 'shape_air', 'estat_KV'],
        PRESET_TYPE_APPL: ['fluid_rate', 'atom_air', 'fan_air', 'estat_KV'],
        PRESET_TYPE_SEALER: ['fluid_rate', 'pressure', 'estat_KV'],
    }

    MAX_COLORS: ClassVar[int] = 30
    
    COLOR_SETUP_VARS: ClassVar[list[str]] = [
        'purge_time', 'load_time', 'wash_time', 'dry_time', 'fill_time',
        'valve_on_delay', 'valve_off_delay', 'trigger_distance',
        'purge_count', 'atomize_psi',
    ]

    CYCLE_TIME_VARS: ClassVar[list[str]] = [
        'color_change_time', 'avg_cycle_time', 'max_cycle_time',
        'min_cycle_time', 'total_cycles', 'last_cycle_time',
    ]

    # Manual setting variables based on Bell vs Gun selection
    MANUAL_SETTINGS_VARS: ClassVar[dict[str, list[str]]] = {
        'BELL': ['trigger_1', 'trigger_2', 'bell_rpm', 'shape_air1', 'shape_air2', 'cc_valve'],
        'GUN': ['trigger_1', 'trigger_2', 'atomize_air', 'fan_air', 'cc_valve']
    }

    GNM_BSC_VARS: ClassVar[list[str]] = [
        'gnm_speed', 'gnm_feedback', 'bsc_target', 'bsc_feedback', 'pump_pressure'
    ]
