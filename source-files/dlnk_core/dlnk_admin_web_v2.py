#!/usr/bin/env python3
"""
dLNk Admin Console v2.0 - Web Interface with Authentication
ระบบจัดการ Admin สำหรับ dLNk IDE (Web Version)
- เพิ่มระบบ Login/Logout
- เพิ่ม C2 Logging Dashboard
- เพิ่ม Alert Management
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Web imports
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session

# Import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dlnk_license_system import DLNKLicenseSystem, LicenseType, LicenseStatus
from dlnk_admin_auth import AdminAuthDB, create_admin_auth_blueprint, login_required, superadmin_required
from dlnk_c2_logging import C2LogDatabase

# Configuration
CONFIG_DIR = Path.home() / ".dlnk-ide"
LICENSE_DB = CONFIG_DIR / "licenses.db"

# Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('DLNK_SECRET_KEY', 'dlnk-admin-secret-key-2025-secure')

# Register auth blueprint
auth_db = AdminAuthDB()
auth_bp = create_admin_auth_blueprint(auth_db)
app.register_blueprint(auth_bp, url_prefix='/auth')

# Initialize systems
license_system = None
c2_db = None

def get_license_system():
    global license_system
    if license_system is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        license_system = DLNKLicenseSystem(str(LICENSE_DB))
    return license_system

def get_c2_db():
    global c2_db
    if c2_db is None:
        c2_db = C2LogDatabase()
    return c2_db


# ===== TEMPLATES =====

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - dLNk Admin</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #0d0d0d; 
            color: #fff; 
            min-height: 100vh;
        }
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 250px;
            height: 100vh;
            background: #1a1a1a;
            padding: 20px;
            border-right: 1px solid #333;
        }
        .sidebar-logo {
            color: #00ff88;
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #333;
        }
        .sidebar-nav a {
            display: block;
            color: #888;
            text-decoration: none;
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 5px;
            transition: all 0.2s;
        }
        .sidebar-nav a:hover, .sidebar-nav a.active {
            background: #242424;
            color: #00ff88;
        }
        .sidebar-user {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            padding: 15px;
            background: #242424;
            border-radius: 8px;
        }
        .sidebar-user .username {
            color: #00ff88;
            font-weight: bold;
        }
        .sidebar-user .role {
            color: #666;
            font-size: 0.8em;
        }
        .sidebar-user .logout {
            display: block;
            color: #ff4444;
            text-decoration: none;
            margin-top: 10px;
            font-size: 0.9em;
        }
        .main-content {
            margin-left: 250px;
            padding: 30px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #fff;
            font-size: 1.8em;
        }
        .card {
            background: #242424;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .card h3 {
            color: #00ff88;
            margin-bottom: 20px;
            font-size: 1.1em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #1a1a2e 0%, #242424 100%);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #333;
        }
        .stat-value {
            font-size: 2.5em;
            color: #00ff88;
            font-weight: bold;
        }
        .stat-label {
            color: #888;
            font-size: 0.9em;
            margin-top: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        th {
            color: #888;
            font-weight: normal;
            font-size: 0.9em;
        }
        .btn {
            background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff4444 0%, #cc3333 100%);
            color: #fff;
        }
        .btn-warning {
            background: linear-gradient(135deg, #ffcc00 0%, #ff9900 100%);
            color: #000;
        }
        .status-active { color: #00ff88; }
        .status-expired { color: #ffcc00; }
        .status-revoked { color: #ff4444; }
        .status-blocked { color: #ff4444; }
        .status-success { color: #00ff88; }
        input, select, textarea {
            background: #1a1a1a;
            border: 1px solid #333;
            color: #fff;
            padding: 12px;
            border-radius: 8px;
            width: 100%;
            margin-bottom: 15px;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #00ff88;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #888;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .alert-badge {
            background: #ff4444;
            color: #fff;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .severity-critical { color: #ff4444; }
        .severity-warning { color: #ffcc00; }
        .severity-info { color: #00ff88; }
        code {
            background: #1a1a1a;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
        }
        .success-box {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-logo">🔐 dLNk Admin</div>
        <nav class="sidebar-nav">
            <a href="{{ url_for('dashboard') }}" class="{{ 'active' if page == 'dashboard' else '' }}">📊 Dashboard</a>
            <a href="{{ url_for('licenses') }}" class="{{ 'active' if page == 'licenses' else '' }}">🔑 Licenses</a>
            <a href="{{ url_for('users') }}" class="{{ 'active' if page == 'users' else '' }}">👥 Users</a>
            <a href="{{ url_for('create_license') }}" class="{{ 'active' if page == 'create' else '' }}">➕ Create License</a>
            <a href="{{ url_for('c2_logs') }}" class="{{ 'active' if page == 'logs' else '' }}">📝 C2 Logs</a>
            <a href="{{ url_for('alerts') }}" class="{{ 'active' if page == 'alerts' else '' }}">
                🚨 Alerts
                {% if pending_alerts > 0 %}<span class="alert-badge">{{ pending_alerts }}</span>{% endif %}
            </a>
        </nav>
        <div class="sidebar-user">
            <div class="username">{{ session.admin_user.username }}</div>
            <div class="role">{{ session.admin_user.role }}</div>
            <a href="{{ url_for('admin_auth.logout') }}" class="logout">🚪 Logout</a>
        </div>
    </div>
    
    <div class="main-content">
        {{ content | safe }}
    </div>
</body>
</html>
"""


