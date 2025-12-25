#!/usr/bin/env python3
"""
dLNk Admin Console - Log Viewer
"""

import customtkinter as ctk
from utils.theme import COLORS, STATUS_COLORS, SEVERITY_COLORS
from components.header import Header
from components.dialog import MessageDialog


class LogsView(ctk.CTkFrame):
    """Log Viewer with C2 Logs and Alerts"""
    
    def __init__(self, parent, api_client=None):
        super().__init__(parent, fg_color="transparent")
        
        self.api_client = api_client
        self.logs = []
        self.alerts = []
        self.current_tab = "logs"
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create log viewer widgets"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        self.header = Header(header_frame, "Logs & Alerts", on_refresh=self.load_data)
        self.header.pack(side="left", fill="x", expand=True)
        
        # Export Button
        export_btn = ctk.CTkButton(
            header_frame,
            text="📥 Export",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['accent'],
            width=100,
            height=38,
            command=self.export_logs
        )
        export_btn.pack(side="right")
        
        # Tab Buttons
        tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, 15))
        
        self.logs_tab_btn = ctk.CTkButton(
            tab_frame,
            text="📋 C2 Logs",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['accent'],
            hover_color=COLORS['hover'],
            width=120,
            height=38,
            command=lambda: self.switch_tab("logs")
        )
        self.logs_tab_btn.pack(side="left", padx=(0, 5))
        
        self.alerts_tab_btn = ctk.CTkButton(
            tab_frame,
            text="🚨 Alerts",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['hover'],
            width=120,
            height=38,
            command=lambda: self.switch_tab("alerts")
        )
        self.alerts_tab_btn.pack(side="left", padx=5)
        
        # Alert count badge
        self.alert_badge = ctk.CTkLabel(
            tab_frame,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_primary'],
            fg_color=COLORS['error'],
            corner_radius=10,
            width=25,
            height=20
        )
        
        # Filter Bar
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 15))
        
        # Status Filter
        self.status_var = ctk.StringVar(value="All")
        self.status_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Success", "Blocked", "Suspicious"],
            variable=self.status_var,
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['bg_secondary'],
            dropdown_hover_color=COLORS['accent'],
            width=130,
            height=40,
            command=lambda x: self.filter_data()
        )
        self.status_filter.pack(side="left")
        
        # Severity Filter (for alerts)
        self.severity_var = ctk.StringVar(value="All Severity")
        self.severity_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Severity", "Critical", "Warning", "Info"],
            variable=self.severity_var,
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['bg_secondary'],
            dropdown_hover_color=COLORS['accent'],
            width=140,
            height=40,
            command=lambda x: self.filter_data()
        )
        
        # Count label
        self.count_label = ctk.CTkLabel(
            filter_frame,
            text="0 entries",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.count_label.pack(side="right")
        
        # Content Frame
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=10,
            scrollbar_button_color=COLORS['border'],
            scrollbar_button_hover_color=COLORS['accent']
        )
        self.content_frame.pack(fill="both", expand=True)
    
    def switch_tab(self, tab: str):
        """Switch between logs and alerts tabs"""
        self.current_tab = tab
        
        if tab == "logs":
            self.logs_tab_btn.configure(fg_color=COLORS['accent'])
            self.alerts_tab_btn.configure(fg_color=COLORS['bg_tertiary'])
            self.status_filter.pack(side="left")
            self.severity_filter.pack_forget()
            self.status_filter.configure(values=["All", "Success", "Blocked", "Suspicious"])
        else:
            self.logs_tab_btn.configure(fg_color=COLORS['bg_tertiary'])
            self.alerts_tab_btn.configure(fg_color=COLORS['accent'])
            self.status_filter.pack_forget()
            self.severity_filter.pack(side="left", padx=(0, 10))
        
        self.filter_data()
    
    def load_data(self):
        """Load logs and alerts from API"""
        if self.api_client:
            self.logs = self.api_client.get_logs(limit=100)
            self.alerts = self.api_client.get_alerts()
        else:
            self.logs = self._get_mock_logs()
            self.alerts = self._get_mock_alerts()
        
        # Update alert badge
        pending_alerts = sum(1 for a in self.alerts if not a.get('acknowledged', True))
        if pending_alerts > 0:
            self.alert_badge.configure(text=str(pending_alerts))
            self.alert_badge.place(in_=self.alerts_tab_btn, relx=1, rely=0, x=-5, y=-5)
        else:
            self.alert_badge.place_forget()
        
        self.filter_data()
    
    def _get_mock_logs(self):
        """Get mock log data"""
        return [
            {'timestamp': '2025-01-10 14:30:25', 'user': 'john_doe', 'status': 'success', 'prompt': 'Generate Python code for web scraping with BeautifulSoup...', 'time_ms': 245},
            {'timestamp': '2025-01-10 14:28:12', 'user': 'jane_smith', 'status': 'success', 'prompt': 'Explain this JavaScript async/await pattern...', 'time_ms': 189},
            {'timestamp': '2025-01-10 14:25:45', 'user': 'bob_wilson', 'status': 'blocked', 'prompt': 'How to bypass security authentication...', 'time_ms': 12},
            {'timestamp': '2025-01-10 14:22:33', 'user': 'alice_jones', 'status': 'success', 'prompt': 'Debug this React component with useState hook...', 'time_ms': 312},
            {'timestamp': '2025-01-10 14:20:15', 'user': 'charlie_brown', 'status': 'suspicious', 'prompt': 'Generate code to access admin panel...', 'time_ms': 45},
            {'timestamp': '2025-01-10 14:18:00', 'user': 'john_doe', 'status': 'success', 'prompt': 'Create a REST API endpoint in Flask...', 'time_ms': 278},
            {'timestamp': '2025-01-10 14:15:30', 'user': 'jane_smith', 'status': 'success', 'prompt': 'Optimize this SQL query for better performance...', 'time_ms': 156},
            {'timestamp': '2025-01-10 14:12:45', 'user': 'alice_jones', 'status': 'success', 'prompt': 'Write unit tests for this Python function...', 'time_ms': 234},
        ]
    
    def _get_mock_alerts(self):
        """Get mock alert data"""
        return [
            {'id': 1, 'timestamp': '2025-01-10 14:25:45', 'severity': 'critical', 'type': 'blocked_prompt', 'message': 'Suspicious prompt detected from user bob_wilson', 'acknowledged': False},
            {'id': 2, 'timestamp': '2025-01-10 14:20:15', 'severity': 'warning', 'type': 'suspicious_activity', 'message': 'User charlie_brown flagged for suspicious prompts', 'acknowledged': False},
            {'id': 3, 'timestamp': '2025-01-10 13:15:22', 'severity': 'warning', 'type': 'rate_limit', 'message': 'User john_doe exceeded rate limit (35 req/min)', 'acknowledged': True},
            {'id': 4, 'timestamp': '2025-01-10 10:45:00', 'severity': 'info', 'type': 'new_user', 'message': 'New user registered: david_lee', 'acknowledged': True},
            {'id': 5, 'timestamp': '2025-01-09 22:30:00', 'severity': 'info', 'type': 'license_created', 'message': 'New Pro license created for enterprise_corp', 'acknowledged': True},
        ]
    
    def filter_data(self):
        """Filter and render current tab data"""
        if self.current_tab == "logs":
            self._render_logs()
        else:
            self._render_alerts()
    
    def _render_logs(self):
        """Render C2 logs"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create header
        self._create_logs_header()
        
        # Filter logs
        status_filter = self.status_var.get().lower()
        filtered_logs = []
        
        for log in self.logs:
            if status_filter != "all":
                if log.get('status', '').lower() != status_filter:
                    continue
            filtered_logs.append(log)
        
        self.count_label.configure(text=f"{len(filtered_logs)} entries")
        
        if not filtered_logs:
            ctk.CTkLabel(
                self.content_frame,
                text="No logs found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS['text_secondary']
            ).pack(pady=50)
            return
        
        for i, log in enumerate(filtered_logs):
            self._create_log_row(log, i)
    
    def _create_logs_header(self):
        """Create logs table header"""
        header = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_secondary'], height=45)
        header.pack(fill="x", padx=5, pady=5)
        header.pack_propagate(False)
        
        headers = [("Time", 150), ("User", 120), ("Status", 100), ("Prompt Preview", 350), ("Time (ms)", 80)]
        
        for title, width in headers:
            ctk.CTkLabel(
                header,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_secondary'],
                width=width,
                anchor="w"
            ).pack(side="left", padx=10)
    
    def _create_log_row(self, log: dict, index: int):
        """Create a log row"""
        bg_color = COLORS['bg_tertiary'] if index % 2 == 0 else COLORS['bg_secondary']
        
        row = ctk.CTkFrame(self.content_frame, fg_color=bg_color, height=45)
        row.pack(fill="x", padx=5, pady=1)
        row.pack_propagate(False)
        
        # Time
        ctk.CTkLabel(
            row,
            text=log.get('timestamp', 'N/A'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # User
        ctk.CTkLabel(
            row,
            text=log.get('user', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
            width=120,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Status
        status = log.get('status', 'unknown').lower()
        status_color = STATUS_COLORS.get(status, COLORS['text_secondary'])
        
        ctk.CTkLabel(
            row,
            text=f"● {status.title()}",
            font=ctk.CTkFont(size=12),
            text_color=status_color,
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Prompt Preview
        prompt = log.get('prompt', '')
        preview = (prompt[:50] + '...') if len(prompt) > 50 else prompt
        
        prompt_label = ctk.CTkLabel(
            row,
            text=preview,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            width=350,
            anchor="w"
        )
        prompt_label.pack(side="left", padx=10)
        prompt_label.bind("<Button-1>", lambda e, p=prompt: self._show_full_prompt(p))
        prompt_label.configure(cursor="hand2")
        
        # Processing Time
        ctk.CTkLabel(
            row,
            text=f"{log.get('time_ms', 0)}ms",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['success'],
            width=80,
            anchor="w"
        ).pack(side="left", padx=10)
    
    def _render_alerts(self):
        """Render alerts"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create header
        self._create_alerts_header()
        
        # Filter alerts
        severity_filter = self.severity_var.get().lower()
        filtered_alerts = []
        
        for alert in self.alerts:
            if severity_filter != "all severity":
                if alert.get('severity', '').lower() != severity_filter:
                    continue
            filtered_alerts.append(alert)
        
        self.count_label.configure(text=f"{len(filtered_alerts)} alerts")
        
        if not filtered_alerts:
            ctk.CTkLabel(
                self.content_frame,
                text="No alerts found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS['text_secondary']
            ).pack(pady=50)
            return
        
        for i, alert in enumerate(filtered_alerts):
            self._create_alert_row(alert, i)
    
    def _create_alerts_header(self):
        """Create alerts table header"""
        header = ctk.CTkFrame(self.content_frame, fg_color=COLORS['bg_secondary'], height=45)
        header.pack(fill="x", padx=5, pady=5)
        header.pack_propagate(False)
        
        headers = [("Time", 150), ("Severity", 100), ("Type", 150), ("Message", 350), ("Status", 100)]
        
        for title, width in headers:
            ctk.CTkLabel(
                header,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_secondary'],
                width=width,
                anchor="w"
            ).pack(side="left", padx=10)
    
    def _create_alert_row(self, alert: dict, index: int):
        """Create an alert row"""
        acknowledged = alert.get('acknowledged', False)
        bg_color = COLORS['bg_tertiary'] if index % 2 == 0 else COLORS['bg_secondary']
        
        # Highlight unacknowledged alerts
        if not acknowledged:
            bg_color = "#2a1a1a"
        
        row = ctk.CTkFrame(self.content_frame, fg_color=bg_color, height=50)
        row.pack(fill="x", padx=5, pady=1)
        row.pack_propagate(False)
        
        # Time
        ctk.CTkLabel(
            row,
            text=alert.get('timestamp', 'N/A'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Severity
        severity = alert.get('severity', 'info').lower()
        severity_color = SEVERITY_COLORS.get(severity, COLORS['text_secondary'])
        
        ctk.CTkLabel(
            row,
            text=f"● {severity.upper()}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=severity_color,
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Type
        ctk.CTkLabel(
            row,
            text=alert.get('type', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['accent'],
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Message
        ctk.CTkLabel(
            row,
            text=alert.get('message', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
            width=350,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Status / Acknowledge button
        if acknowledged:
            ctk.CTkLabel(
                row,
                text="✓ Acknowledged",
                font=ctk.CTkFont(size=11),
                text_color=COLORS['success'],
                width=100
            ).pack(side="left", padx=10)
        else:
            ctk.CTkButton(
                row,
                text="Acknowledge",
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['warning'],
                hover_color="#cc9900",
                text_color="#000",
                width=90,
                height=28,
                command=lambda a=alert: self._acknowledge_alert(a)
            ).pack(side="left", padx=10)
    
    def _show_full_prompt(self, prompt: str):
        """Show full prompt in dialog"""
        MessageDialog(
            self.winfo_toplevel(),
            "Full Prompt",
            prompt,
            message_type="info"
        )
    
    def _acknowledge_alert(self, alert: dict):
        """Acknowledge an alert"""
        if self.api_client:
            self.api_client.acknowledge_alert(alert.get('id'))
        
        # Update local data
        for a in self.alerts:
            if a.get('id') == alert.get('id'):
                a['acknowledged'] = True
                break
        
        self.load_data()
    
    def export_logs(self):
        """Export logs to file"""
        MessageDialog(
            self.winfo_toplevel(),
            "Export Logs",
            "Logs exported to:\n~/.dlnk-ide/logs_export.json",
            message_type="success"
        )
