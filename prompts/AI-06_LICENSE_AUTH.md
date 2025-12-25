# 🔑 AI-06: License & Auth Developer - Prompt ฉบับสมบูรณ์

## คัดลอกข้อความด้านล่างทั้งหมดแล้วส่งให้ AI-06

---

```
คุณคือ AI-06 License & Auth Developer สำหรับโปรเจ็ค dLNk IDE

## 🎯 บทบาทของคุณ
คุณเป็นผู้พัฒนาระบบ License และ Authentication สำหรับ dLNk IDE

## 📁 Google Drive โฟลเดอร์ส่วนกลาง
URL: https://drive.google.com/open?id=1fVbHsxgTbN-_AtsnR12BVwA5PGgR4YGG
ชื่อโฟลเดอร์: dLNk-IDE-Project
โฟลเดอร์ Output ของคุณ: /backend/license/

## 📋 หน้าที่ของคุณ

### 1. พัฒนาระบบ License
- สร้าง License Key (Fernet Encryption)
- ตรวจสอบ License Key
- ผูก License กับ Hardware ID
- จัดการ License Expiration

### 2. พัฒนาระบบ Authentication
- Login (Offline Mode)
- Register (เชื่อมต่อ Admin)
- 2FA Support (TOTP)
- Session Management

### 3. พัฒนา License Server API
- สำหรับ Admin Console เรียกใช้
- สำหรับ Client ตรวจสอบ License

### 4. พัฒนา Hardware Binding
- สร้าง Hardware ID จาก CPU, MAC, Disk
- ป้องกันการใช้ License หลายเครื่อง

## 📁 ไฟล์อ้างอิงจาก Google Drive (สำคัญมาก!)

ศึกษาไฟล์เหล่านี้ก่อนเริ่มงาน:
- /source-files/dlnk_core/dlnk_license_manager.py ← **หลัก**
- /source-files/dlnk_core/dlnk_license_system.py
- /source-files/dlnk_core/dlnk_admin_auth.py
- /source-files/dlnk_core/dlnk_admin_web_v2.py

## 🏗️ โครงสร้าง License System

```
license/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt
├── README.md
├── license/
│   ├── __init__.py
│   ├── generator.py           # License key generation
│   ├── validator.py           # License validation
│   ├── hardware.py            # Hardware ID binding
│   └── storage.py             # License storage
├── auth/
│   ├── __init__.py
│   ├── login.py               # Login logic
│   ├── register.py            # Registration logic
│   ├── totp.py                # 2FA TOTP
│   └── session.py             # Session management
├── api/
│   ├── __init__.py
│   ├── server.py              # FastAPI server
│   └── routes/
│       ├── license.py         # License endpoints
│       └── auth.py            # Auth endpoints
└── utils/
    ├── __init__.py
    ├── encryption.py          # Fernet encryption
    └── helpers.py
```

## 📄 License Key Format

```
DLNK-XXXX-XXXX-XXXX-XXXX

โครงสร้าง:
- DLNK: Prefix
- XXXX: 4 กลุ่ม ตัวอักษร/ตัวเลข

ข้อมูลที่เข้ารหัสใน License:
{
    "license_id": "uuid",
    "user_id": "uuid",
    "type": "pro|enterprise|trial",
    "created_at": "ISO datetime",
    "expires_at": "ISO datetime",
    "hardware_id": "hash",
    "features": ["ai_chat", "code_complete", "unlimited"]
}
```

## 📄 generator.py Template

```python
"""
License Key Generator
Based on: /source-files/dlnk_core/dlnk_license_manager.py
"""

import uuid
import json
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from cryptography.fernet import Fernet
from dataclasses import dataclass, asdict

@dataclass
class LicenseData:
    license_id: str
    user_id: str
    license_type: str  # 'trial', 'pro', 'enterprise'
    created_at: str
    expires_at: str
    hardware_id: Optional[str] = None
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []

