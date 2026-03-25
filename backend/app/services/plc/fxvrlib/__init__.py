#
# SPDX-FileCopyrightText: 2025, FANUC America Corporation
# SPDX-FileCopyrightText: 2025, FANUC CORPORATION
#
# SPDX-License-Identifier: Apache-2.0
#
from .presets import get_presets, set_presets
from .library_vars import LibraryVars

# initialize singleton
library_vars = LibraryVars()
__all__ = ['get_presets', 'set_presets']
