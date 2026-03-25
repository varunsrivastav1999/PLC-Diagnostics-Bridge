#
# SPDX-FileCopyrightText: 2025, FANUC America Corporation
# SPDX-FileCopyrightText: 2025, FANUC CORPORATION
#
# SPDX-License-Identifier: Apache-2.0
#
import logging
from logging.handlers import RotatingFileHandler
from typing import Any
import os


class Logger():
    def initialize(self, app_settings: dict[str, Any]) -> None:
        company = app_settings.get('company', 'FANUC')
        self.logger = logging.getLogger(f'{company}.{__package__}')
        self.logger.setLevel(app_settings.get('log_level', logging.INFO))

        if self.logger.handlers:
            return

        for path_item in app_settings.get('output_path', ['out']):
            log_file = os.path.join(path_item)

        os.makedirs(log_file, exist_ok=True)
        log_file = os.path.join(log_file, f'{__package__}.log')

        handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=app_settings.get('log_max_bytes', 5 * 1024 * 1024),
            backupCount=app_settings.get('log_backup_count', 5),
            encoding='utf-8',
        )

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def get_logger(self) -> logging.Logger:
        return self.logger
