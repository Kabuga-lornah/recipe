import requests
import os
from dotenv import load_dotenv

load_dotenv()

class RecipeAPI:
    def __init__(self):
        self.api_key = os.getenv("SPOONACULAR_KEY", "454d5677aa39414c8f106f81b4999f65")
        self.base_url = "https://api.spoonacular.com"
    
    def search_recipes(self, query):
        url = f"{self.base_url}/recipes/complexSearch"
        params = {
            'apiKey': self.api_key,
            'query': query,
            'number': 10,
            'addRecipeInformation': True
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            print(f"Error searching recipes: {e}")
            return []
    
    def get_recipe_details(self, recipe_id):
        url = f"{self.base_url}/recipes/{recipe_id}/information"
        params = {
            'apiKey': self.api_key,
            'includeNutrition': True
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting recipe details: {e}")
            return None
    
    def find_recipes_by_ingredients(self, ingredients):
        url = f"{self.base_url}/recipes/findByIngredients"
        params = {
            'apiKey': self.api_key,
            'ingredients': ingredients,  # Expecting a comma-separated string
            'number': 10,  # Increased from 5 to get more results
            'ignorePantry': True,
            'ranking': 1
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            recipes = response.json()
        
        # Debug print to see what we're getting
            print(f"Found {len(recipes)} recipes for ingredients: {ingredients}")
        
        # Get detailed information for each recipe
            detailed_recipes = []
            for recipe in recipes:
                details = self.get_recipe_details(recipe['id'])
                if details:
                    detailed_recipes.append(details)
        
            return detailed_recipes
        except requests.RequestException as e:
            print(f"Error finding recipes by ingredients: {e}")
            return []
    
    def generate_meal_plan(self, time_frame='day'):
        url = f"{self.base_url}/mealplanner/generate"
        params = {
            'apiKey': self.api_key,
            'timeFrame': time_frame
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error generating meal plan: {e}")
            return None
