#
# SPDX-FileCopyrightText: 2025, FANUC America Corporation
# SPDX-FileCopyrightText: 2025, FANUC CORPORATION
#
# SPDX-License-Identifier: Apache-2.0
#
from ftplib import FTP
from io import BytesIO
from time import monotonic_ns
from typing import Optional


class FtpClient():
    def get_ipaddress(self):
        return self.ip_address

    def __init__(self, ip_address: str, username: str, password: str, port: int = 21):
        self.ftp: Optional[FTP] = None
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.port = port

    def connect(self, args: dict):
        if not self.ftp:
            self.ftp = FTP()
            self.ftp.connect(self.ip_address, self.port)
            self.ftp.login(user=self.username, passwd=self.password)

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()
            self.ftp.close()
            self.ftp = None

    def get_file_content(self, remote_file: str) -> tuple[str, int]:
        start_time = monotonic_ns()
        buffer = BytesIO()
        ftp = self.ftp
        if ftp is None:
            raise RuntimeError('FTP client not connected')
        ftp.retrbinary(f"RETR {remote_file}", buffer.write)
        content = buffer.getvalue().decode('ascii')
        duration = monotonic_ns() - start_time
        return content, duration

    def put(self, remote_file: str, file_content: str) -> int:
        start_time = monotonic_ns()
        if not remote_file:
            raise RuntimeError('Controller filename being written not supplied.')

        if not file_content:
            raise RuntimeError('Supplied empty file content to write to controller.')

        buffer = BytesIO()
        buffer.write(file_content.encode('ascii'))
        buffer.seek(0)
        ftp = self.ftp
        if ftp is None:
            raise RuntimeError('FTP client not connected')
        ftp.storbinary(f"STOR {remote_file}", buffer)
        return monotonic_ns() - start_time
