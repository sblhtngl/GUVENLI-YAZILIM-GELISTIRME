from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return self.role == "admin"

    def is_owner(self):
        return self.role == "owner"

    def is_user(self):
        return self.role == "user"
