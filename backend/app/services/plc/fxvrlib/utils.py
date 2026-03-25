#
# SPDX-FileCopyrightText: 2025, FANUC America Corporation
# SPDX-FileCopyrightText: 2025, FANUC CORPORATION
#
# SPDX-License-Identifier: Apache-2.0
#
from .library_constants import LibraryConstants
from .library_vars import LibraryVars

import re
import os


def ns_to_sec_string(nanoseconds: int) -> str:
    seconds = nanoseconds / 1_000_000_000
    return f'{seconds:.6f}'


def save_to_file(filename: str, content: str):
    # check whether file exists and delete before writing
    if os.path.exists(filename):
        os.remove(filename)
    # write content to file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


def extract_controller_version(input: str):
    pattern = r'version\s*=\s*"V(?P<major_version>\d+)\.(?P<sub_version>\d+)'
    match = re.match(pattern, input)
    if match:
        return f'{match.group("major_version")}.{match.group("sub_version")}'


def get_preset_offset(job_no: int, color_no: int, preset_no: int) -> int:
    library_vars = LibraryVars()

    # Compute and return the robot controller's preset offset.
    # An exception is throw for invalid arguments
    if job_no <= 0 or job_no > LibraryConstants.MAX_JOB_NO:
        msg = (
            f'Invalid job number supplied. job_no: {job_no!r} '
            f'is not within range: (0 < color_no <= {LibraryConstants.MAX_JOB_NO}).'
        )
        library_vars.get_logger().error(msg)
        raise Exception(msg)

    if color_no <= 0 or color_no > LibraryConstants.MAX_SYSTEM_COLOR_NO:
        msg = (
            f'Invalid color number supplied. color_no: {color_no!r} '
            f'is not within range: (0 < color_no <= {LibraryConstants.MAX_SYSTEM_COLOR_NO}).'
        )
        library_vars.get_logger().error(msg)
        raise Exception(msg)

    if preset_no <= 0 or preset_no > LibraryConstants.MAX_PRESETS_PER_COLOR:
        msg = (
            f'Invalid preset number supplied. preset_no: {preset_no!r} '
            f'is not within range: (0 < preset_no <= {LibraryConstants.MAX_PRESETS_PER_COLOR}).'
        )
        library_vars.get_logger().error(msg)
        raise Exception(msg)

    a = (LibraryConstants.MAX_SYSTEM_COLOR_NO *
         LibraryConstants.MAX_PRESETS_PER_COLOR) * (job_no - 1)
    b = LibraryConstants.MAX_PRESETS_PER_COLOR * (color_no - 1)
    c = a + b + preset_no
    offset = (c - 1) % 1000 + 1

    if offset > LibraryConstants.MAX_PRESET_OFFSET:
        msg = (
            f'Computed offset exceeds maximum offset. offset: {offset!r} '
            f'max_offset: {LibraryConstants.MAX_PRESET_OFFSET!r}.'
        )
        library_vars.get_logger().error(msg)
        raise Exception(msg)

    return offset
