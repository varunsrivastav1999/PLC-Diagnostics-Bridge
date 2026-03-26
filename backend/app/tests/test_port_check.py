import pytest
from unittest.mock import patch, MagicMock
from app.services.plc.mitsubishi import MitsubishiPLCService
from app.schemas.plc import PLCConnectRequest, PLCType


class TestGenericPortCheck:
    """Test suite for generic PLC port checking functionality"""
    
    @pytest.fixture
    def service(self):
        """Create a PLC service instance (using Mitsubishi as a concrete example)"""
        return MitsubishiPLCService()
    
    def test_check_port_busy_port_open(self, service):
        """Test that check_port_busy returns True when port is open"""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect_ex.return_value = 0  # Connection successful
            
            result = service.check_port_busy('192.168.1.100', 5000)
            
            assert result['busy'] is True
            assert result['status'] == 'open'
            mock_sock_instance.connect_ex.assert_called_once_with(('192.168.1.100', 5000))
    
    def test_check_port_busy_port_closed(self, service):
        """Test that check_port_busy returns False when port is closed"""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect_ex.return_value = 1  # Connection refused
            
            result = service.check_port_busy('192.168.1.100', 5000)
            
            assert result['busy'] is False
            assert result['status'] == 'closed'
    
    def test_check_port_busy_exception_handling(self, service):
        """Test that check_port_busy returns False on any exception"""
        with patch('socket.socket') as mock_socket:
            mock_socket.side_effect = Exception("Socket error")
            result = service.check_port_busy('192.168.1.100', 5000)
            assert result['busy'] is False
            assert result['status'] == 'error'

class TestPortCheckAPI:
    """Integration tests for port check with API"""
    
    @pytest.fixture
    def test_client(self):
        """Import and return TestClient for FastAPI"""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_check_port_endpoint_siemens_free(self, test_client):
        """Port closed in low-level check is interpreted as free from UI mapping"""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect_ex.return_value = 1

            payload = {
                "plc_type": "siemens",
                "ip": "192.168.1.100",
                "port": 102
            }
            response = test_client.post("/api/plc/check-port", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['port_busy'] is False
            assert data['port_status'] == 'closed'

    def test_check_port_endpoint_mitsubishi_busy(self, test_client):
        """Port open in low-level check is interpreted as busy from UI mapping"""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.connect_ex.return_value = 0

            payload = {
                "plc_type": "mitsubishi",
                "ip": "192.168.1.100",
                "port": 5000
            }
            response = test_client.post("/api/plc/check-port", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data['port_busy'] is True
            assert data['port_status'] == 'open'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