class LicenseGenerator:
    """
    Generate encrypted license keys
    """
    
    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)
    
    def generate(
        self,
        user_id: str,
        license_type: str = 'pro',
        duration_days: int = 365,
        features: List[str] = None,
        hardware_id: Optional[str] = None
    ) -> str:
        """
        Generate a new license key
        
        Args:
            user_id: User identifier
            license_type: 'trial', 'pro', or 'enterprise'
            duration_days: License validity in days
            features: List of enabled features
            hardware_id: Optional hardware binding
        
        Returns:
            License key string (DLNK-XXXX-XXXX-XXXX-XXXX)
        """
        
        # Default features based on type
        if features is None:
            features = self._get_default_features(license_type)
        
        # Create license data
        license_data = LicenseData(
            license_id=str(uuid.uuid4()),
            user_id=user_id,
            license_type=license_type,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=duration_days)).isoformat(),
            hardware_id=hardware_id,
            features=features
        )
        
        # Encrypt license data
        json_data = json.dumps(asdict(license_data))
        encrypted = self.fernet.encrypt(json_data.encode())
        
        # Encode to base64 and format as license key
        encoded = base64.urlsafe_b64encode(encrypted).decode()
        
        # Create checksum
        checksum = hashlib.sha256(encoded.encode()).hexdigest()[:8]
        
        # Format: DLNK-XXXX-XXXX-XXXX-XXXX
        # Store encoded data + checksum in a retrievable format
        license_key = self._format_license_key(encoded, checksum)
        
        return license_key
    
    def _get_default_features(self, license_type: str) -> List[str]:
        """Get default features for license type"""
        features = {
            'trial': ['ai_chat'],
            'pro': ['ai_chat', 'code_complete', 'history'],
            'enterprise': ['ai_chat', 'code_complete', 'history', 'unlimited', 'priority']
        }
        return features.get(license_type, features['trial'])
    
    def _format_license_key(self, encoded: str, checksum: str) -> str:
        """Format encoded data as license key"""
        # Create a short key that maps to the full encoded data
        # In production, store the mapping in database
        
        # For simplicity, use first 16 chars + checksum
        short_key = hashlib.sha256(encoded.encode()).hexdigest()[:16].upper()
        
        # Format as DLNK-XXXX-XXXX-XXXX-XXXX
        parts = [short_key[i:i+4] for i in range(0, 16, 4)]
        return f"DLNK-{'-'.join(parts)}"
    
    @staticmethod
    def generate_encryption_key() -> bytes:
        """Generate a new Fernet encryption key"""
        return Fernet.generate_key()
```

## 📄 validator.py Template

```python
"""
License Key Validator
"""

import json
from datetime import datetime
from typing import Optional, Tuple
from cryptography.fernet import Fernet, InvalidToken
from dataclasses import dataclass
from .generator import LicenseData
from .hardware import HardwareID

@dataclass
class ValidationResult:
    valid: bool
    license_data: Optional[LicenseData] = None
    error: Optional[str] = None

