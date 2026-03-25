#
# SPDX-FileCopyrightText: 2025, FANUC America Corporation
# SPDX-FileCopyrightText: 2025, FANUC CORPORATION
#
# SPDX-License-Identifier: Apache-2.0
#
from .ftp_client import FtpClient


class RobotController():
    def __init__(self):
        self.name: str = ''
        self.description: str = ''
        self.ip_address: str = ''
        self.ftp_username: str = ''
        self.ftp_password: str = ''
        self.ftp_port: int = 21
        self.version = ''
        self.ftp = None

    def get_ftp(self) -> FtpClient:
        if not self.ftp:
            self.ftp = FtpClient(
                self.ip_address,
                self.ftp_username,
                self.ftp_password,
                self.ftp_port,
            )
        return self.ftp

    def get_name(self) -> str:
        return self.name

    def get_ip_address(self) -> str:
        return self.ip_address

    def init_from_settings(self, controller_settings: dict):
        self.name = controller_settings.get('name', '')
        self.description = controller_settings.get('description', '')
        self.ip_address = controller_settings.get('ip_address', '')
        self.ftp_username = controller_settings.get('ftp_username', 'guest')
        self.ftp_password = controller_settings.get('ftp_password', 'guest')
        self.ftp_port = controller_settings.get('ftp_port', 21)
        self.version = controller_settings.get('version', '')