# ===== ROUTES =====

@app.route('/')
@login_required
def dashboard():
    ls = get_license_system()
    c2 = get_c2_db()
    
    license_stats = ls.get_license_stats()
    c2_stats = c2.get_dashboard_stats()
    pending_alerts = c2.get_alerts(unacknowledged_only=True, limit=1)
    
    content = f"""
    <div class="header">
        <h1>Dashboard</h1>
        <span style="color: #666;">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{license_stats['total_licenses']}</div>
            <div class="stat-label">Total Licenses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{license_stats['active_licenses']}</div>
            <div class="stat-label">Active Licenses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{c2_stats['requests_today']}</div>
            <div class="stat-label">Requests Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{c2_stats['active_users_today']}</div>
            <div class="stat-label">Active Users Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{c2_stats['blocked_today']}</div>
            <div class="stat-label">Blocked Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{c2_stats['pending_alerts']}</div>
            <div class="stat-label">Pending Alerts</div>
        </div>
    </div>
    
    <div class="card">
        <h3>📈 Top Users Today</h3>
        <table>
            <tr><th>User ID</th><th>Requests</th></tr>
    """
    
    for user in c2_stats.get('top_users', []):
        content += f"<tr><td>{user['user_id']}</td><td>{user['count']}</td></tr>"
    
    if not c2_stats.get('top_users'):
        content += "<tr><td colspan='2' style='color: #666;'>No activity today</td></tr>"
    
    content += """
        </table>
    </div>
    
    <div class="card">
        <h3>📝 Recent Activity</h3>
        <table>
            <tr><th>Time</th><th>Action</th><th>Details</th></tr>
    """
    
    for activity in license_stats.get('recent_activity', [])[:5]:
        content += f"""
            <tr>
                <td>{activity['timestamp'][:19]}</td>
                <td>{activity['action']}</td>
                <td>{activity['details']}</td>
            </tr>
        """
    
    content += "</table></div>"
    
    return render_template_string(BASE_TEMPLATE, 
                                  content=content, 
                                  page="dashboard", 
                                  title="Dashboard",
                                  pending_alerts=len(pending_alerts))


