Recipe Management System
Project Description
The Recipe Management System is a desktop application built using Python's Tkinter library, designed to help users manage recipes, plan meals, and discover new dishes. It integrates with the Spoonacular API for recipe data and uses MongoDB for user authentication, managing favorite recipes, and saving meal plans.

Features
User Authentication: Register new users and log in existing ones.

Recipe Search: Search for recipes by name.

Find by Ingredients: Discover recipes based on ingredients you have.

Weekly Meal Planning: Create and manage a weekly meal plan, with the ability to search for and assign recipes to specific days.

Favorites Management: Save your favorite recipes for quick access and easily remove them when no longer needed.

Recipe Details: View detailed information for each recipe, including ingredients, instructions, and nutritional information.

Text-to-Speech Instructions: Listen to recipe instructions read aloud.

User Profile: View your profile information and log out.

Technologies Used
Python 3

Tkinter: For the graphical user interface.

Requests: To make HTTP requests to the Spoonacular API.

PyMongo: Python driver for MongoDB for database interactions.

python-dotenv: To manage environment variables (API keys, database URI).

Pillow (PIL): For image processing (displaying recipe images).

pyttsx3: For text-to-speech functionality.

Spoonacular API: For accessing a vast database of recipes and food information.

MongoDB: NoSQL database for storing user data, favorite recipes, and meal plans.

Project Structure
main.py: The main application file, responsible for setting up the Tkinter window, navigation, and integrating all other modules.

auth.py: Handles user registration and login functionalities, interacting with the Database module.

api_handler.py: Manages all interactions with the Spoonacular API, including searching for recipes, getting recipe details, and finding recipes by ingredients.

database.py: Provides an interface for interacting with MongoDB, handling user data, storing and retrieving favorite recipes, and managing meal plans.

styles.py: Defines the visual styles and themes for the Tkinter widgets, ensuring a consistent look and feel throughout the application.

text_to_speech.py: Implements text-to-speech capabilities, allowing users to listen to recipe instructions.

Setup and Installation
Prerequisites
Python 3.x installed on your system.

A Spoonacular API Key (you can get one from Spoonacular API).

A MongoDB Atlas URI or a local MongoDB instance.

Steps
Clone the repository (if applicable, or download the project files):

git clone <repository_url>
cd recipe-management-system

(Note: Replace <repository_url> with the actual URL if this project is hosted on Git.)

Create a virtual environment (recommended):

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

Install the required Python packages:

pip install -r requirements.txt

(If you don't have a requirements.txt file, you can create one with the following packages and then run the command above, or install them one by one):

tkinter
requests
pymongo
python-dotenv
Pillow
pyttsx3

Set up Environment Variables:
Create a .env file in the root directory of the project with the following content:

SPOONACULAR_KEY="your_spoonacular_api_key_here"
MONGODB_URI="your_mongodb_connection_string_here"

Replace "your_spoonacular_api_key_here" with your actual Spoonacular API key.

Replace "your_mongodb_connection_string_here" with your MongoDB connection URI (e.g., from MongoDB Atlas).

Run the application:

python main.py

Usage
Login/Register: Upon launching the application, you will be presented with a login/registration screen. Create a new account or log in with existing credentials.

Navigate: After logging in, you will see the main application dashboard with options to:

Search Recipes

Find by Ingredients

Meal Plan

Favorites

View Profile

Search Recipes: Enter a dish name to find relevant recipes.

Find by Ingredients: Input a comma-separated list of ingredients to get recipe suggestions.

Meal Plan: Organize your weekly meals by adding recipes to specific days.

Favorites: Save recipes you like for easy access later.

Recipe Details: Click on a recipe to view its ingredients, instructions (with text-to-speech option), and nutrition information.

Logout: Log out from the profile menu.

Contributing
Contributions are welcome! Please feel free to fork the repository, make improvements, and submit pull requests.

