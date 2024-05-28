from bson import ObjectId, errors
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import mongo

class Group:
    @staticmethod
    def create_group(name):
        group = {
            "name": name,
            "users": []
        }
        result = mongo.db.groups.insert_one(group)
        return result.inserted_id

    @staticmethod
    def find_group_by_id(group_id):
        try:
            return mongo.db.groups.find_one({"_id": ObjectId(group_id)})
        except errors.InvalidId:
            return None

    @staticmethod
    def find_group_by_name(name):
        return mongo.db.groups.find_one({"name": name})

    @staticmethod
    def add_user_to_group(group_id, user_id):
        try:
            mongo.db.groups.update_one({"_id": ObjectId(group_id)}, {"$addToSet": {"users": user_id}})
        except errors.InvalidId:
            pass

class User(UserMixin):
    def __init__(self, email, username, password, superuser=False, group_id=None, profile_image=None):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)
        self.superuser = superuser
        self.group_id = group_id
        self.profile_image = profile_image

    @staticmethod
    def create_user(email, username, password, superuser=False, group_id=None, profile_image=None):
        user = {
            "email": email,
            "username": username,
            "password": generate_password_hash(password),
            "superuser": superuser,
            "group_id": ObjectId(group_id) if group_id else None,
            "profile_image": profile_image
        }
        result = mongo.db.users.insert_one(user)
        return result.inserted_id

    @staticmethod
    def get_user_by_email(email):
        return mongo.db.users.find_one({"email": email})

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return mongo.db.users.find_one({"_id": ObjectId(user_id)})
        except errors.InvalidId:
            return None

    @staticmethod
    def update_user(user_id, update_data):
        try:
            if "password" in update_data:
                update_data["password"] = generate_password_hash(update_data["password"])
            if "group_id" in update_data and update_data["group_id"]:
                update_data["group_id"] = ObjectId(update_data["group_id"])
            mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        except errors.InvalidId:
            pass

    @staticmethod
    def delete_user(user_id):
        try:
            mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        except errors.InvalidId:
            pass

    @staticmethod
    def validate_login(email, password):
        user = User.get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            return user
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self['_id'])