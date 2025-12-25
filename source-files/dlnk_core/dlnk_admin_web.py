#!/usr/bin/env python3
"""
dLNk Admin Console - Web Interface Only
ระบบจัดการ Admin สำหรับ dLNk IDE (Web Version)
"""

import os
import sys
import json
from pathlib import Path

# Web imports
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
from flask_cors import CORS

# Import license system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dlnk_license_system import DLNKLicenseSystem, LicenseType, LicenseStatus

# Configuration
CONFIG_DIR = Path.home() / ".dlnk-ide"
LICENSE_DB = CONFIG_DIR / "licenses.db"

# Flask app
app = Flask(__name__)
app.secret_key = "dlnk-admin-secret-key-2025"
CORS(app)

license_system = None

# HTML Template
WEB_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>dLNk Admin Console</title>
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
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            background: #1a1a1a; 
            padding: 20px; 
            margin-bottom: 20px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { color: #00ff88; }
        .card { 
            background: #242424; 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 20px;
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 15px; 
        }
        .stat-card { 
            background: #1a1a1a; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
        }
        .stat-value { font-size: 2em; color: #00ff88; font-weight: bold; }
        .stat-label { color: #888; font-size: 0.9em; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { color: #888; font-weight: normal; }
        .btn { 
            background: #00ff88; 
            color: #000; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 5px; 
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover { background: #00cc6a; }
        .btn-danger { background: #ff4444; color: #fff; }
        .btn-danger:hover { background: #cc3333; }
        .status-active { color: #00ff88; }
        .status-expired { color: #ffcc00; }
        .status-revoked { color: #ff4444; }
        input, select { 
            background: #1a1a1a; 
            border: 1px solid #333; 
            color: #fff; 
            padding: 10px; 
            border-radius: 5px;
            width: 100%;
            margin-bottom: 10px;
        }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #888; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; }
        .nav a { 
            color: #888; 
            text-decoration: none; 
            padding: 10px 20px;
            border-radius: 5px;
        }
        .nav a:hover, .nav a.active { background: #242424; color: #00ff88; }
        textarea { 
            background: #0d0d0d; 
            border: 1px solid #333; 
            color: #fff; 
            padding: 10px;
            border-radius: 5px;
            width: 100%;
            font-family: monospace;
        }
        .success-box {
            background: #1a3d1a;
            border: 1px solid #00ff88;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 dLNk Admin Console</h1>
            <span>Admin</span>
        </div>
        
        <div class="nav">
            <a href="/" class="{{ 'active' if page == 'dashboard' else '' }}">📊 Dashboard</a>
            <a href="/licenses" class="{{ 'active' if page == 'licenses' else '' }}">🔑 Licenses</a>
            <a href="/users" class="{{ 'active' if page == 'users' else '' }}">👥 Users</a>
            <a href="/create" class="{{ 'active' if page == 'create' else '' }}">➕ Create</a>
        </div>
        
        {{ content | safe }}
    </div>
</body>
</html>
"""


def get_license_system():
    global license_system
    if license_system is None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        license_system = DLNKLicenseSystem(str(LICENSE_DB))
    return license_system


@app.route('/')
def dashboard():
    ls = get_license_system()
    stats = ls.get_license_stats()
    
    content = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{stats['total_licenses']}</div>
            <div class="stat-label">Total Licenses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['active_licenses']}</div>
            <div class="stat-label">Active</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['expired_licenses']}</div>
            <div class="stat-label">Expired</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['revoked_licenses']}</div>
            <div class="stat-label">Revoked</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['total_users']}</div>
            <div class="stat-label">Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['total_activations']}</div>
            <div class="stat-label">Activations</div>
        </div>
    </div>
    
    <div class="card">
        <h3>📝 Recent Activity</h3>
        <table>
            <tr><th>Time</th><th>Action</th><th>Details</th></tr>
    """
    
    for activity in stats.get('recent_activity', []):
        content += f"""
            <tr>
                <td>{activity['timestamp'][:19]}</td>
                <td>{activity['action']}</td>
                <td>{activity['details']}</td>
            </tr>
        """
    
    content += "</table></div>"
    
    return render_template_string(WEB_TEMPLATE, content=content, page="dashboard")


@app.route('/licenses')
def licenses():
    ls = get_license_system()
    all_licenses = ls.get_all_licenses()
    
    content = """
    <div class="card">
        <h3>🔑 All Licenses</h3>
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
                    <a href="/extend/{lic.key}" class="btn">+30d</a>
                    {'<a href="/revoke/' + lic.key + '" class="btn btn-danger">Revoke</a>' if lic.status == LicenseStatus.ACTIVE else ''}
                </td>
            </tr>
        """
    
    content += "</table></div>"
    
    return render_template_string(WEB_TEMPLATE, content=content, page="licenses")


@app.route('/users')
def users():
    ls = get_license_system()
    all_users = ls.get_all_users()
    
    content = """
    <div class="card">
        <h3>👥 All Users</h3>
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
    
    return render_template_string(WEB_TEMPLATE, content=content, page="users")


@app.route('/create', methods=['GET', 'POST'])
def create():
    ls = get_license_system()
    result = None
    
    if request.method == 'POST':
        owner = request.form.get('owner', 'User')
        license_type = LicenseType(request.form.get('type', 'basic'))
        duration = int(request.form.get('duration', 30))
        
        license_obj = ls.create_license(
            user_id="admin",
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
    <div class="card">
        <h3>➕ Create New License</h3>
        <form method="POST">
            <div class="form-group">
                <label>Owner Name</label>
                <input type="text" name="owner" placeholder="Enter owner name">
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
                <input type="number" name="duration" value="30">
            </div>
            <button type="submit" class="btn">Create License</button>
        </form>
    """
    
    if result:
        content += f"""
        <div class="success-box">
            <h4 style="color: #00ff88;">✅ License Created Successfully!</h4>
            <p><strong>Key:</strong> <code>{result['key']}</code></p>
            <p><strong>Type:</strong> {result['type']}</p>
            <p><strong>Expires:</strong> {result['expires']}</p>
            <p><strong>Encrypted Key (for distribution):</strong></p>
            <textarea rows="4" readonly>{result['encrypted']}</textarea>
        </div>
        """
    
    content += "</div>"
    
    return render_template_string(WEB_TEMPLATE, content=content, page="create")


@app.route('/extend/<key>')
def extend(key):
    ls = get_license_system()
    ls.extend_license(key, 30)
    return redirect('/licenses')


@app.route('/revoke/<key>')
def revoke(key):
    ls = get_license_system()
    ls.revoke_license(key)
    return redirect('/licenses')


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
def api_stats():
    ls = get_license_system()
    return jsonify(ls.get_license_stats())


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk Admin Console - Web Interface')
    parser.add_argument('--port', type=int, default=5001, help='Web server port')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    
    args = parser.parse_args()
    
    print(f"""
============================================================
dLNk Admin Console - Web Interface
============================================================
Starting server on http://{args.host}:{args.port}

Default admin credentials:
  Username: admin
  Password: admin123
============================================================
    """)
    
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
