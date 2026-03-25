#
# SPDX-FileCopyrightText: 2025, FANUC America Corporation
# SPDX-FileCopyrightText: 2025, FANUC CORPORATION
#
# SPDX-License-Identifier: Apache-2.0
#
import tomllib
import os
import logging
from typing import Optional

from .logger import Logger
from .robot_controller import RobotController


class LibraryVars():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LibraryVars, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.app_settings = {}
        self.robot_controllers = {}
        self.app_settings = self.load_settings('fxvrlib.toml')
        self.logger = Logger()
        self.logger.initialize(self.app_settings.get('app_settings', {}))
        
    def reload_settings(self):
        new_settings = self.load_settings('fxvrlib.toml')
        if new_settings:
            self.app_settings = new_settings
            self.logger.initialize(self.app_settings.get('app_settings', {}))
        self.logger.get_logger().info(f"APP SETTINGS Reloaded: {self.app_settings}")

    def get_logger(self) -> logging.Logger:
        return self.logger.get_logger()

    def make_output_path_filename(self, filename: str) -> str:
        output_path = ''
        for path_item in self.app_settings.get('output_path', ['out']):
            output_path = os.path.join(path_item)

        return os.path.join(output_path, filename)

    def load_settings(self, file: str) -> dict:
        app_settings = {}
        # Get path relative to this file
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        settings_file = os.path.join(current_file_path, 'config', file)
        
        logging.debug(f"Attempting to load settings from: {settings_file}")

        if os.path.exists(settings_file):
            with open(settings_file, "rb") as f:
                app_settings = tomllib.load(f)
            logging.debug("Successfully loaded settings.")
        else:
            logging.debug("Settings file NOT found.")

        return app_settings

    def get_robot_controller(self, name: str) -> Optional[RobotController]:
        # return existing instance of the robot controller or
        # create and return a new instance
        robot_controller: Optional[RobotController] = None
        for settings in self.app_settings.get('robot_controllers', []):
            if settings.get('name', '').lower() == name.lower():
                robot_controller = RobotController()
                robot_controller.init_from_settings(settings)

        return robot_controller

    def get_robot_controller_by_ip(self, ip_address: str) -> Optional[RobotController]:
        # Search for robot controller by IP address
        robot_controller: Optional[RobotController] = None
        for settings in self.app_settings.get('robot_controllers', []):
            if settings.get('ip_address', '') == ip_address:
                robot_controller = RobotController()
                robot_controller.init_from_settings(settings)
                break

        return robot_controller
