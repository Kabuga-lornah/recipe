import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthFrame
from api_handler import RecipeAPI
from database import Database
from text_to_speech import TextToSpeech
from styles import AppStyles
from PIL import Image, ImageTk
import io
import requests

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Management System")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.styles = AppStyles()
        self.api = RecipeAPI()
        self.db = Database()
        self.tts = TextToSpeech()
        self.root.configure(bg=self.styles.background_color)
        
        # Navigation history stack
        self.nav_history = []
        
        self.main_container = tk.Frame(self.root, **self.styles.frame_style)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.show_auth_screen()
    
    def show_auth_screen(self):
        self.nav_history = []
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        self.auth_frame = AuthFrame(
            self.main_container, 
            on_login_success=self.show_main_app,
            **self.styles.frame_style
        )
        self.auth_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_main_app(self, user):
        self.current_user = user
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        self.nav_history.append(('home', None))
        
        # Header with profile and home buttons
        self.header_frame = tk.Frame(self.main_container, bg=self.styles.primary_color)
        self.header_frame.pack(fill=tk.X)
        
        tk.Button(
            self.header_frame,
            text="🏠 Home",
            command=self.show_home_page,
            bg=self.styles.primary_color,
            fg='white',
            borderwidth=0,
            font=self.styles.normal_font
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            self.header_frame,
            text=f"Welcome, {self.current_user['username']}",
            bg=self.styles.primary_color,
            fg='white',
            font=self.styles.header_font,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, expand=True)
        
        tk.Button(
            self.header_frame,
            text="Profile",
            command=self.show_profile_menu,
            bg=self.styles.primary_color,
            fg='white',
            borderwidth=0,
            font=self.styles.normal_font
        ).pack(side=tk.RIGHT, padx=20)
        
        self.content_frame = tk.Frame(self.main_container, **self.styles.frame_style)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.show_home_page()
    
    def show_profile_menu(self):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="View Profile", command=self.show_profile)
        menu.add_command(label="Logout", command=self.logout)
        menu.tk_popup(*self._get_menu_position())
    
    def _get_menu_position(self):
        x = self.root.winfo_rootx() + self.header_frame.winfo_x() + self.header_frame.winfo_width() - 100
        y = self.root.winfo_rooty() + self.header_frame.winfo_y() + self.header_frame.winfo_height()
        return (x, y)
    
    def show_profile(self):
        self.clear_content()
        self.nav_history.append(('profile', None))
        
        tk.Label(self.content_frame, text="Your Profile", font=self.styles.title_font).pack(pady=20)
        
        info_frame = tk.Frame(self.content_frame, **self.styles.frame_style)
        info_frame.pack(pady=20)
        
        tk.Label(info_frame, text=f"Username: {self.current_user['username']}").pack(anchor="w", pady=5)
        tk.Label(info_frame, text=f"Email: {self.current_user['email']}").pack(anchor="w", pady=5)
        tk.Button(
            info_frame,
            text="Logout",
            command=self.logout,
            **{**self.styles.button_style, 'bg': self.styles.error_color}
        ).pack(pady=20)
        
        self._add_back_button(bottom=True)
    
    def show_home_page(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Welcome to Recipe Manager", font=self.styles.title_font).pack(pady=20)
        
        features = [
            {"title": "Search Recipes", "command": self.show_search_page, "color": "#4a6fa5"},
            {"title": "Find by Ingredients", "command": self.show_ingredients_page, "color": "#166088"},
            {"title": "Meal Plan", "command": self.show_meal_plan_page, "color": "#4fc3f7"},
            {"title": "Favorites", "command": self.show_favorites_page, "color": "#388e3c"}
        ]
        
        cards_frame = tk.Frame(self.content_frame, **self.styles.frame_style)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for i, feature in enumerate(features):
            row, col = divmod(i, 3)
            card = tk.Frame(
                cards_frame,
                bg="white",
                bd=1,
                relief=tk.RAISED,
                padx=20,
                pady=20
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            cards_frame.grid_columnconfigure(col, weight=1)
            cards_frame.grid_rowconfigure(row, weight=1)
            
            tk.Label(card, text=feature["title"], font=self.styles.header_font, bg="white", fg=feature["color"]).pack()
            tk.Button(
                card,
                text="Go",
                command=feature["command"],
                bg=feature["color"],
                fg="white",
                **{k:v for k,v in self.styles.button_style.items() if k not in ['bg', 'fg']}
            ).pack(pady=5)
    
    def show_search_page(self):
        self.clear_content()
        self.nav_history.append(('search', None))
        
        tk.Label(self.content_frame, text="Search Recipes", font=self.styles.title_font).pack(pady=10)
        
        search_frame = tk.Frame(self.content_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        self.search_entry = tk.Entry(search_frame, **self.styles.entry_style, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="Search",
            command=self.perform_search,
            **self.styles.button_style
        ).pack(side=tk.LEFT)
        
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        self.results_frame = tk.Frame(self.content_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        self._add_back_button(bottom=True)
    
    def perform_search(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
        
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(self.results_frame, text="Searching...", **self.styles.label_style)
        loading_label.pack(pady=20)
        self.root.update()
        
        results = self.api.search_recipes(query)
        loading_label.destroy()
        
        if not results:
            tk.Label(self.results_frame, text="No recipes found.", **self.styles.label_style).pack(pady=20)
            return
        
        self._display_scrollable_results(results)
    
    def show_ingredients_page(self):
        self.clear_content()
        self.nav_history.append(('ingredients', None))
        
        tk.Label(self.content_frame, text="Find Recipes by Ingredients", font=self.styles.title_font).pack(pady=10)
        
        tk.Label(self.content_frame, text="Enter ingredients (comma separated):").pack()
        
        self.ingredients_entry = tk.Entry(self.content_frame, **self.styles.entry_style, width=60)
        self.ingredients_entry.pack(pady=10)
        
        tk.Button(
            self.content_frame,
            text="Find Recipes",
            command=self.find_by_ingredients,
            **self.styles.button_style
        ).pack(pady=10)
        
        self.ingredients_results_frame = tk.Frame(self.content_frame)
        self.ingredients_results_frame.pack(fill=tk.BOTH, expand=True)
        self.ingredients_entry.bind('<Return>', lambda e: self.find_by_ingredients())
        
        self._add_back_button(bottom=True)
    
    def find_by_ingredients(self):
        ingredients_text = self.ingredients_entry.get()
        if not ingredients_text:
            messagebox.showwarning("Warning", "Please enter some ingredients")
            return
    
        ingredients_clean = ingredients_text.strip()
    
        for widget in self.ingredients_results_frame.winfo_children():
            widget.destroy()
    
        loading_label = tk.Label(self.ingredients_results_frame, text="Searching...", **self.styles.label_style)
        loading_label.pack(pady=20)
        self.root.update()
    
        results = self.api.find_recipes_by_ingredients(ingredients_clean)
        loading_label.destroy()
    
        if not results:
            tk.Label(self.ingredients_results_frame, text="No recipes found with those ingredients.", **self.styles.label_style).pack(pady=20)
            return
    
        self.results_frame = self.ingredients_results_frame
        self._display_scrollable_results(results)

    def show_meal_plan_page(self):
        self.clear_content()
        self.nav_history.append(('meal_plan', None))
        
        tk.Label(self.content_frame, text="Weekly Meal Plan", font=self.styles.title_font).pack(pady=10)
        
        # Search and add meal section
        search_frame = tk.Frame(self.content_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(search_frame, text="Search for a dish:").pack(side=tk.LEFT)
        self.meal_search_entry = tk.Entry(search_frame, **self.styles.entry_style, width=30)
        self.meal_search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="Search",
            command=self.search_meal_for_plan,
            **self.styles.button_style
        ).pack(side=tk.LEFT)
        
        self.meal_search_entry.bind('<Return>', lambda e: self.search_meal_for_plan())
        
        # Meal plan display (7 days)
        self.meal_plan_frame = tk.Frame(self.content_frame)
        self.meal_plan_frame.pack(fill=tk.BOTH, expand=True)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_frames = {}
        self.day_meals = {}
        
        # Load saved meal plan from database
        self.weekly_meals = self.db.get_meal_plan(str(self.current_user['_id']))
        
        for i, day in enumerate(days):
            day_frame = tk.Frame(self.meal_plan_frame, bd=1, relief=tk.RIDGE, padx=10, pady=10)
            day_frame.grid(row=i//3, column=i%3, sticky="nsew", padx=5, pady=5)
            self.meal_plan_frame.grid_columnconfigure(i%3, weight=1)
            self.meal_plan_frame.grid_rowconfigure(i//3, weight=1)
            
            tk.Label(day_frame, text=day, font=self.styles.header_font).pack()
            
            # Check if we have a saved meal for this day
            if day in self.weekly_meals:
                recipe = self.weekly_meals[day]
                meal_text = f"{recipe['title']}\n{recipe.get('readyInMinutes', 'N/A')} min"
                meal_label = tk.Label(
                    day_frame, 
                    text=meal_text, 
                    wraplength=150,
                    cursor="hand2",
                    fg="blue"
                )
                meal_label.bind("<Button-1>", lambda e, r=recipe: self.show_recipe_details(r['id']))
                meal_label.pack()
                self.day_meals[day] = meal_label
            else:
                self.day_meals[day] = tk.Label(day_frame, text="No meal selected", wraplength=150)
                self.day_meals[day].pack()
            
            self.day_frames[day] = day_frame
        
        # Nutrition summary
        self.nutrition_frame = tk.Frame(self.content_frame)
        self.nutrition_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(self.nutrition_frame, text="Weekly Nutrition Summary:", font=self.styles.header_font).pack()
        self.calories_label = tk.Label(self.nutrition_frame, text="Total Calories: 0")
        self.calories_label.pack()
        
        # Calculate nutrition if we have meals
        if self.weekly_meals:
            self.calculate_weekly_nutrition()
        
        self._add_back_button(bottom=True)

    def search_meal_for_plan(self):
        query = self.meal_search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
        
        results = self.api.search_recipes(query)
        if not results:
            messagebox.showinfo("Info", "No recipes found")
            return
        
        popup = tk.Toplevel(self.root)
        popup.title("Select Recipe")
        popup.geometry("400x400")
        
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="Select a day for this recipe:").pack()
        
        day_var = tk.StringVar()
        day_dropdown = ttk.Combobox(scrollable_frame, textvariable=day_var, 
                                   values=list(self.day_frames.keys()))
        day_dropdown.pack(pady=5)
        
        for recipe in results:
            frame = tk.Frame(scrollable_frame, bd=1, relief=tk.RIDGE, padx=5, pady=5)
            frame.pack(fill=tk.X, pady=2)
            
            tk.Label(frame, text=recipe['title'], wraplength=300).pack(anchor="w")
            tk.Label(frame, text=f"{recipe.get('readyInMinutes', 'N/A')} min | {recipe.get('servings', 'N/A')} servings").pack(anchor="w")
            
            tk.Button(
                frame,
                text="Select",
                command=lambda r=recipe: self.add_meal_to_plan(r, day_var.get(), popup),
                **self.styles.button_style
            ).pack(side=tk.RIGHT)

    def add_meal_to_plan(self, recipe, day, popup):
        if not day:
            messagebox.showwarning("Warning", "Please select a day")
            return
        
        # Update the UI
        meal_text = f"{recipe['title']}\n{recipe.get('readyInMinutes', 'N/A')} min"
        meal_label = tk.Label(
            self.day_frames[day], 
            text=meal_text, 
            wraplength=150,
            cursor="hand2",
            fg="blue"
        )
        meal_label.bind("<Button-1>", lambda e, r=recipe: self.show_recipe_details(r['id']))
        meal_label.pack()
        
        # Remove the old label if it exists
        if day in self.day_meals:
            self.day_meals[day].destroy()
        self.day_meals[day] = meal_label
        
        # Save to database
        self.db.save_meal_plan(str(self.current_user['_id']), day, recipe)
        
        # Update weekly meals
        self.weekly_meals[day] = recipe
        
        # Calculate total calories
        self.calculate_weekly_nutrition()
        popup.destroy()

    def calculate_weekly_nutrition(self):
        if not hasattr(self, 'weekly_meals'):
            return
        
        total_calories = 0
        for day, recipe in self.weekly_meals.items():
            if 'nutrition' in recipe and 'nutrients' in recipe['nutrition']:
                for nutrient in recipe['nutrition']['nutrients']:
                    if nutrient['name'] == 'Calories':
                        total_calories += nutrient['amount']
                        break
        
        self.calories_label.config(text=f"Total Calories: {total_calories:.0f}")
    
    def show_favorites_page(self):
        self.clear_content()
        self.nav_history.append(('favorites', None))
        
        tk.Label(self.content_frame, text="Your Favorites", font=self.styles.title_font).pack(pady=10)
        
        favorites = self.db.get_favorites(str(self.current_user['_id']))
        
        if not favorites:
            tk.Label(self.content_frame, text="No favorites yet.", **self.styles.label_style).pack(pady=20)
            return
        
        # Create a dedicated frame for results
        self.favorites_results_frame = tk.Frame(self.content_frame)
        self.favorites_results_frame.pack(fill=tk.BOTH, expand=True)
        
        print(f"DEBUG: Found {len(favorites)} favorites")
        for fav in favorites:
            print(f"DEBUG: Favorite recipe: {fav.get('title', 'No title')} - ID: {fav.get('id', 'No ID')}")
        
        self._display_scrollable_results(favorites, is_favorite=True, container=self.favorites_results_frame)
        
        self._add_back_button(bottom=True)
    
    def _add_back_button(self, bottom=False):
        if len(self.nav_history) > 1:
            button = tk.Button(
                self.content_frame if not bottom else self.results_frame if hasattr(self, 'results_frame') else self.content_frame,
                text="← Back",
                command=self.show_previous_page,
                **self.styles.button_style
            )
            if bottom:
                button.pack(side=tk.BOTTOM, pady=10, padx=10, anchor='se')
            else:
                button.pack(anchor="nw", padx=10, pady=10)
    
    def _display_scrollable_results(self, items, is_favorite=False, is_meal_plan=False, container=None):
        # Use provided container or default to content_frame
        container = container or (self.results_frame if hasattr(self, 'results_frame') else self.content_frame)
        
        # Safely destroy all children widgets
        try:
            for widget in container.winfo_children():
                widget.destroy()
        except tk.TclError as e:
            print(f"DEBUG: Error clearing container: {e}")
            # If there's an error, create a new container
            container = tk.Frame(self.content_frame)
            container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
    
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )   
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
        recipes_frame = tk.Frame(scrollable_frame)
        recipes_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
        print(f"DEBUG: Displaying {len(items)} items, is_favorite={is_favorite}")
    
        if not is_meal_plan:
            for i, item in enumerate(items):
                print(f"DEBUG: Processing item {i}: {item.get('title', 'No title')}")
                
                row, col = divmod(i, 3)
                card = tk.Frame(
                    recipes_frame,
                    bg="white",
                    bd=1,
                    relief=tk.RAISED,
                    padx=10,
                    pady=10
                )
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                recipes_frame.grid_columnconfigure(col, weight=1)
                recipes_frame.grid_rowconfigure(row, weight=1)
            
                title_text = item.get('title', 'Untitled Recipe')
                tk.Label(
                    card,
                    text=title_text,
                    font=self.styles.header_font,
                    wraplength=200,
                    bg="white"
                ).pack(pady=(0, 5))
            
                if item.get('image'):
                    try:
                        response = requests.get(item['image'], stream=True)
                        img = Image.open(io.BytesIO(response.content))
                        img = img.resize((200, 150), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        label = tk.Label(card, image=photo, bg="white")
                        label.image = photo
                        label.pack(pady=5)
                    except Exception as e:
                        print(f"DEBUG: Error loading image: {e}")
                        pass
            
                info_frame = tk.Frame(card, bg="white")
                info_frame.pack(fill="x", pady=5)
            
                tk.Label(
                    info_frame,
                    text=f"⏱️ {item.get('readyInMinutes', 'N/A')} min",
                    bg="white"
                ).pack(side="left")
            
                tk.Label(
                    info_frame,
                    text=f"👨‍🍳 {item.get('servings', 'N/A')} servings",
                    bg="white"
                ).pack(side="right")
            
                btn_frame = tk.Frame(card, bg="white")
                btn_frame.pack(fill="x", pady=(5, 0))
            
                recipe_id = item.get('id') or item.get('recipe_id')
                print(f"DEBUG: Recipe ID for view button: {recipe_id}")
                
                tk.Button(
                    btn_frame,
                    text="View",
                    command=lambda r=item: self.show_recipe_details(r.get('id') or r.get('recipe_id')),
                    **{**self.styles.button_style, 'font': self.styles.small_font}
                ).pack(side="left", expand=True, fill="x", padx=2)
            
                if is_favorite:
                    tk.Button(
                        btn_frame,
                        text="Remove",
                        command=lambda r=item: self.remove_from_favorites(r.get('id') or r.get('recipe_id')),
                        **{**self.styles.button_style, 'bg': self.styles.error_color, 'font': self.styles.small_font}
                    ).pack(side="left", expand=True, fill="x", padx=2)
                else:
                    tk.Button(
                        btn_frame,
                        text="Save",
                        command=lambda r=item: self.add_to_favorites(r),
                        **{**self.styles.button_style, 'bg': self.styles.success_color, 'font': self.styles.small_font}
                    ).pack(side="left", expand=True, fill="x", padx=2)
    
    def show_recipe_details(self, recipe_id):
        self.clear_content()
        self.nav_history.append(('recipe_details', recipe_id))
        
        print(f"DEBUG: Loading recipe details for ID: {recipe_id}")
        
        recipe = self.api.get_recipe_details(recipe_id)
        if not recipe:
            messagebox.showerror("Error", "Could not load recipe details")
            return
        
        details_frame = tk.Frame(self.content_frame, **self.styles.frame_style)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(details_frame, text=recipe.get('title', 'Untitled Recipe'), font=self.styles.title_font).pack(pady=10)
        
        if recipe.get('image'):
            try:
                response = requests.get(recipe['image'], stream=True)
                img = Image.open(io.BytesIO(response.content))
                img = img.resize((300, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(details_frame, image=photo)
                label.image = photo
                label.pack(pady=10)
            except Exception:
                pass
        
        tab_control = ttk.Notebook(details_frame)
        
        # Ingredients Tab
        ingredients_tab = tk.Frame(tab_control)
        self._create_ingredients_tab(ingredients_tab, recipe)
        tab_control.add(ingredients_tab, text='Ingredients')
        
        # Instructions Tab
        instructions_tab = tk.Frame(tab_control)
        self._create_instructions_tab(instructions_tab, recipe)
        tab_control.add(instructions_tab, text='Instructions')
        
        # Nutrition Tab
        nutrition_tab = tk.Frame(tab_control)
        self._create_nutrition_tab(nutrition_tab, recipe)
        tab_control.add(nutrition_tab, text='Nutrition')
        
        tab_control.pack(expand=1, fill="both", padx=5, pady=5)
        
        # Favorite Button
        action_frame = tk.Frame(details_frame)
        action_frame.pack(pady=10)
        
        is_favorite = any(fav['id'] == recipe['id'] for fav in self.db.get_favorites(str(self.current_user['_id'])))

        if is_favorite:
            tk.Button(
                action_frame,
                text="Remove Favorite",
                command=lambda: self.remove_from_favorites(recipe['id']),
                **{**self.styles.button_style, 'bg': self.styles.error_color}
            ).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(
                action_frame,
                text="Add Favorite",
                command=lambda: self.add_to_favorites(recipe),
                **self.styles.button_style
            ).pack(side=tk.LEFT, padx=5)
        
        self._add_back_button(bottom=True)
    
    def _create_ingredients_tab(self, parent, recipe):
        ingredients = recipe.get('extendedIngredients', [])
        if not ingredients:
            tk.Label(parent, text="No ingredients info").pack(pady=20)
            return
        
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for ing in ingredients:
            tk.Label(frame, text=f"• {ing['original']}", wraplength=600, justify=tk.LEFT).pack(anchor="w")
    
    def _create_instructions_tab(self, parent, recipe):
        instructions = recipe.get('instructions')
        analyzed = recipe.get('analyzedInstructions', [])
        
        if not instructions and not analyzed:
            tk.Label(parent, text="No instructions available").pack(pady=20)
            return
        
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # TTS Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            btn_frame,
            text="Read Aloud",
            command=lambda: self.read_instructions(instructions or self._format_instructions(analyzed)),
            **self.styles.button_style
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Stop",
            command=self.tts.stop_speaking,
            **{**self.styles.button_style, 'bg': self.styles.error_color}
        ).pack(side=tk.LEFT, padx=5)
        
        if instructions:
            text = tk.Text(frame, wrap=tk.WORD, height=15)
            text.insert(tk.END, instructions)
            text.config(state=tk.DISABLED)
            text.pack(fill=tk.BOTH, expand=True)
        else:
            for instruction in analyzed:
                tk.Label(frame, text=instruction['name'], font=self.styles.header_font).pack(anchor="w", pady=(10,0))
                for step in instruction['steps']:
                    step_frame = tk.Frame(frame)
                    step_frame.pack(fill=tk.X, pady=2)
                    tk.Label(step_frame, text=f"Step {step['number']}:", font=self.styles.normal_font).pack(side=tk.LEFT)
                    tk.Label(step_frame, text=step['step'], wraplength=600, justify=tk.LEFT).pack(side=tk.LEFT)
    
    def _format_instructions(self, analyzed):
        return "\n".join(
            f"Step {step['number']}: {step['step']}" 
            for instruction in analyzed 
            for step in instruction['steps']
        )
    
    def _create_nutrition_tab(self, parent, recipe):
        nutrients = recipe.get('nutrition', {}).get('nutrients', [])
        if not nutrients:
            tk.Label(parent, text="No nutrition info").pack(pady=20)
            return
        
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(frame, text="Nutrition Information", font=self.styles.header_font).pack(pady=10)
        
        key_nutrients = ['Calories', 'Protein', 'Fat', 'Carbohydrates']
        for nutrient in nutrients:
            if nutrient['name'] in key_nutrients:
                nutrient_frame = tk.Frame(frame)
                nutrient_frame.pack(fill=tk.X, pady=2)
                tk.Label(nutrient_frame, text=f"{nutrient['name']}:").pack(side=tk.LEFT)
                tk.Label(nutrient_frame, text=f"{nutrient['amount']} {nutrient['unit']}").pack(side=tk.RIGHT)
    
    def read_instructions(self, text):
        if not text:
            messagebox.showwarning("Warning", "No instructions to read")
            return
        self.tts.speak(text)
    
    def add_to_favorites(self, recipe):
        if not self.current_user:
            messagebox.showerror("Error", "Login required")
            return
        
        if self.db.add_favorite(str(self.current_user['_id']), recipe):
            messagebox.showinfo("Success", "Added to favorites")
            # Refresh if we're on the favorites page
            if len(self.nav_history) > 0 and self.nav_history[-1][0] == 'favorites':
                self.show_favorites_page()
        else:
            messagebox.showerror("Error", "Failed to add favorite")
    
    def remove_from_favorites(self, recipe_id):
        if not self.current_user:
            messagebox.showerror("Error", "Login required")
            return
        
        if self.db.remove_favorite(str(self.current_user['_id']), recipe_id):
            messagebox.showinfo("Success", "Removed from favorites")
            # Refresh if we're on the favorites page or recipe details page
            if len(self.nav_history) > 0:
                if self.nav_history[-1][0] == 'favorites':
                    self.show_favorites_page()
                elif self.nav_history[-1][0] == 'recipe_details':
                    self.show_recipe_details(recipe_id)
        else:
            messagebox.showerror("Error", "Failed to remove favorite")
    
    def show_previous_page(self):
        if len(self.nav_history) <= 1:
            return
        
        # Remove current page from history
        self.nav_history.pop()
        
        # Get the previous page
        page_type, *args = self.nav_history[-1]
        
        if page_type == 'home':
            self.show_home_page()
        elif page_type == 'profile':
            self.show_profile()
        elif page_type == 'search':
            self.show_search_page()
        elif page_type == 'ingredients':
            self.show_ingredients_page()
        elif page_type == 'meal_plan':
            self.show_meal_plan_page()
        elif page_type == 'favorites':
            self.show_favorites_page()
        elif page_type == 'recipe_details':
            self.show_recipe_details(args[0])
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def logout(self):
        self.current_user = None
        self.tts.stop_speaking()
        self.show_auth_screen()
    
    def cleanup(self):
        """Clean up resources before closing the application"""
        self.tts.stop_speaking()
        self.db.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.protocol("WM_DELETE_WINDOW", app.cleanup)
    root.mainloop()