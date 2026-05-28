#
# Extended features for Manual Settings and GNM/BSC
#
import logging
import xml.etree.ElementTree as ET
import re
from time import monotonic_ns
from typing import Any
from .library_constants import LibraryConstants
from .library_vars import LibraryVars

def get_manual_settings(args: dict[str, Any]) -> list[dict[str, Any]]:
    # Mock dynamic data since exact system variables are not provided yet
    data = []
    manual_type = args.get('manual_type', 'BELL')
    variables = LibraryConstants.MANUAL_SETTINGS_VARS.get(manual_type, LibraryConstants.MANUAL_SETTINGS_VARS['BELL'])
    
    # Mocking 5 channels/items
    for i in range(1, 6):
        kvp = {'channel': i}
        for name in variables:
            kvp[name] = 0.0
        data.append(kvp)
    return data

def set_manual_settings(args: dict[str, Any]) -> bool:
    # Mock save
    return True

def get_gnm_bsc_settings(args: dict[str, Any]) -> list[dict[str, Any]]:
    # Mock dynamic data since exact system variables are not provided yet
    data = []
    for i in range(1, 3): # e.g. 2 pumps/bells
        kvp = {'unit_no': i}
        for name in LibraryConstants.GNM_BSC_VARS:
            kvp[name] = 0.0
        data.append(kvp)
    return data

def set_gnm_bsc_settings(args: dict[str, Any]) -> bool:
    # Mock save
    return True