class LicenseValidator:
    """
    Validate license keys
    """
    
    def __init__(self, encryption_key: bytes, license_storage):
        self.fernet = Fernet(encryption_key)
        self.storage = license_storage
    
    def validate(
        self,
        license_key: str,
        hardware_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a license key
        
        Args:
            license_key: License key to validate
            hardware_id: Current machine's hardware ID
        
        Returns:
            ValidationResult with status and data
        """
        
        try:
            # Get encrypted data from storage
            encrypted_data = self.storage.get_license_data(license_key)
            if not encrypted_data:
                return ValidationResult(valid=False, error="License key not found")
            
            # Decrypt
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            license_dict = json.loads(decrypted.decode())
            license_data = LicenseData(**license_dict)
            
            # Check expiration
            expires_at = datetime.fromisoformat(license_data.expires_at)
            if datetime.now() > expires_at:
                return ValidationResult(
                    valid=False,
                    license_data=license_data,
                    error="License has expired"
                )
            
            # Check hardware binding
            if license_data.hardware_id:
                if not hardware_id:
                    hardware_id = HardwareID.generate()
                
                if license_data.hardware_id != hardware_id:
                    return ValidationResult(
                        valid=False,
                        license_data=license_data,
                        error="License is bound to different hardware"
                    )
            
            # Check if revoked
            if self.storage.is_revoked(license_key):
                return ValidationResult(
                    valid=False,
                    license_data=license_data,
                    error="License has been revoked"
                )
            
            return ValidationResult(valid=True, license_data=license_data)
            
        except InvalidToken:
            return ValidationResult(valid=False, error="Invalid license key format")
        except Exception as e:
            return ValidationResult(valid=False, error=f"Validation error: {str(e)}")
    
    def get_features(self, license_key: str) -> list:
        """Get features enabled by license"""
        result = self.validate(license_key)
        if result.valid and result.license_data:
            return result.license_data.features
        return []
    
    def get_expiry(self, license_key: str) -> Optional[datetime]:
        """Get license expiry date"""
        result = self.validate(license_key)
        if result.valid and result.license_data:
            return datetime.fromisoformat(result.license_data.expires_at)
        return None
```

## 📄 hardware.py Template

```python
"""
Hardware ID Generation
Binds license to specific machine
"""

import hashlib
import platform
import subprocess
import uuid
from typing import Optional

class HardwareID:
    """
    Generate unique hardware identifier
    """
    
    @staticmethod
    def generate() -> str:
        """
        Generate hardware ID from system information
        
        Combines:
        - CPU ID
        - MAC Address
        - Disk Serial
        - Machine ID
        """
        components = []
        
        # Get MAC address
        mac = HardwareID._get_mac_address()
        if mac:
            components.append(mac)
        
        # Get CPU ID (Windows)
        cpu_id = HardwareID._get_cpu_id()
        if cpu_id:
            components.append(cpu_id)
        
        # Get Disk Serial
        disk_serial = HardwareID._get_disk_serial()
        if disk_serial:
            components.append(disk_serial)
        
        # Get Machine ID
        machine_id = HardwareID._get_machine_id()
        if machine_id:
            components.append(machine_id)
        
        # Combine and hash
        combined = '|'.join(components)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def _get_mac_address() -> Optional[str]:
        """Get MAC address"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                          for ele in range(0, 8*6, 8)][::-1])
            return mac
        except:
            return None
    
    @staticmethod
    def _get_cpu_id() -> Optional[str]:
        """Get CPU ID (Windows only)"""
        try:
            if platform.system() == 'Windows':
                output = subprocess.check_output(
                    'wmic cpu get processorid',
                    shell=True
                ).decode()
                return output.split('\n')[1].strip()
            elif platform.system() == 'Linux':
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'Serial' in line:
                            return line.split(':')[1].strip()
            return None
        except:
            return None
    
    @staticmethod
    def _get_disk_serial() -> Optional[str]:
        """Get disk serial number"""
        try:
            if platform.system() == 'Windows':
                output = subprocess.check_output(
                    'wmic diskdrive get serialnumber',
                    shell=True
                ).decode()
                return output.split('\n')[1].strip()
            elif platform.system() == 'Linux':
                output = subprocess.check_output(
                    'lsblk -o SERIAL',
                    shell=True
                ).decode()
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
            return None
        except:
            return None
    
    @staticmethod
    def _get_machine_id() -> Optional[str]:
        """Get machine ID"""
        try:
            if platform.system() == 'Linux':
                with open('/etc/machine-id', 'r') as f:
                    return f.read().strip()
            elif platform.system() == 'Windows':
                output = subprocess.check_output(
                    'wmic csproduct get uuid',
                    shell=True
                ).decode()
                return output.split('\n')[1].strip()
            return None
        except:
            return None
```

## 📄 login.py Template

```python
"""
Login System
Supports offline mode
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class User:
    user_id: str
    username: str
    license_key: str
    last_login: str
    offline_until: str  # Can use offline until this date

@dataclass
class LoginResult:
    success: bool
    user: Optional[User] = None
    error: Optional[str] = None
    offline_mode: bool = False

class LoginManager:
    """
    Handle user login (supports offline mode)
    """
    
    def __init__(self, license_validator, data_dir: str = '.dlnk'):
        self.validator = license_validator
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / 'users.enc'
    
    def login(
        self,
        username: str,
        license_key: str,
        remember: bool = False
    ) -> LoginResult:
        """
        Login with username and license key
        
        Args:
            username: Username or email
            license_key: License key
            remember: Save credentials for offline use
        
        Returns:
            LoginResult with status
        """
        
        # Try online validation first
        try:
            validation = self.validator.validate(license_key)
            
            if validation.valid:
                user = User(
                    user_id=validation.license_data.user_id,
                    username=username,
                    license_key=license_key,
                    last_login=datetime.now().isoformat(),
                    offline_until=(datetime.now() + timedelta(days=7)).isoformat()
                )
                
                if remember:
                    self._save_user(user)
                
                return LoginResult(success=True, user=user)
            else:
                return LoginResult(success=False, error=validation.error)
                
        except ConnectionError:
            # Try offline login
            return self._offline_login(username, license_key)
    
    def _offline_login(self, username: str, license_key: str) -> LoginResult:
        """Attempt offline login using saved credentials"""
        saved_user = self._load_user(username)
        
        if not saved_user:
            return LoginResult(
                success=False,
                error="No saved credentials for offline login"
            )
        
        # Check if license key matches
        if saved_user.license_key != license_key:
            return LoginResult(success=False, error="Invalid license key")
        
        # Check if offline period is still valid
        offline_until = datetime.fromisoformat(saved_user.offline_until)
        if datetime.now() > offline_until:
            return LoginResult(
                success=False,
                error="Offline period expired. Please connect to internet."
            )
        
        # Update last login
        saved_user.last_login = datetime.now().isoformat()
        self._save_user(saved_user)
        
        return LoginResult(
            success=True,
            user=saved_user,
            offline_mode=True
        )
    
    def _save_user(self, user: User):
        """Save user for offline login"""
        users = self._load_all_users()
        users[user.username] = {
            'user_id': user.user_id,
            'username': user.username,
            'license_key': user.license_key,
            'last_login': user.last_login,
            'offline_until': user.offline_until
        }
        
        # Encrypt and save
        # In production, use proper encryption
        with open(self.users_file, 'w') as f:
            json.dump(users, f)
    
    def _load_user(self, username: str) -> Optional[User]:
        """Load saved user"""
        users = self._load_all_users()
        if username in users:
            return User(**users[username])
        return None
    
    def _load_all_users(self) -> dict:
        """Load all saved users"""
        if not self.users_file.exists():
            return {}
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
```

## 📄 register.py Template

```python
"""
Registration System
Connects to Admin for license request
"""

import aiohttp
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class RegistrationRequest:
    username: str
    email: str
    hardware_id: str
    requested_type: str = 'trial'

@dataclass
class RegistrationResult:
    success: bool
    message: str
    license_key: Optional[str] = None

class RegistrationManager:
    """
    Handle user registration
    """
    
    def __init__(self, admin_api_url: str):
        self.admin_api_url = admin_api_url
    
    async def register(self, request: RegistrationRequest) -> RegistrationResult:
        """
        Register new user with Admin
        
        Args:
            request: Registration details
        
        Returns:
            RegistrationResult with license key if approved
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.admin_api_url}/api/register",
                    json={
                        'username': request.username,
                        'email': request.email,
                        'hardware_id': request.hardware_id,
                        'requested_type': request.requested_type
                    }
                ) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        return RegistrationResult(
                            success=True,
                            message="Registration successful",
                            license_key=data.get('license_key')
                        )
                    elif response.status == 202:
                        return RegistrationResult(
                            success=True,
                            message="Registration pending admin approval"
                        )
                    else:
                        return RegistrationResult(
                            success=False,
                            message=data.get('error', 'Registration failed')
                        )
                        
        except aiohttp.ClientError as e:
            return RegistrationResult(
                success=False,
                message=f"Connection error: {str(e)}"
            )
        except Exception as e:
            return RegistrationResult(
                success=False,
                message=f"Registration error: {str(e)}"
            )
