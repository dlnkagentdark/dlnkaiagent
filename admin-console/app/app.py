#!/usr/bin/env python3
"""
dLNk Admin Console - Main Application
"""

import customtkinter as ctk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.theme import COLORS
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.licenses_view import LicensesView
from views.users_view import UsersView
from views.logs_view import LogsView
from views.tokens_view import TokensView
from views.settings_view import SettingsView
from components.sidebar import Sidebar
from app.auth import AdminAuth
from app.api_client import APIClient
import config


class AdminApp(ctk.CTk):
    """Main Admin Console Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title(config.APP_NAME)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        
        # Configure appearance
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Initialize components
        self.auth = AdminAuth()
        self.api_client = APIClient()
        
        self.current_view = None
        self.is_authenticated = False
        self.admin_data = None
        
        # Check for existing session
        if self.auth.is_authenticated():
            self.admin_data = self.auth.get_session()
            self.is_authenticated = True
            self.show_main_app()
        else:
            self.show_login()
    
    def show_login(self):
        """Show login view"""
        self.clear_views()
        self.login_view = LoginView(self, self.on_login_success)
        self.login_view.pack(fill="both", expand=True)
    
    def on_login_success(self, admin_data):
        """Called when login is successful"""
        self.is_authenticated = True
        self.admin_data = admin_data
        self.show_main_app()
    
    def show_main_app(self):
        """Show main application with sidebar"""
        self.clear_views()
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Create sidebar
        self.sidebar = Sidebar(
            self.main_container,
            on_navigate=self.navigate_to,
            on_logout=self.logout
        )
        self.sidebar.pack(side="left", fill="y")
        
        # Update sidebar with user info
        if self.admin_data:
            self.sidebar.update_user_info(
                self.admin_data.get('username', 'Admin'),
                self.admin_data.get('role', 'admin')
            )
        
        # Create content area
        self.content_area = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS['bg_secondary'],
            corner_radius=0
        )
        self.content_area.pack(side="left", fill="both", expand=True)
        
        # Show dashboard by default
        self.navigate_to("dashboard")
    
    def navigate_to(self, view_name: str):
        """Navigate to a view"""
        # Clear current view
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Update sidebar active state
        self.sidebar.set_active(view_name)
        
        # Create new view
        views = {
            'dashboard': lambda p: DashboardView(p, self.api_client),
            'licenses': lambda p: LicensesView(p, self.api_client),
            'users': lambda p: UsersView(p, self.api_client),
            'logs': lambda p: LogsView(p, self.api_client),
            'tokens': lambda p: TokensView(p, self.api_client),
            'settings': lambda p: SettingsView(p, self.api_client),
        }
        
        view_factory = views.get(view_name)
        if view_factory:
            self.current_view = view_factory(self.content_area)
            self.current_view.pack(fill="both", expand=True, padx=20, pady=20)
    
    def clear_views(self):
        """Clear all views"""
        for widget in self.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Logout and show login"""
        self.auth.logout()
        self.is_authenticated = False
        self.admin_data = None
        self.show_login()
    
    def on_closing(self):
        """Handle window close"""
        self.destroy()


def main():
    """Main entry point"""
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run app
    app = AdminApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