@app.route('/licenses')
@login_required
def licenses():
    ls = get_license_system()
    c2 = get_c2_db()
    all_licenses = ls.get_all_licenses()
    pending_alerts = c2.get_alerts(unacknowledged_only=True, limit=1)
    
    content = """
    <div class="header">
        <h1>License Management</h1>
        <a href="/create" class="btn">➕ Create New</a>
    </div>
    
    <div class="card">
        <table>
            <tr><th>Key</th><th>Type</th><th>Status</th><th>Expires</th><th>Actions</th></tr>
    """
    
    for lic in all_licenses:
        status_class = f"status-{lic.status.value}"
        content += f"""
            <tr>
                <td><code>{lic.key}</code></td>
                <td>{lic.license_type.value}</td>
                <td class="{status_class}">{lic.status.value}</td>
                <td>{lic.expires_at[:10]}</td>
                <td>
                    <a href="/extend/{lic.key}" class="btn" style="padding: 5px 10px; font-size: 0.9em;">+30d</a>
                    {'<a href="/revoke/' + lic.key + '" class="btn btn-danger" style="padding: 5px 10px; font-size: 0.9em;">Revoke</a>' if lic.status == LicenseStatus.ACTIVE else ''}
                </td>
            </tr>
        """
    
    content += "</table></div>"
    
    return render_template_string(BASE_TEMPLATE, 
                                  content=content, 
                                  page="licenses", 
                                  title="Licenses",
                                  pending_alerts=len(pending_alerts))


@app.route('/users')
@login_required
def users():
    ls = get_license_system()
    c2 = get_c2_db()
    all_users = ls.get_all_users()
    pending_alerts = c2.get_alerts(unacknowledged_only=True, limit=1)
    
    content = """
    <div class="header">
        <h1>User Management</h1>
    </div>
    
    <div class="card">
        <table>
            <tr><th>Username</th><th>Email</th><th>Role</th><th>Created</th></tr>
    """
    
    for user in all_users:
        content += f"""
            <tr>
                <td><strong>{user.username}</strong></td>
                <td>{user.email or 'N/A'}</td>
                <td>{user.role}</td>
                <td>{user.created_at[:10]}</td>
            </tr>
        """
    
    content += "</table></div>"
    
    return render_template_string(BASE_TEMPLATE, 
                                  content=content, 
                                  page="users", 
                                  title="Users",
                                  pending_alerts=len(pending_alerts))


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_license():
    ls = get_license_system()
    c2 = get_c2_db()
    pending_alerts = c2.get_alerts(unacknowledged_only=True, limit=1)
    result = None
    
    if request.method == 'POST':
        owner = request.form.get('owner', 'User')
        license_type = LicenseType(request.form.get('type', 'basic'))
        duration = int(request.form.get('duration', 30))
        
        license_obj = ls.create_license(
            user_id=session['admin_user']['username'],
            license_type=license_type,
            duration_days=duration,
            owner_name=owner
        )
        
        result = {
            "key": license_obj.key,
            "type": license_obj.license_type.value,
            "expires": license_obj.expires_at[:10],
            "encrypted": license_obj.encrypted_key
        }
    
    content = """
    <div class="header">
        <h1>Create New License</h1>
    </div>
    
    <div class="card">
        <form method="POST">
            <div class="form-group">
                <label>Owner Name</label>
                <input type="text" name="owner" placeholder="Enter owner name" required>
            </div>
            <div class="form-group">
                <label>License Type</label>
                <select name="type">
                    <option value="trial">Trial (7 days features)</option>
                    <option value="basic" selected>Basic</option>
                    <option value="pro">Pro</option>
                    <option value="enterprise">Enterprise</option>
                    <option value="admin">Admin</option>
                </select>
            </div>
            <div class="form-group">
                <label>Duration (days)</label>
                <input type="number" name="duration" value="30" min="1" max="365">
            </div>
            <button type="submit" class="btn">Create License</button>
        </form>
    """
    
    if result:
        content += f"""
        <div class="success-box">
            <h4 style="color: #00ff88; margin-bottom: 15px;">✅ License Created Successfully!</h4>
            <p><strong>Key:</strong> <code>{result['key']}</code></p>
            <p><strong>Type:</strong> {result['type']}</p>
            <p><strong>Expires:</strong> {result['expires']}</p>
            <p style="margin-top: 15px;"><strong>Encrypted Key (for distribution):</strong></p>
            <textarea rows="4" readonly style="margin-top: 10px;">{result['encrypted']}</textarea>
        </div>
        """
    
    content += "</div>"
    
    return render_template_string(BASE_TEMPLATE, 
                                  content=content, 
                                  page="create", 
                                  title="Create License",
                                  pending_alerts=len(pending_alerts))


