from datetime import datetime
from typing import Dict, Any


db = 'rent_house_database.sqlite'

class MaintenanceRequest:
    def __init__(self, data: Dict[str, Any]):
        self.request_id     = data.get('request_id')
        self.tenant_id      = data.get('TenantID')
        self.room_id        = data.get('RoomID')
        self.landlord_id    = data.get('LandlordID')

        # ←– Thêm 3 trường này vào model
        self.room_name      = data.get('room_name')
        self.tenant_name    = data.get('tenant_name')
        self.tenant_phone   = data.get('tenant_phone')

        self.issue_type     = data.get('issue_type')
        self.urgency_level  = data.get('urgency_level')
        self.description    = data.get('description')
        self.contact_phone  = data.get('contact_phone')
        self.available_time = data.get('available_time')
        self.discovery_date = data.get('discovery_date')
        self.image_path     = data.get('image_path')
        self.status         = data.get('status', 'Pending')
        self.created_at     = data.get('created_at', datetime.now().isoformat())
