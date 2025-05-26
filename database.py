from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb+srv://wangarilornah:8f5DuLdsRbKVlLXc@cluster0.pe3akmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.client = MongoClient(self.uri)
        self.db = self.client['recipe_app']
        self.users = self.db['users']
        self.favorites = self.db['favorites']
    
    def add_user(self, username, email, password):
        try:
            if self.users.find_one({'email': email}):
                return False, "Email already exists"
            user_data = {
                'username': username,
                'email': email,
                'password': password  
            }
            self.users.insert_one(user_data)
            return True, "User registered successfully"
        except PyMongoError as e:
            return False, f"Database error: {str(e)}"
    
    def authenticate_user(self, username, password):
        try:
            user = self.users.find_one({'username': username, 'password': password})
            return user is not None, user
        except PyMongoError as e:
            return False, None
    
    def add_favorite(self, user_id, recipe_data):
        try:
            recipe_data['user_id'] = ObjectId(user_id)
            self.favorites.insert_one(recipe_data)
            return True
        except PyMongoError as e:
            print(f"Error adding favorite: {e}")
            return False
    
    def remove_favorite(self, user_id, recipe_id):
        try:
            result = self.favorites.delete_one({
                'user_id': ObjectId(user_id),
                'id': recipe_id
            })
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error removing favorite: {e}")
            return False
    
    def get_favorites(self, user_id):
        try:
            favorites = list(self.favorites.find({'user_id': ObjectId(user_id)}))
            # Convert ObjectId to string for JSON serialization
            for fav in favorites:
                fav['_id'] = str(fav['_id'])
            return favorites
        except PyMongoError as e:
            print(f"Error getting favorites: {e}")
            return []
    
    def close(self):
        self.client.close()