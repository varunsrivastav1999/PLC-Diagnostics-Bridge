#
# SPDX-FileCopyrightText: 2025, FANUC America Corporation
# SPDX-FileCopyrightText: 2025, FANUC CORPORATION
#
# SPDX-License-Identifier: Apache-2.0
#
import logging
from time import monotonic_ns
import xml.etree.ElementTree as ET
import re
from typing import Any
from .utils import save_to_file, ns_to_sec_string
from .library_constants import LibraryConstants
from .library_vars import LibraryVars

def get_color_setup(args: dict[str, Any]) -> list[dict[str, Any]]:
    start_time = monotonic_ns()
    library_vars = LibraryVars()

    robot_controller = None
    if args.get('robot_ip'):
        robot_controller = library_vars.get_robot_controller_by_ip(args['robot_ip'])
    if not robot_controller:
        robot_controller = library_vars.get_robot_controller(args.get('robot_name'))
        
    if not robot_controller:
        raise RuntimeError("Robot controller not found.")

    color_names = LibraryConstants.COLOR_SETUP_VARS

    # Request all colors
    cvr_content = '<XMLCFG>\n<PROG name="PAPS1">\n'
    for color_no in range(1, LibraryConstants.MAX_COLORS + 1):
        for var_name in color_names:
            cvr_content += f'<VAR name="COLOR_DATA.NODEDATA[1].COLORS[{color_no}].{var_name}"/>\n'
    cvr_content += '</PROG>\n</XMLCFG>\n'

    ftp = robot_controller.get_ftp()
    try:
        ftp.connect(args)
        base_filename = 'tmp_colors'
        ftp.put(f'{base_filename}.cvr', cvr_content)
        xvr_content, _ = ftp.get_file_content(f'{base_filename}.xvr')

        # Initialize structure
        color_data = []
        for i in range(LibraryConstants.MAX_COLORS):
            kvp = {'color_no': i + 1}
            for name in color_names:
                kvp[name] = 0.0
            color_data.append(kvp)

        # Parse XML
        root = ET.fromstring(xvr_content)
        nodes = root.findall(".//PROG[@name='PAPS1']/ARRAY")
        if not nodes:
            nodes = root.findall(".//PROG[@name='PAPS1']/VAR")
            
        for node in nodes:
            name = node.get('name') or ''
            match = re.match(r'COLOR_DATA\.NODEDATA\[1\]\.COLORS\[(?P<color>\d+)\]\.(?P<varname>\w+)', name)
            if match:
                color_no = int(match.group('color'))
                varname = match.group('varname')
                if varname in color_names:
                    try:
                        val = float(node.text or 0)
                        color_data[color_no - 1][varname] = val
                    except ValueError:
                        pass

        return color_data

    finally:
        if ftp:
            ftp.disconnect()

def set_color_setup(args: dict[str, Any]) -> bool:
    library_vars = LibraryVars()
    robot_controller = None
    if args.get('robot_ip'):
        robot_controller = library_vars.get_robot_controller_by_ip(args['robot_ip'])
        
    if not robot_controller:
        raise RuntimeError("Robot controller not found.")

    color_names = LibraryConstants.COLOR_SETUP_VARS
    colors_list = args.get('colors', [])

    xvr_content = (
        '<?xml version="1.0" encoding="iso-8859-1"?>\n'
        '<XMLVAR version="V9.40468">\n<PROG name="PAPS1">\n'
    )

    for c_data in colors_list:
        color_no = int(c_data['color_no'])
        for var_name in color_names:
            if var_name in c_data:
                val = float(c_data[var_name])
                xvr_content += f'<VAR name="COLOR_DATA.NODEDATA[1].COLORS[{color_no}].{var_name}" prot="RW">{val}</VAR>\n'

    xvr_content += '</PROG>\n</XMLVAR>\n'
    ftp = robot_controller.get_ftp()

    try:
        ftp.connect(args)
        ftp.put('set_colors.xvr', xvr_content)
        return True
    finally:
        if ftp:
            ftp.disconnect()

def get_color_cycle_time(args: dict[str, Any]) -> list[dict[str, Any]]:
    # Dynamic mock schema similar to get_color_setup for Cycle Times
    start_time = monotonic_ns()
    library_vars = LibraryVars()

    robot_controller = None
    if args.get('robot_ip'):
        robot_controller = library_vars.get_robot_controller_by_ip(args['robot_ip'])
        
    if not robot_controller:
        raise RuntimeError("Robot controller not found.")

    var_names = LibraryConstants.CYCLE_TIME_VARS

    cvr_content = '<XMLCFG>\n<PROG name="PAPS1">\n'
    for color_no in range(1, LibraryConstants.MAX_COLORS + 1):
        for var_name in var_names:
            cvr_content += f'<VAR name="CYCLE_DATA.NODEDATA[1].TIMES[{color_no}].{var_name}"/>\n'
    cvr_content += '</PROG>\n</XMLCFG>\n'

    ftp = robot_controller.get_ftp()
    try:
        ftp.connect(args)
        base_filename = 'tmp_cycle'
        ftp.put(f'{base_filename}.cvr', cvr_content)
        xvr_content, _ = ftp.get_file_content(f'{base_filename}.xvr')

        color_data = []
        for i in range(LibraryConstants.MAX_COLORS):
            kvp = {'color_no': i + 1}
            for name in var_names:
                kvp[name] = 0.0
            color_data.append(kvp)

        root = ET.fromstring(xvr_content)
        nodes = root.findall(".//PROG[@name='PAPS1']/ARRAY")
        if not nodes:
            nodes = root.findall(".//PROG[@name='PAPS1']/VAR")
            
        for node in nodes:
            name = node.get('name') or ''
            match = re.match(r'CYCLE_DATA\.NODEDATA\[1\]\.TIMES\[(?P<color>\d+)\]\.(?P<varname>\w+)', name)
            if match:
                color_no = int(match.group('color'))
                varname = match.group('varname')
                if varname in var_names:
                    try:
                        val = float(node.text or 0)
                        color_data[color_no - 1][varname] = val
                    except ValueError:
                        pass

        return color_data
    finally:
        if ftp:
            ftp.disconnect()