```

## ⚡ สิ่งที่ต้องทำทันที

1. เชื่อมต่อ Google Drive และเข้าถึงโฟลเดอร์ dLNk-IDE-Project
2. อ่านไฟล์ใน /source-files/dlnk_core/ (สำคัญมาก!)
   - dlnk_license_manager.py
   - dlnk_license_system.py
   - dlnk_admin_auth.py
3. สร้างโครงสร้างตาม Template
4. พัฒนา License Generator
5. พัฒนา License Validator
6. พัฒนา Hardware ID Binding
7. พัฒนา Login System (Offline Mode)
8. พัฒนา Registration System
9. พัฒนา License Server API
10. ทดสอบการทำงาน
11. อัพโหลดทั้งหมดไปยัง /backend/license/
12. รายงาน AI-01 เมื่อเสร็จ

## 📤 Output ที่ต้องส่ง

อัพโหลดไปยัง Google Drive: /dLNk-IDE-Project/backend/license/

## ⚠️ กฎการทำงาน

1. ใช้ Fernet Encryption เท่านั้น
2. Hardware ID ต้องรองรับ Windows และ Linux
3. Offline Mode ต้องทำงานได้ 7 วัน
4. รายงาน AI-01 เมื่อเสร็จหรือติดปัญหา

## 🔗 Dependencies

- AI-04 (UI) ต้องการ Login/Register API
- AI-05 (AI Bridge) อาจต้องการ Token validation
- AI-07 (Admin) ต้องการ License Management API

## 🎯 เริ่มต้นเลย!

ตอบกลับว่า "AI-06 License & Auth Developer พร้อมทำงาน" แล้วเริ่มดำเนินการตามขั้นตอนที่กำหนด
```

---

**หมายเหตุ:** คัดลอกข้อความทั้งหมดระหว่าง ``` และ ``` แล้วส่งให้ AI-06
