#TODO ?
import sqlite3
from typing import Dict, Any
db = 'rent_house_database.sqlite'

class Tenant:
    def __init__(self, data: Dict[str, Any]):
        self.tenant_id = data.get('TenantID')
        self.fullname = data.get('Fullname')
        self.birth = data.get('Birth')
        self.cccd = data.get('CCCD')
        self.gender = data.get('Gender')
        self.job_title = data.get('JobTitle')
        self.marital_status = data.get('MaritalStatus')  # 'Married', 'Single', 'Other'
        self.email = data.get('Email')
        self.phone_number = data.get('PhoneNumber')
        self.home_address = data.get('HomeAddress')
        self.rent_start_date = data.get('RentStartDate')
        self.rent_end_date = data.get('RentEndDate')
        self.user_id = data.get('UserID')
        self.username = data.get("Username")
        self.created_at = data.get("CreatedAt", None)  # Thêm trường created_at nếu cần



    def to_dict(self):
        """Return tenant information as a dictionary (database field names)"""
        return {
            "TenantID": self.tenant_id,
            "Fullname": self.fullname,
            "Birth": self.birth,
            "CCCD": self.cccd,
            "Gender": self.gender,
            "JobTitle": self.job_title,
            "MaritalStatus": self.marital_status,
            "Email": self.email,
            "PhoneNumber": self.phone_number,
            "HomeAddress": self.home_address,
            "RentStartDate": self.rent_start_date,
            "RentEndDate": self.rent_end_date,
            "UserID": self.user_id
        }
