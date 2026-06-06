"""Settings screen for application configuration"""
import customtkinter as ctk
import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


class SettingsScreen(ctk.CTkFrame):
    """Screen for application settings"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.config_path = Path("./config/settings.json")
        self._create_widgets()
    
    def _create_widgets(self):
        try:
            # Title
            title = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
            title.pack(pady=20)
            
            # Settings frame (scrollable)
            settings_frame = ctk.CTkScrollableFrame(self)
            settings_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # App settings section
            self._create_section(settings_frame, "Application")
            
            theme_var = ctk.StringVar(value=self.config.get('app', {}).get('theme', 'dark'))
            self._create_setting(settings_frame, "Theme:", theme_var, ["dark", "light"])
            
            lang_var = ctk.StringVar(value=self.config.get('app', {}).get('language', 'en'))
            self._create_setting(settings_frame, "Language:", lang_var, ["en", "sw", "fr", "ar", "es"])
            
            # OCR settings
            self._create_section(settings_frame, "OCR")
            
            ocr_engine = ctk.StringVar(value=self.config.get('ocr', {}).get('engine', 'paddle'))
            self._create_setting(settings_frame, "OCR Engine:", ocr_engine, ["paddle", "tesseract"])
            
            # Speech settings
            self._create_section(settings_frame, "Speech")
            
            voice_var = ctk.StringVar(value=self.config.get('speech', {}).get('voice', 'en_US-amy-medium'))
            self._create_setting(settings_frame, "Voice:", voice_var, ["en_US-amy-medium", "en_GB-alan-medium"])
            
            # Camera settings
            self._create_section(settings_frame, "Camera")
            
            camera_enabled = ctk.IntVar(value=int(self.config.get('camera', {}).get('enabled', True)))
            camera_check = ctk.CTkCheckBox(settings_frame, text="Enable Camera", variable=camera_enabled)
            camera_check.pack(anchor="w", padx=20, pady=5)
            
            # Save button
            save_btn = ctk.CTkButton(settings_frame, text="Save Settings", command=self._save_settings)
            save_btn.pack(padx=20, pady=20)
        
        except Exception as e:
            logger.error(f"Error creating settings screen: {e}")
    
    def _create_section(self, parent, title):
        label = ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(anchor="w", padx=20, pady=(20, 10))
    
    def _create_setting(self, parent, label, var, values):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=20, pady=5)
        
        label_widget = ctk.CTkLabel(frame, text=label, width=150)
        label_widget.pack(side="left", padx=5)
        
        combo = ctk.CTkComboBox(frame, variable=var, values=values)
        combo.pack(side="left", fill="x", expand=True, padx=5)
    
    def _save_settings(self):
        try:
            # Save settings to JSON
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info("Settings saved")
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
