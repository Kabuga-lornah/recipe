from tkinter import font as tkfont
import tkinter as tk

class AppStyles:
    def __init__(self):
        # Colors
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#166088"
        self.accent_color = "#4fc3f7"
        self.background_color = "#f5f5f5"
        self.text_color = "#333333"
        self.error_color = "#d32f2f"
        self.success_color = "#388e3c"
        
        # Fonts
        self.title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.header_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = tkfont.Font(family="Helvetica", size=12)
        self.small_font = tkfont.Font(family="Helvetica", size=10)
        
        # Button Style
        self.button_style = {
            'bg': self.primary_color,
            'fg': 'white',
            'activebackground': self.secondary_color,
            'activeforeground': 'white',
            'font': self.normal_font,
            'borderwidth': 0,
            'highlightthickness': 0,
            'padx': 15,
            'pady': 8,
            'relief': tk.FLAT
        }
        
        # Entry Style
        self.entry_style = {
            'bg': 'white',
            'fg': self.text_color,
            'font': self.normal_font,
            'borderwidth': 1,
            'relief': tk.SOLID,
            'highlightthickness': 1,
            'highlightcolor': self.accent_color,
            'highlightbackground': '#cccccc'
        }
        
        # Label Style
        self.label_style = {
            'bg': self.background_color,
            'fg': self.text_color,
            'font': self.normal_font
        }
        
        # Frame Style
        self.frame_style = {
            'bg': self.background_color
        }