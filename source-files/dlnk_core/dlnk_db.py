import sqlite3
import os
import uuid
import datetime
import socket
import json

DB_NAME = "dlnk_customers.db"

def get_hwid():
    """Generates a unique hardware ID based on MAC address."""
    return str(uuid.getnode())

def get_ip_address():
    """Gets the local IP address (simulated for now to avoid external requests)."""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "127.0.0.1"

def init_db():
    """Initializes the database schema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Targets/Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hwid TEXT UNIQUE NOT NULL,
            license_key TEXT,
            ip_address TEXT,
            hostname TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            launch_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Create Activity Log Table (For future auditing)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hwid TEXT,
            action TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def register_checkin(license_key, hostname="Unknown"):
    """Registers a device check-in or updates existing record."""
    hwid = get_hwid()
    ip = get_ip_address()
    now = datetime.datetime.now()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT * FROM targets WHERE hwid=?", (hwid,))
    data = cursor.fetchone()
    
    if data:
        # Update existing
        cursor.execute('''
            UPDATE targets 
            SET last_seen=?, launch_count=launch_count+1, ip_address=?, license_key=?
            WHERE hwid=?
        ''', (now, ip, license_key, hwid))
        print(f"[DB] Updated target: {hwid}")
    else:
        # Insert new
        cursor.execute('''
            INSERT INTO targets (hwid, license_key, ip_address, hostname, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (hwid, license_key, ip, hostname, now, now))
        print(f"[DB] New target registered: {hwid}")
        
    # Log detailed activity
    cursor.execute("INSERT INTO activity_log (hwid, action, details) VALUES (?, ?, ?)", 
                   (hwid, "LOGIN", f"IP:{ip} | Key:{license_key}"))
    
    conn.commit()
    conn.close()
    return hwid

# Auto-init on import
if not os.path.exists(DB_NAME):
    init_db()
