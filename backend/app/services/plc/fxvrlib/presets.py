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
from .utils import get_preset_offset, save_to_file, ns_to_sec_string
from .library_constants import LibraryConstants
from .library_vars import LibraryVars


def get_presets(args: dict[str, Any]) -> list[dict[str, Any]]:
    start_time = monotonic_ns()
    library_vars = LibraryVars()

    # Try to get robot controller by IP first, then by name
    robot_controller = None
    if args.get('robot_ip'):
        robot_controller = library_vars.get_robot_controller_by_ip(args['robot_ip'])
    
    if not robot_controller:
        robot_controller = library_vars.get_robot_controller(args['robot_name'])
        
    if not robot_controller:
        msg = f"Robot controller not found. robot_ip: {args.get('robot_ip')!r}, robot_name: {args.get('robot_name')!r}"
        library_vars.get_logger().error(msg)
        raise RuntimeError(msg)

    # get starting and ending preset KAREL path node offsets
    job_no = int(args['job_no']) if args['job_no'] else 0
    color_no = int(args['color_no']) if args['color_no'] else 0
    preset_type = args['preset_type'] if args['preset_type'] else ''

    if preset_type != LibraryConstants.PRESET_TYPE_BELL and preset_type != LibraryConstants.PRESET_TYPE_GUN:
        msg = 'Preset type not defined. Need to supply preset_type equal to BELL or GUN'
        library_vars.get_logger().error(msg)
        raise RuntimeError(msg)

    # get preset table
    preset_names = LibraryConstants.PRESET_NAME_TABLES[preset_type]
    num_presets = len(preset_names)

    start_offset = get_preset_offset(job_no, color_no, 1)
    ending_offset = get_preset_offset(job_no, color_no, LibraryConstants.MAX_PRESETS_PER_COLOR)
    if library_vars.get_logger().isEnabledFor(logging.DEBUG):
        msg = (
            f"Getting presets starting from: {start_offset!r} to: {ending_offset!r} "
            f"for job: {job_no!r} color_no: {color_no!r}"
        )
        library_vars.get_logger().debug(msg)

    # create CVR then load onto robot so we can ask for corresponding XVR file
    cvr_content = '<XMLCFG>\n<PROG name="PAPS1">\n'
    for offset in range(start_offset, ending_offset + 1):
        for preset_no in range(1, num_presets + 1):
            cvr_content += f'<VAR name="PRESET_DATA.NODEDATA[1].PRESETS[{preset_no},{offset}]"/>\n'
    cvr_content += '</PROG>\n</XMLCFG>\n'

    ftp = robot_controller.get_ftp()

    try:
        # write CVR of what presets are being requested
        ftp.connect(args)
        base_filename = 'tmp_presets'
        filename = base_filename + '.cvr'
        cvr_put_duration = ftp.put(filename, cvr_content)
        if library_vars.get_logger().isEnabledFor(logging.DEBUG):
            path_filename = library_vars.make_output_path_filename('get_' + filename)
            save_to_file(path_filename, cvr_content)

        # read requested presets from controller
        filename = base_filename + '.xvr'
        xvr_content, xvr_get_duration = ftp.get_file_content(filename)
        if library_vars.get_logger().isEnabledFor(logging.DEBUG):
            path_filename = library_vars.make_output_path_filename('get_' + filename)
            save_to_file(path_filename, xvr_content.replace('\r', ''))

        # create return array of preset objects
        preset_data: list[dict[str, Any]] = []
        for i in range(LibraryConstants.MAX_PRESETS_PER_COLOR):
            kvp: dict[str, Any] = {'job_no': job_no, 'color_no': color_no, 'preset_no': (i + 1)}
            for j in range(num_presets):
                kvp[preset_names[j]] = 0.0
            preset_data.append(kvp)

        # build JSON preset objects from controller XML
        root = ET.fromstring(xvr_content)
        nodes = root.findall(".//PROG[@name='PAPS1']/ARRAY")
        for node in nodes:
            name = node.get('name') or ''
            match = re.match(r'PRESET_DATA.NODEDATA\[1\]\.PRESETS\[(?P<preset>\d+),(?P<offset>\d+)\]', name)
            if match:
                preset_no = int(match.group('preset'))
                offset_no = int(match.group('offset')) - start_offset
                try:
                    # guard against missing or malformed text
                    text = node.text or ''
                    value = float(text)
                except (TypeError, ValueError):
                    raise RuntimeError(f'Invalid preset value read from controller: {name!r} value: {text!r}')
                preset_data[offset_no][preset_names[preset_no - 1]] = value

        library_vars.get_logger().debug(preset_data)
        duration = monotonic_ns() - start_time + cvr_put_duration + xvr_get_duration
        msg = (
            f'[get_presets] robot:({robot_controller.get_name()}:{robot_controller.get_ip_address()}) '
            f'duration: {ns_to_sec_string(duration)} sec. '
            f'cvr_put_duration: {ns_to_sec_string(cvr_put_duration)} sec. '
            f'xvr_get_duration: {ns_to_sec_string(xvr_get_duration)} sec.'
        )
        library_vars.get_logger().info(msg)

        return preset_data

    except Exception as e:
        msg = (
            f'Failed to read presets for job_no: {job_no!r} color_no: {color_no!r} '
            f'from robot:({robot_controller.get_name()}:{robot_controller.get_ip_address()}).\n'
            f'ex: {str(e)!r}'
        )
        library_vars.get_logger().error(msg)
        raise
    finally:
        if ftp:
            ftp.disconnect()


