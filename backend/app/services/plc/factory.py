from app.schemas.plc import PLCType
from app.services.plc.base import BasePLCService

def get_plc_service(plc_type: PLCType) -> BasePLCService:
    if plc_type == PLCType.siemens:
        from app.services.plc.siemens import SiemensPLCService
        return SiemensPLCService()
    elif plc_type == PLCType.mitsubishi:
        from app.services.plc.mitsubishi import MitsubishiPLCService
        return MitsubishiPLCService()
    elif plc_type == PLCType.rockwell:
        from app.services.plc.rockwell import RockwellPLCService
        return RockwellPLCService()
    elif plc_type == PLCType.abb:
        from app.services.plc.abb import ABBPLCService
        return ABBPLCService()
    elif plc_type == PLCType.fanuc:
        from app.services.plc.fanuc import FanucPLCService
        return FanucPLCService()
    else:
        raise ValueError(f"Unsupported PLC type: {plc_type}")
