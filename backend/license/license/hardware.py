"""
Hardware ID Generation
ระบบสร้าง Hardware ID สำหรับผูก License กับเครื่อง
รองรับทั้ง Windows และ Linux
"""

import hashlib
import platform
import subprocess
import uuid
from typing import Optional, List
import logging

logger = logging.getLogger('dLNk-Hardware')


class HardwareID:
    """
    สร้าง Hardware ID ที่ไม่ซ้ำกันสำหรับแต่ละเครื่อง
    
    ใช้ข้อมูลจาก:
    - MAC Address
    - CPU ID
    - Disk Serial
    - Machine ID
    """
    
    @staticmethod
    def generate() -> str:
        """
        สร้าง Hardware ID จากข้อมูลระบบ
        
        Returns:
            Hardware ID hash (SHA256)
        """
        components = []
        
        # Get MAC address
        mac = HardwareID._get_mac_address()
        if mac:
            components.append(f"mac:{mac}")
        
        # Get CPU ID
        cpu_id = HardwareID._get_cpu_id()
        if cpu_id:
            components.append(f"cpu:{cpu_id}")
        
        # Get Disk Serial
        disk_serial = HardwareID._get_disk_serial()
        if disk_serial:
            components.append(f"disk:{disk_serial}")
        
        # Get Machine ID
        machine_id = HardwareID._get_machine_id()
        if machine_id:
            components.append(f"machine:{machine_id}")
        
        # Get hostname as fallback
        hostname = HardwareID._get_hostname()
        if hostname:
            components.append(f"host:{hostname}")
        
        # If no components found, use a random UUID (not ideal but prevents crash)
        if not components:
            logger.warning("Could not get any hardware identifiers, using random UUID")
            components.append(f"random:{str(uuid.uuid4())}")
        
        # Combine and hash
        combined = '|'.join(sorted(components))
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def generate_short() -> str:
        """สร้าง Hardware ID แบบสั้น (16 ตัวอักษร)"""
        return HardwareID.generate()[:16].upper()
    
    @staticmethod
    def _get_mac_address() -> Optional[str]:
        """Get MAC address"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                          for ele in range(0, 8*6, 8)][::-1])
            # Check if it's a real MAC (not random)
            if mac and not mac.startswith('00:00:00'):
                return mac
            return None
        except Exception as e:
            logger.debug(f"Failed to get MAC address: {e}")
            return None
    
    @staticmethod
    def _get_cpu_id() -> Optional[str]:
        """Get CPU ID"""
        try:
            system = platform.system()
            
            if system == 'Windows':
                output = subprocess.check_output(
                    'wmic cpu get processorid',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode()
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
                    
            elif system == 'Linux':
                # Try /proc/cpuinfo
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if 'Serial' in line or 'serial' in line:
                                return line.split(':')[1].strip()
                            if 'model name' in line:
                                # Use model name as fallback
                                return hashlib.md5(line.split(':')[1].strip().encode()).hexdigest()[:16]
                except FileNotFoundError:
                    pass
                
                # Try dmidecode
                try:
                    output = subprocess.check_output(
                        ['sudo', 'dmidecode', '-t', 'processor'],
                        stderr=subprocess.DEVNULL
                    ).decode()
                    for line in output.split('\n'):
                        if 'ID:' in line:
                            return line.split(':')[1].strip().replace(' ', '')
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                    
            elif system == 'Darwin':  # macOS
                output = subprocess.check_output(
                    ['sysctl', '-n', 'machdep.cpu.brand_string'],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                return hashlib.md5(output.encode()).hexdigest()[:16]
                
            return None
        except Exception as e:
            logger.debug(f"Failed to get CPU ID: {e}")
            return None
    
    @staticmethod
    def _get_disk_serial() -> Optional[str]:
        """Get disk serial number"""
        try:
            system = platform.system()
            
            if system == 'Windows':
                output = subprocess.check_output(
                    'wmic diskdrive get serialnumber',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode()
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    serial = lines[1].strip()
                    if serial:
                        return serial
                        
            elif system == 'Linux':
                # Try lsblk
                try:
                    output = subprocess.check_output(
                        ['lsblk', '-o', 'SERIAL', '-n'],
                        stderr=subprocess.DEVNULL
                    ).decode()
                    lines = output.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            return line.strip()
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                
                # Try /dev/disk/by-id
                try:
                    import os
                    disk_by_id = '/dev/disk/by-id'
                    if os.path.exists(disk_by_id):
                        for disk in os.listdir(disk_by_id):
                            if 'ata-' in disk or 'nvme-' in disk:
                                return hashlib.md5(disk.encode()).hexdigest()[:16]
                except Exception:
                    pass
                    
            elif system == 'Darwin':  # macOS
                output = subprocess.check_output(
                    ['system_profiler', 'SPSerialATADataType'],
                    stderr=subprocess.DEVNULL
                ).decode()
                for line in output.split('\n'):
                    if 'Serial Number' in line:
                        return line.split(':')[1].strip()
                        
            return None
        except Exception as e:
            logger.debug(f"Failed to get disk serial: {e}")
            return None
    
    @staticmethod
    def _get_machine_id() -> Optional[str]:
        """Get machine ID"""
        try:
            system = platform.system()
            
            if system == 'Linux':
                # Try /etc/machine-id
                try:
                    with open('/etc/machine-id', 'r') as f:
                        return f.read().strip()
                except FileNotFoundError:
                    pass
                
                # Try /var/lib/dbus/machine-id
                try:
                    with open('/var/lib/dbus/machine-id', 'r') as f:
                        return f.read().strip()
                except FileNotFoundError:
                    pass
                    
            elif system == 'Windows':
                output = subprocess.check_output(
                    'wmic csproduct get uuid',
                    shell=True,
                    stderr=subprocess.DEVNULL
                ).decode()
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
                    
            elif system == 'Darwin':  # macOS
                output = subprocess.check_output(
                    ['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'],
                    stderr=subprocess.DEVNULL
                ).decode()
                for line in output.split('\n'):
                    if 'IOPlatformUUID' in line:
                        return line.split('"')[3]
                        
            return None
        except Exception as e:
            logger.debug(f"Failed to get machine ID: {e}")
            return None
    
    @staticmethod
    def _get_hostname() -> Optional[str]:
        """Get hostname"""
        try:
            return platform.node()
        except Exception:
            return None
    
    @staticmethod
    def get_system_info() -> dict:
        """
        ดึงข้อมูลระบบทั้งหมด
        
        Returns:
            Dictionary ของข้อมูลระบบ
        """
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'mac_address': HardwareID._get_mac_address(),
            'hardware_id': HardwareID.generate(),
            'hardware_id_short': HardwareID.generate_short()
        }
    
    @staticmethod
    def verify_hardware_id(stored_hwid: str, current_hwid: str = None) -> bool:
        """
        ตรวจสอบว่า Hardware ID ตรงกันหรือไม่
        
        Args:
            stored_hwid: Hardware ID ที่เก็บไว้
            current_hwid: Hardware ID ปัจจุบัน (ถ้าไม่ระบุจะสร้างใหม่)
        
        Returns:
            True ถ้าตรงกัน
        """
        if current_hwid is None:
            current_hwid = HardwareID.generate()
        return stored_hwid == current_hwid


# Convenience functions
def get_hardware_id() -> str:
    """Get current hardware ID"""
    return HardwareID.generate()


def get_hardware_id_short() -> str:
    """Get short hardware ID"""
    return HardwareID.generate_short()


def verify_hardware(stored_hwid: str) -> bool:
    """Verify hardware ID"""
    return HardwareID.verify_hardware_id(stored_hwid)