def set_presets(args: dict[str, Any]) -> bool:
    start_time = monotonic_ns()
    library_vars = LibraryVars()

    # Try to get robot controller by IP first, then by name
    robot_controller = None
    if args.get('robot_ip'):
        robot_controller = library_vars.get_robot_controller_by_ip(args['robot_ip'])
    
    if not robot_controller:
        robot_controller = library_vars.get_robot_controller(args['robot_name'])
        
    if not robot_controller:
        msg = f"Robot controller not found. robot_ip: {args.get('robot_ip')!r}, robot_name: {args.get('robot_name')!r}"
        library_vars.get_logger().error(msg)
        raise RuntimeError(msg)

    # get starting and ending preset KAREL path node offsets
    job_no = int(args["job_no"]) if args["job_no"] else 0
    color_no = int(args["color_no"]) if args["color_no"] else 0
    preset_type = args['preset_type'] if args['preset_type'] else ''

    if preset_type != LibraryConstants.PRESET_TYPE_BELL and preset_type != LibraryConstants.PRESET_TYPE_GUN:
        msg = 'Preset type not defined. Need to supply preset_type equal to BELL or GUN'
        library_vars.get_logger().error(msg)
        raise RuntimeError(msg)

    start_offset = get_preset_offset(job_no, color_no, 1)
    ending_offset = get_preset_offset(job_no, color_no, LibraryConstants.MAX_PRESETS_PER_COLOR)
    if library_vars.get_logger().isEnabledFor(logging.DEBUG):
        msg = f'Setting presets {start_offset!r} to {ending_offset!r} for job: {job_no!r} color_no: {color_no!r}'
        library_vars.get_logger().debug(msg)

    # get preset table
    preset_names = LibraryConstants.PRESET_NAME_TABLES[preset_type]
    xvr_content = (
        '<?xml version="1.0" encoding="iso-8859-1"?>\n'
        '<XMLVAR version="V9.40468     5/16/2025">\n<PROG name="PAPS1">\n'
    )

    # build XVR by iterating offsets first, then preset indices (matches get_presets ordering)
    for offset in range(start_offset, ending_offset + 1):
        presets_entry = args['presets'][offset - start_offset]
        for index, preset_name in enumerate(preset_names, start=1):
            if not presets_entry.get(preset_name):
                msg = f'Missing preset name: {preset_name!r} for supplied presets[{index}].'
                library_vars.get_logger().error(msg)
                raise RuntimeError(msg)
            value = float(presets_entry.get(preset_name, 0.0))
            xvr_content += (
                f'<ARRAY name="PRESET_DATA.NODEDATA[1].PRESETS[{index},{offset}]" '
                f'prot="RW">{value}</ARRAY>\n'
            )
    xvr_content += '</PROG>\n</XMLVAR>\n'
    ftp = robot_controller.get_ftp()

    try:
        ftp.connect(args)
        # save preset data to file
        filename = 'set_presets.xvr'
        xvr_put_duration = ftp.put(filename, xvr_content)
        if library_vars.get_logger().isEnabledFor(logging.DEBUG):
            path_filename = library_vars.make_output_path_filename(filename)
            save_to_file(path_filename, xvr_content)

        duration = monotonic_ns() - start_time + xvr_put_duration
        msg = (
            f'[set_presets] robot:({robot_controller.get_name()}:{robot_controller.get_ip_address()}) '
            f'duration: {ns_to_sec_string(duration)} sec. '
            f'xvr_put_duration: {ns_to_sec_string(xvr_put_duration)} sec.'
        )
        library_vars.get_logger().info(msg)

        return True

    except Exception as e:
        msg = (
            f'Failed to set presets for job_no: {job_no!r} color_no: {color_no!r} '
            f'off robot: ({robot_controller.get_name()}:{robot_controller.get_ip_address()}).'
            f'\nex: {str(e)!r}'
        )
        library_vars.get_logger().error(msg)
    finally:
        if ftp:
            ftp.disconnect()

    return False
