#!/usr/bin/env python3
"""
dLNk Admin Console - Dashboard View
"""

import customtkinter as ctk
from utils.theme import COLORS
from components.header import Header
from components.chart import StatCard, ChartPlaceholder, ActivityList


class DashboardView(ctk.CTkFrame):
    """Dashboard View with Statistics and Charts"""
    
    def __init__(self, parent, api_client=None):
        super().__init__(parent, fg_color="transparent")
        
        self.api_client = api_client
        self.stat_cards = {}
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Header
        self.header = Header(self, "Dashboard", on_refresh=self.load_data)
        self.header.pack(fill="x", pady=(0, 20))
        
        # Stats Cards Row
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Configure grid
        for i in range(6):
            stats_frame.columnconfigure(i, weight=1)
        
        # Create stat cards
        stats_config = [
            ("total_licenses", "Total Licenses", "0", COLORS['success'], "🔑"),
            ("active_licenses", "Active Licenses", "0", COLORS['accent'], "✓"),
            ("requests_today", "Requests Today", "0", COLORS['accent_secondary'], "📊"),
            ("active_users", "Active Users", "0", COLORS['success'], "👥"),
            ("blocked_today", "Blocked Today", "0", COLORS['warning'], "🚫"),
            ("pending_alerts", "Pending Alerts", "0", COLORS['error'], "🚨"),
        ]
        
        for i, (key, title, value, color, icon) in enumerate(stats_config):
            card = StatCard(stats_frame, title, value, color, icon)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.stat_cards[key] = card
        
        # Charts Row
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True)
        charts_frame.columnconfigure(0, weight=2)
        charts_frame.columnconfigure(1, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        
        # Usage Chart
        self.usage_chart = ChartPlaceholder(
            charts_frame, 
            "📈 Usage Over Time",
            chart_type="line",
            height=300
        )
        self.usage_chart.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
        
        # Recent Activity
        self.activity_list = ActivityList(
            charts_frame,
            title="📋 Recent Activity",
            activities=[]
        )
        self.activity_list.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
        
        # Bottom Row - Top Users
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(20, 0))
        
        # Top Users Card
        self.top_users_card = ctk.CTkFrame(
            bottom_frame,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=12
        )
        self.top_users_card.pack(fill="x")
        
        # Top Users Header
        ctk.CTkLabel(
            self.top_users_card,
            text="🏆 Top Users Today",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", padx=20, pady=15)
        
        # Top Users Container
        self.top_users_container = ctk.CTkFrame(
            self.top_users_card,
            fg_color="transparent"
        )
        self.top_users_container.pack(fill="x", padx=20, pady=(0, 15))
    
    def load_data(self):
        """Load dashboard data from API"""
        if self.api_client:
            stats = self.api_client.get_dashboard_stats()
        else:
            # Use mock data
            stats = self._get_mock_stats()
        
        self.update_stats(stats)
    
    def _get_mock_stats(self):
        """Get mock statistics data"""
        return {
            'license_stats': {
                'total_licenses': 156,
                'active_licenses': 142,
                'expired_licenses': 10,
                'revoked_licenses': 4,
                'recent_activity': [
                    {'text': 'User john_doe logged in', 'time': '2 min ago', 'icon': '👤'},
                    {'text': 'New license created', 'time': '5 min ago', 'icon': '🔑'},
                    {'text': 'Alert: Suspicious activity', 'time': '10 min ago', 'icon': '⚠️'},
                    {'text': 'Token refreshed', 'time': '15 min ago', 'icon': '🔄'},
                    {'text': 'User jane_smith registered', 'time': '20 min ago', 'icon': '✨'},
                ]
            },
            'c2_stats': {
                'requests_today': 4567,
                'active_users_today': 89,
                'blocked_today': 12,
                'pending_alerts': 3,
                'top_users': [
                    {'user_id': 'john_doe', 'count': 234},
                    {'user_id': 'jane_smith', 'count': 189},
                    {'user_id': 'alice_jones', 'count': 156},
                    {'user_id': 'bob_wilson', 'count': 134},
                    {'user_id': 'charlie_brown', 'count': 98},
                ]
            }
        }
    
    def update_stats(self, stats: dict):
        """Update dashboard with new statistics"""
        license_stats = stats.get('license_stats', {})
        c2_stats = stats.get('c2_stats', {})
        
        # Update stat cards
        self.stat_cards['total_licenses'].update_value(
            f"{license_stats.get('total_licenses', 0):,}"
        )
        self.stat_cards['active_licenses'].update_value(
            f"{license_stats.get('active_licenses', 0):,}"
        )
        self.stat_cards['requests_today'].update_value(
            f"{c2_stats.get('requests_today', 0):,}"
        )
        self.stat_cards['active_users'].update_value(
            f"{c2_stats.get('active_users_today', 0):,}"
        )
        self.stat_cards['blocked_today'].update_value(
            f"{c2_stats.get('blocked_today', 0):,}"
        )
        
        pending = c2_stats.get('pending_alerts', 0)
        self.stat_cards['pending_alerts'].update_value(
            str(pending),
            COLORS['error'] if pending > 0 else COLORS['success']
        )
        
        # Update activity list
        activities = license_stats.get('recent_activity', [])
        self.activity_list.update_activities(activities)
        
        # Update top users
        self._update_top_users(c2_stats.get('top_users', []))
        
        # Update header time
        self.header.update_time()
    
    def _update_top_users(self, top_users: list):
        """Update top users display"""
        # Clear existing
        for widget in self.top_users_container.winfo_children():
            widget.destroy()
        
        if not top_users:
            ctk.CTkLabel(
                self.top_users_container,
                text="No activity today",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_secondary']
            ).pack(pady=10)
            return
        
        # Create header row
        header_frame = ctk.CTkFrame(self.top_users_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="Rank",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_secondary'],
            width=50
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame,
            text="User",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_secondary'],
            width=200
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame,
            text="Requests",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_secondary'],
            width=100
        ).pack(side="left")
        
        # Create user rows
        medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
        
        for i, user in enumerate(top_users[:5]):
            row = ctk.CTkFrame(
                self.top_users_container,
                fg_color=COLORS['bg_secondary'] if i % 2 == 0 else "transparent",
                corner_radius=5
            )
            row.pack(fill="x", pady=2)
            
            # Rank
            ctk.CTkLabel(
                row,
                text=medals[i] if i < len(medals) else str(i + 1),
                font=ctk.CTkFont(size=14),
                width=50
            ).pack(side="left", padx=5, pady=8)
            
            # User
            ctk.CTkLabel(
                row,
                text=user.get('user_id', 'Unknown'),
                font=ctk.CTkFont(size=13),
                text_color=COLORS['text_primary'],
                width=200,
                anchor="w"
            ).pack(side="left", padx=5)
            
            # Count
            ctk.CTkLabel(
                row,
                text=f"{user.get('count', 0):,}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS['success'],
                width=100
            ).pack(side="left", padx=5)
