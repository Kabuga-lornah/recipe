from tkinter import Frame, Label, Entry, Button, messagebox
from database import Database

class AuthFrame(Frame):
    def __init__(self, master, on_login_success, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.db = Database()
        self.on_login_success = on_login_success
        
        self.current_user = None
        
        self.create_widgets()
        self.show_login()
    
    def create_widgets(self):
        # Login Frame
        self.login_frame = Frame(self)
        
        Label(self.login_frame, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.login_email = Entry(self.login_frame)
        self.login_email.grid(row=0, column=1, padx=5, pady=5)
        
        Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.login_password = Entry(self.login_frame, show="*")
        self.login_password.grid(row=1, column=1, padx=5, pady=5)
        
        Button(self.login_frame, text="Login", command=self.handle_login).grid(row=2, column=1, pady=10)
        Button(self.login_frame, text="Register", command=self.show_register).grid(row=3, column=1, pady=5)
        
        # Register Frame
        self.register_frame = Frame(self)
        
        Label(self.register_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.register_username = Entry(self.register_frame)
        self.register_username.grid(row=0, column=1, padx=5, pady=5)
        
        Label(self.register_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.register_email = Entry(self.register_frame)
        self.register_email.grid(row=1, column=1, padx=5, pady=5)
        
        Label(self.register_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.register_password = Entry(self.register_frame, show="*")
        self.register_password.grid(row=2, column=1, padx=5, pady=5)
        
        Button(self.register_frame, text="Register", command=self.handle_register).grid(row=3, column=1, pady=10)
        Button(self.register_frame, text="Back to Login", command=self.show_login).grid(row=4, column=1, pady=5)
    
    def show_login(self):
        self.register_frame.pack_forget()
        self.login_frame.pack(padx=20, pady=20)
    
    def show_register(self):
        self.login_frame.pack_forget()
        self.register_frame.pack(padx=20, pady=20)
    
    def handle_login(self):
        email = self.login_email.get()
        password = self.login_password.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        success, user = self.db.authenticate_user(email, password)
        if success:
            self.current_user = user
            self.on_login_success(user)
        else:
            messagebox.showerror("Error", "Invalid email or password")
    
    def handle_register(self):
        username = self.register_username.get()
        email = self.register_email.get()
        password = self.register_password.get()
        
        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        success, message = self.db.add_user(username, email, password)
        if success:
            messagebox.showinfo("Success", message)
            self.show_login()
        else:
            messagebox.showerror("Error", message)
    
    def get_current_user(self):
        return self.current_user
    
    def cleanup(self):
        self.db.close()