@app.route('/c2-logs')
@login_required
def c2_logs():
    c2 = get_c2_db()
    logs = c2.get_recent_logs(limit=50)
    pending_alerts = c2.get_alerts(unacknowledged_only=True, limit=1)
    
    content = """
    <div class="header">
        <h1>C2 Logs</h1>
    </div>
    
    <div class="card">
        <table>
            <tr><th>Time</th><th>User</th><th>Status</th><th>Prompt Preview</th><th>Processing</th></tr>
    """
    
    for log in logs:
        status_class = f"status-{log['status']}"
        content += f"""
            <tr>
                <td>{log['timestamp'][:19]}</td>
                <td>{log['user_id']}</td>
                <td class="{status_class}">{log['status']}</td>
                <td>{(log['prompt_preview'] or '')[:50]}...</td>
                <td>{log['processing_time_ms']}ms</td>
            </tr>
        """
    
    content += "</table></div>"
    
    return render_template_string(BASE_TEMPLATE, 
                                  content=content, 
                                  page="logs", 
                                  title="C2 Logs",
                                  pending_alerts=len(pending_alerts))


@app.route('/alerts')
@login_required
def alerts():
    c2 = get_c2_db()
    all_alerts = c2.get_alerts(unacknowledged_only=False, limit=100)
    pending_alerts = [a for a in all_alerts if not a['acknowledged']]
    
    content = """
    <div class="header">
        <h1>Alerts</h1>
    </div>
    
    <div class="card">
        <table>
            <tr><th>Time</th><th>Severity</th><th>Type</th><th>Message</th><th>Status</th></tr>
    """
    
    for alert in all_alerts:
        severity_class = f"severity-{alert['severity']}"
        status = "✅ Acknowledged" if alert['acknowledged'] else "⚠️ Pending"
        content += f"""
            <tr>
                <td>{alert['timestamp'][:19]}</td>
                <td class="{severity_class}">{alert['severity'].upper()}</td>
                <td>{alert['alert_type']}</td>
                <td>{alert['message']}</td>
                <td>{status}</td>
            </tr>
        """
    
    if not all_alerts:
        content += "<tr><td colspan='5' style='color: #666; text-align: center;'>No alerts</td></tr>"
    
    content += "</table></div>"
    
    return render_template_string(BASE_TEMPLATE, 
                                  content=content, 
                                  page="alerts", 
                                  title="Alerts",
                                  pending_alerts=len(pending_alerts))


@app.route('/extend/<key>')
@login_required
def extend(key):
    ls = get_license_system()
    ls.extend_license(key, 30)
    return redirect('/licenses')


@app.route('/revoke/<key>')
@login_required
def revoke(key):
    ls = get_license_system()
    ls.revoke_license(key)
    return redirect('/licenses')


# ===== API ENDPOINTS =====

@app.route('/api/verify', methods=['POST'])
def api_verify():
    ls = get_license_system()
    
    data = request.json
    key = data.get('key', '')
    hwid = data.get('hwid', '')
    
    valid, message, license_obj = ls.verify_license(key, hwid)
    
    if valid:
        return jsonify({
            "valid": True,
            "message": message,
            "features": license_obj.features if license_obj else []
        })
    else:
        return jsonify({
            "valid": False,
            "message": message
        }), 401


@app.route('/api/stats')
@login_required
def api_stats():
    ls = get_license_system()
    c2 = get_c2_db()
    
    return jsonify({
        "license_stats": ls.get_license_stats(),
        "c2_stats": c2.get_dashboard_stats()
    })


# ===== MAIN =====

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk Admin Console v2.0')
    parser.add_argument('--port', type=int, default=5001, help='Web server port')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           dLNk Admin Console v2.0                        ║
║                                                          ║
║  🔐 Authentication: ENABLED                              ║
║  📝 C2 Logging: ENABLED                                  ║
║  🚨 Alerts: ENABLED                                      ║
║                                                          ║
║  Server: http://{args.host}:{args.port}                         ║
║                                                          ║
║  Default credentials:                                    ║
║    Username: admin                                       ║
║    Password: admin123 (CHANGE IMMEDIATELY!)              ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
