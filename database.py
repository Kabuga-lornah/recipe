from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb+srv://wangarilornah:8f5DuLdsRbKVlLXc@cluster0.pe3akmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.client = MongoClient(self.uri)
        self.db = self.client['recipe_app']
        self.users = self.db['users']
        self.favorites = self.db['favorites']
        self.meal_plans = self.db['meal_plans']
    
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
    
    def authenticate_user(self, email, password):
        try:
            user = self.users.find_one({'email': email, 'password': password})
            if user:
                user['_id'] = str(user['_id'])
                return True, user
            return False, None
        except PyMongoError as e:
            print(f"Authentication error: {e}")
            return False, None
    
    def add_favorite(self, user_id, recipe_data):
        try:
            # Get the recipe ID
            recipe_id = recipe_data.get('id', recipe_data.get('recipe_id'))
            
            # Check if already favorited to avoid duplicates
            existing = self.favorites.find_one({
                'user_id': ObjectId(user_id),
                '$or': [
                    {'recipe_id': recipe_id},
                    {'id': recipe_id}
                ]
            })
            
            if existing:
                print("Recipe already in favorites")
                return True  # Return success since it's already favorited
            
            # Create properly formatted favorite document
            favorite_doc = {
                'title': recipe_data.get('title', 'Untitled Recipe'),
                'recipe_id': recipe_id,
                'user': user_id,  # Using string user_id as expected by schema
                'user_id': ObjectId(user_id),  # Keep this for backward compatibility
                'created_at': datetime.utcnow(),
                # Include all the recipe data for easy access - ensure 'id' field is present
                'id': recipe_id,  # This is crucial for the UI to work
                'image': recipe_data.get('image'),
                'readyInMinutes': recipe_data.get('readyInMinutes'),
                'servings': recipe_data.get('servings'),
                'summary': recipe_data.get('summary'),
                'instructions': recipe_data.get('instructions'),
                'extendedIngredients': recipe_data.get('extendedIngredients', []),
                'nutrition': recipe_data.get('nutrition', {}),
                # Add any other fields that might be needed for display
                'sourceUrl': recipe_data.get('sourceUrl'),
                'sourceName': recipe_data.get('sourceName'),
                'dishTypes': recipe_data.get('dishTypes', []),
                'cuisines': recipe_data.get('cuisines', []),
                'diets': recipe_data.get('diets', []),
                'occasions': recipe_data.get('occasions', [])
            }
            
            self.favorites.insert_one(favorite_doc)
            print(f"Successfully added recipe {recipe_id} to favorites")
            return True
        except PyMongoError as e:
            print(f"Error adding favorite: {e}")
            return False
    
    def remove_favorite(self, user_id, recipe_id):
        try:
            # Try both possible field names for recipe_id
            result = self.favorites.delete_one({
                'user_id': ObjectId(user_id),
                '$or': [
                    {'id': recipe_id},
                    {'recipe_id': recipe_id}
                ]
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
                fav['user_id'] = str(fav['user_id'])
            return favorites
        except PyMongoError as e:
            print(f"Error getting favorites: {e}")
            return []
    
    def save_meal_plan(self, user_id, day, recipe_data):
        try:
            # Update or insert meal plan for specific day and user
            self.meal_plans.update_one(
                {'user_id': ObjectId(user_id), 'day': day},
                {'$set': {
                    'user_id': ObjectId(user_id),
                    'day': day,
                    'recipe': recipe_data
                }},
                upsert=True
            )
            return True
        except PyMongoError as e:
            print(f"Error saving meal plan: {e}")
            return False
    
    def get_meal_plan(self, user_id):
        try:
            meal_plans = list(self.meal_plans.find({'user_id': ObjectId(user_id)}))
            # Convert ObjectId to string and organize by day
            meal_plan_dict = {}
            for plan in meal_plans:
                plan['_id'] = str(plan['_id'])
                meal_plan_dict[plan['day']] = plan['recipe']
            return meal_plan_dict
        except PyMongoError as e:
            print(f"Error getting meal plan: {e}")
            return {}
    
    def remove_meal_plan(self, user_id, day):
        try:
            result = self.meal_plans.delete_one({
                'user_id': ObjectId(user_id),
                'day': day
            })
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error removing meal plan: {e}")
            return False
    
    def close(self):
        self.client.close()