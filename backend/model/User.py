
class User:
    def __init__(self, username, password, role, user_id=None, is_active=0,created_at=None):
        self.username = username
        self.password = password
        self.role = role
        self.user_id = user_id
        self.is_active = is_active
        self.created_at = created_at

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "user_id": self.user_id,
            "is_active": self.is_active,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            username=data.get("username"),
            password=data.get("password"),
            role=data.get("role"),
            user_id=data.get("user_id"),
            is_active=data.get("is_active", 0),
            created_at=data.get("created_at", None)
        )

