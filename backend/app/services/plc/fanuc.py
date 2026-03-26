import os
from typing import Any
import json
from app.services.plc.base import BasePLCService
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError
from .fxvrlib.library_vars import LibraryVars
from .fxvrlib.presets import get_presets, set_presets

class FanucPLCService(BasePLCService):
    """
    Fanuc PLC Service using official fxvrlib package for Paint Robot Preset management via FTP.
    Address format: 'job_no,color_no,preset_type,preset_no,preset_name'
    Example: '1,1,BELL,1,fluid_rate'
    preset_type must be 'BELL' or 'GUN'.
    preset_name examples for BELL: 'fluid_rate', 'bell_speed', 'shape_air1', 'estat_KV', 'shape_air2'
    """
    def __init__(self):
        super().__init__()
        # Initialize the global singleton settings
        self.library_vars = LibraryVars()

    def connect(self, req: PLCConnectRequest) -> bool:
        try:
            controller = self.library_vars.get_robot_controller_by_ip(req.ip)
            if not controller:
                # Dynamically inject the new IP configuration into the singleton
                settings = {
                    "id": f"dynamic-{req.ip}",
                    "name": f"Robot_{req.ip}",
                    "description": "Dynamically linked via PLC Diagnostics Bridge",
                    "ip_address": req.ip,
                    "ftp_port": req.port if req.port else 21,
                    "ftp_username": "guest",
                    "ftp_password": "guest",
                    "version": "V9.40468"
                }
                
                if 'robot_controllers' not in self.library_vars.app_settings:
                    self.library_vars.app_settings['robot_controllers'] = []
                    
                # Prevent duplicates
                if not any(c.get('ip_address') == req.ip for c in self.library_vars.app_settings['robot_controllers']):
                    self.library_vars.app_settings['robot_controllers'].append(settings)
                    
                    # Persist to TOML file permanently
                    toml_path = os.path.join(os.path.dirname(__file__), 'fxvrlib', 'config', 'fxvrlib.toml')
                    if os.path.exists(toml_path):
                        with open(toml_path, 'a') as f:
                            f.write(f"\n[[robot_controllers]]\n")
                            f.write(f'id = "{settings["id"]}"\n')
                            f.write(f'name = "{settings["name"]}"\n')
                            f.write(f'description = "{settings["description"]}"\n')
                            f.write(f'ip_address = "{settings["ip_address"]}"\n')
                            f.write(f'ftp_port = {settings["ftp_port"]}\n')
                            f.write(f'ftp_username = "{settings["ftp_username"]}"\n')
                            f.write(f'ftp_password = "{settings["ftp_password"]}"\n')
                            f.write(f'version = "{settings["version"]}"\n')
                            
                controller = self.library_vars.get_robot_controller_by_ip(req.ip)
                
            # test FTP connection
            try:
                ftp = controller.get_ftp()
                ftp.connect({}) # we just need to test login
                ftp.disconnect()
            except Exception as e:
                raise PLCConnectionError(f"Fanuc FTP connection failed: {e}")
                
            self.is_connected = True
            self.ip = req.ip
            return True
        except Exception as e:
            self.is_connected = False
            raise PLCConnectionError(f"Fanuc connection failed: {e}")

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def test_connection(self) -> bool:
        if not self.is_connected:
            return False
        try:
            controller = self.library_vars.get_robot_controller_by_ip(self.ip)
            if not controller: return False
            ftp = controller.get_ftp()
            ftp.connect({})
            ftp.disconnect()
            return True
        except Exception:
            self.is_connected = False
            return False

    def _parse_address(self, address: str):
        """Parse address like '1,1,BELL', '1,1,BELL,1', or '1,1,BELL,1,fluid_rate'"""
        parts = address.split(',')
        if len(parts) < 3 or len(parts) > 5:
            raise ValueError("Fanuc address must be in format: 'job_no,color_no,preset_type,[preset_no],[preset_name]' (e.g. '1,1,BELL')")
        job_no = int(parts[0])
        color_no = int(parts[1])
        preset_type = parts[2].upper()
        preset_no = int(parts[3]) if len(parts) > 3 else None
        preset_name = parts[4] if len(parts) > 4 else None
        return job_no, color_no, preset_type, preset_no, preset_name

    def read(self, req: PLCReadRequest) -> Any:
        if not self.is_connected:
            raise PLCReadError("Fanuc not connected")
        try:
            # RAW File / Memory Read (e.g. MD:PAVRPRST.VA or error.ls)
            diagnostic_files = ['errall.ls', 'erract.ls', 'errhist.ls', 'summary.dg', 'logbook.ls']
            addr_lower = req.address.lower()
            if addr_lower in diagnostic_files and ':' not in req.address:
                req.address = f"MD:{req.address}"

            if ':' in req.address or req.address.upper().endswith(('.VA', '.VR', '.DT', '.LS', '.XML', '.TXT', '.DG')):
                controller = self.library_vars.get_robot_controller_by_ip(req.ip)
                if not controller:
                    raise PLCReadError("Controller session lost")

                ftp = controller.get_ftp()
                try:
                    ftp.connect({})
                    content, _ = ftp.get_file_content(req.address)
                    # Ensure content is properly decoded as string
                    if isinstance(content, bytes):
                        content = content.decode('utf-8', errors='replace')
                    return content
                except UnicodeDecodeError as e:
                    raise PLCReadError(f"Failed to decode file content: {e}")
                except Exception as e:
                    raise PLCReadError(f"FTP file read failed: {e}")
                finally:
                    try:
                        ftp.disconnect()
                    except:
                        pass  # Ignore disconnect errors

            # Standard structured PaintTool Preset Read
            job_no, color_no, preset_type, preset_no, preset_name = self._parse_address(req.address)
            
            args = {
                'robot_ip': req.ip,
                'robot_name': None,
                'job_no': job_no,
                'color_no': color_no,
                'preset_type': preset_type
            }
            
            presets = get_presets(args)
            
            # Return full array if no preset_no
            if preset_no is None:
                return presets
                
            # preset_no is 1-indexed (1 to 20), list is 0-indexed
            if preset_no < 1 or preset_no > len(presets):
                raise ValueError(f"Invalid preset_no: {preset_no}. Must be between 1 and {len(presets)}.")
                
            preset_dict = presets[preset_no - 1]
            
            # Return dict if no preset_name
            if preset_name is None:
                return preset_dict
                
            if preset_name not in preset_dict:
                raise ValueError(f"Invalid preset_name: {preset_name}. Available: {list(preset_dict.keys())}")
                
            return preset_dict[preset_name]
            
        except Exception as e:
            raise PLCReadError(f"Fanuc read failed: {e}")

    def write(self, req: PLCWriteRequest) -> bool:
        if not self.is_connected:
            raise PLCWriteError("Fanuc not connected")
        try:
            # RAW File / Memory Write (Upload)
            if ':' in req.address or req.address.upper().endswith(('.VA', '.VR', '.DT', '.LS', '.XML', '.TXT', '.CVR', '.XVR')):
                controller = self.library_vars.get_robot_controller_by_ip(req.ip)
                if not controller:
                    raise PLCWriteError("Controller session lost")
                
                ftp = controller.get_ftp()
                try:
                    ftp.connect({})
                    # Ensure value is string
                    val_str = req.value if isinstance(req.value, str) else str(req.value)
                    ftp.put(req.address, val_str)
                    return True
                finally:
                    ftp.disconnect()

            # Standard structured PaintTool Preset Write
            job_no, color_no, preset_type, preset_no, preset_name = self._parse_address(req.address)
            
            args = {
                'robot_ip': req.ip,
                'robot_name': None,
                'job_no': job_no,
                'color_no': color_no,
                'preset_type': preset_type
            }
            
            # If writing entire structure (3 parts), we assume req.value is the 20-item list
            if preset_no is None:
                if not isinstance(req.value, list) or len(req.value) == 0:
                    raise ValueError("When writing entire preset type block, value must be a list of dicts.")
                
                # Sanitize floats
                sanitized_list = []
                for idx, row in enumerate(req.value):
                    if not isinstance(row, dict):
                        raise ValueError(f"Row {idx} is not a dict.")
                    sanitized_row = {}
                    for k, v in row.items():
                        try:
                            # job_no, color_no, preset_no bypass float requirement conceptually, 
                            # but fxvrlib writes everything as floats in XVR except identifiers.
                            sanitized_row[k] = float(v) if k not in ['job_no', 'color_no', 'preset_no'] else int(v)
                        except (ValueError, TypeError):
                            raise ValueError(f"Invalid numeric value '{v}' for key '{k}' at preset row {idx+1}")
                    sanitized_list.append(sanitized_row)
                    
                args['presets'] = sanitized_list
                if set_presets(args):
                    return True
                raise PLCWriteError("set_presets returned False")
            
            # If writing sub-level, we need to read first
            presets = get_presets(args)
            
            if preset_no < 1 or preset_no > len(presets):
                raise ValueError(f"Invalid preset_no: {preset_no}. Must be between 1 and {len(presets)}.")
                
            if preset_name is None:
                if not isinstance(req.value, dict):
                    raise ValueError("When writing a single preset row, value must be a dict.")
                    
                for k, v in req.value.items():
                    try:
                        req.value[k] = float(v) if k not in ['job_no', 'color_no', 'preset_no'] else int(v)
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid numeric value '{v}' for key '{k}'")
                        
                # update dictionary
                presets[preset_no - 1].update(req.value)
            else:
                preset_dict = presets[preset_no - 1]
                if preset_name not in preset_dict:
                    raise ValueError(f"Invalid preset_name: {preset_name}. Available: {list(preset_dict.keys())}")
                    
                # Update the specific value
                try:
                    preset_dict[preset_name] = float(req.value)
                except (ValueError, TypeError):
                    raise ValueError(f"Value '{req.value}' must be convertible to float for Fanuc presets.")
                
            args['presets'] = presets
            
            # Write back
            if set_presets(args):
                return True
            else:
                raise PLCWriteError("set_presets returned False")
                
        except Exception as e:
            raise PLCWriteError(f"Fanuc write failed: {e}")
