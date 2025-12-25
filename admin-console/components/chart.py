#!/usr/bin/env python3
"""
dLNk Admin Console - Chart Components
"""

import customtkinter as ctk
from utils.theme import COLORS


class StatCard(ctk.CTkFrame):
    """Statistics Card Component"""
    
    def __init__(self, parent, title: str, value: str, color: str = None, 
                 icon: str = None, subtitle: str = None):
        super().__init__(parent, fg_color=COLORS['bg_tertiary'], corner_radius=12)
        
        self.title = title
        self.value = value
        self.color = color or COLORS['success']
        self.icon = icon
        self.subtitle = subtitle
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create card widgets"""
        # Icon (optional)
        if self.icon:
            icon_label = ctk.CTkLabel(
                self,
                text=self.icon,
                font=ctk.CTkFont(size=24),
                text_color=self.color
            )
            icon_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        title_label.pack(anchor="w", padx=20, pady=(15 if not self.icon else 0, 5))
        
        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text=self.value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.color
        )
        self.value_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Subtitle (optional)
        if self.subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=self.subtitle,
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_secondary']
            )
            subtitle_label.pack(anchor="w", padx=20, pady=(0, 20))
        else:
            # Add padding at bottom
            ctk.CTkFrame(self, fg_color="transparent", height=15).pack()
    
    def update_value(self, value: str, color: str = None):
        """Update the displayed value"""
        self.value = value
        self.value_label.configure(text=value)
        if color:
            self.color = color
            self.value_label.configure(text_color=color)


class ChartPlaceholder(ctk.CTkFrame):
    """Placeholder for Chart (can be replaced with matplotlib integration)"""
    
    def __init__(self, parent, title: str, chart_type: str = "line", height: int = 250):
        super().__init__(parent, fg_color=COLORS['bg_tertiary'], corner_radius=12, height=height)
        self.pack_propagate(False)
        
        self.title = title
        self.chart_type = chart_type
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create chart placeholder widgets"""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(anchor="w", padx=20, pady=20)
        
        # Chart area
        chart_area = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=8)
        chart_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Placeholder text
        placeholder = ctk.CTkLabel(
            chart_area,
            text=f"📊 {self.chart_type.title()} Chart\n\nData visualization will appear here",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        placeholder.pack(expand=True)


class ActivityList(ctk.CTkFrame):
    """Recent Activity List Component"""
    
    def __init__(self, parent, title: str = "Recent Activity", activities: list = None):
        super().__init__(parent, fg_color=COLORS['bg_tertiary'], corner_radius=12, width=300)
        self.pack_propagate(False)
        
        self.title = title
        self.activities = activities or []
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create activity list widgets"""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(anchor="w", padx=20, pady=20)
        
        # Activity items container
        self.items_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=COLORS['border'],
            scrollbar_button_hover_color=COLORS['accent']
        )
        self.items_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Populate activities
        self.update_activities(self.activities)
    
    def update_activities(self, activities: list):
        """Update the activity list"""
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        self.activities = activities
        
        if not activities:
            no_activity = ctk.CTkLabel(
                self.items_frame,
                text="No recent activity",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_secondary']
            )
            no_activity.pack(pady=20)
            return
        
        for activity in activities:
            self._create_activity_item(activity)
    
    def _create_activity_item(self, activity):
        """Create a single activity item"""
        if isinstance(activity, dict):
            text = activity.get('text', str(activity))
            time = activity.get('time', '')
            icon = activity.get('icon', '•')
        else:
            text = str(activity)
            time = ''
            icon = '•'
        
        item_frame = ctk.CTkFrame(self.items_frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=3)
        
        # Icon
        icon_label = ctk.CTkLabel(
            item_frame,
            text=icon,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['accent'],
            width=20
        )
        icon_label.pack(side="left", padx=(10, 5))
        
        # Text
        text_label = ctk.CTkLabel(
            item_frame,
            text=text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True)
        
        # Time (optional)
        if time:
            time_label = ctk.CTkLabel(
                item_frame,
                text=time,
                font=ctk.CTkFont(size=10),
                text_color=COLORS['text_secondary']
            )
            time_label.pack(side="right", padx=10)
