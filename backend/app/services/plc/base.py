import socket
from abc import ABC, abstractmethod
from typing import Any
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType

class BasePLCService(ABC):
    def __init__(self):
        self.is_connected = False

    @abstractmethod
    def connect(self, req: PLCConnectRequest) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    def check_port_busy(self, ip: str, port: int) -> dict:
        """
        Check port status on the given IP address.
        Returns detailed status information.
        """
        result = {
            'busy': False,
            'status': 'unknown',
            'message': '',
            'response_time': None
        }
        
        try:
            import time
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            connect_result = sock.connect_ex((ip, port))
            response_time = time.time() - start_time
            
            sock.close()
            
            result['response_time'] = round(response_time * 1000, 2)  # ms
            
            if connect_result == 0:
                result['busy'] = True
                result['status'] = 'open'
                result['message'] = f'Port {port} is open and accepting connections'
            else:
                result['busy'] = False
                result['status'] = 'closed'
                result['message'] = f'Port {port} is closed or filtered'
                
        except socket.timeout:
            result['status'] = 'timeout'
            result['message'] = f'Port {port} check timed out'
        except socket.gaierror:
            result['status'] = 'dns_error'
            result['message'] = f'Invalid IP address: {ip}'
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'Port check failed: {str(e)}'
        
        return result

    @abstractmethod
    def read(self, req: PLCReadRequest) -> Any:
        pass

    @abstractmethod
    def write(self, req: PLCWriteRequest) -> bool:
        pass
