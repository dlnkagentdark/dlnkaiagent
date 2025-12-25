"""
Hardware ID Generation - Cross-Platform Support
ระบบสร้าง Hardware ID สำหรับผูก License กับเครื่อง
รองรับ Windows, macOS, และ Linux

Version: 2.0.0
Updated: 2024-12-25
Author: AI-06 Auth & License API Developer

Features:
- Cross-platform support (Windows, macOS, Linux)
- Multiple hardware identifiers for reliability
- Fallback mechanisms for each platform
- Consistent HWID generation across reboots
- Short HWID format for user-friendly display
"""

import hashlib
import platform
import subprocess
import uuid
import os
import re
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger('dLNk-Hardware')


class Platform(Enum):
    """Supported platforms"""
    WINDOWS = "Windows"
    MACOS = "Darwin"
    LINUX = "Linux"
    UNKNOWN = "Unknown"


@dataclass
class HardwareComponent:
    """Hardware component information"""
    name: str
    value: str
    source: str
    reliable: bool = True


class HardwareID:
    """
    Cross-Platform Hardware ID Generator
    
    สร้าง Hardware ID ที่ไม่ซ้ำกันสำหรับแต่ละเครื่อง
    รองรับ Windows, macOS, และ Linux
    
    ใช้ข้อมูลจาก:
    - MAC Address (Primary network interface)
    - CPU ID / Serial
    - Disk Serial Number
    - Machine ID / UUID
    - Motherboard Serial (Windows)
    - Platform-specific identifiers
    """
    
    _cached_hwid: Optional[str] = None
    _cached_components: Optional[List[HardwareComponent]] = None
    
    @staticmethod
    def get_platform() -> Platform:
        """Get current platform"""
        system = platform.system()
        try:
            return Platform(system)
        except ValueError:
            return Platform.UNKNOWN
    
    @staticmethod
    def generate(use_cache: bool = True) -> str:
        """
        สร้าง Hardware ID จากข้อมูลระบบ
        
        Args:
            use_cache: ใช้ค่าที่ cache ไว้ (default: True)
        
        Returns:
            Hardware ID hash (SHA256, 64 characters)
        """
        if use_cache and HardwareID._cached_hwid:
            return HardwareID._cached_hwid
        
        components = HardwareID._collect_components()
        
        # Sort and combine components
        component_strings = [f"{c.name}:{c.value}" for c in components if c.value]
        
        if not component_strings:
            logger.warning("Could not get any hardware identifiers, using fallback")
            component_strings.append(f"fallback:{str(uuid.uuid4())}")
        
        combined = '|'.join(sorted(component_strings))
        hwid = hashlib.sha256(combined.encode()).hexdigest()
        
        # Cache the result
        HardwareID._cached_hwid = hwid
        HardwareID._cached_components = components
        
        return hwid
    
    @staticmethod
    def generate_short(length: int = 16) -> str:
        """
        สร้าง Hardware ID แบบสั้น
        
        Args:
            length: ความยาวของ HWID (default: 16)
        
        Returns:
            Short Hardware ID (uppercase)
        """
        return HardwareID.generate()[:length].upper()
    
    @staticmethod
    def _collect_components() -> List[HardwareComponent]:
        """Collect all hardware components"""
        components = []
        current_platform = HardwareID.get_platform()
        
        # MAC Address (all platforms)
        mac = HardwareID._get_mac_address()
        if mac:
            components.append(HardwareComponent("mac", mac, "uuid.getnode"))
        
        # Platform-specific components
        if current_platform == Platform.WINDOWS:
            components.extend(HardwareID._get_windows_components())
        elif current_platform == Platform.MACOS:
            components.extend(HardwareID._get_macos_components())
        elif current_platform == Platform.LINUX:
            components.extend(HardwareID._get_linux_components())
        
        # Fallback: hostname (all platforms)
        hostname = HardwareID._get_hostname()
        if hostname:
            components.append(HardwareComponent("host", hostname, "platform.node", reliable=False))
        
        return components
    
    # ==================== MAC Address ====================
    
    @staticmethod
    def _get_mac_address() -> Optional[str]:
        """Get primary MAC address"""
        try:
            mac_int = uuid.getnode()
            
            # Check if it's a real MAC (not random)
            # Random MACs have the multicast bit set
            if (mac_int >> 40) & 1:
                logger.debug("MAC address appears to be random")
                return None
            
            mac = ':'.join(['{:02x}'.format((mac_int >> ele) & 0xff)
                          for ele in range(0, 8*6, 8)][::-1])
            
            # Validate MAC format
            if mac and not mac.startswith('00:00:00'):
                return mac
            
            return None
        except Exception as e:
            logger.debug(f"Failed to get MAC address: {e}")
            return None
    
    # ==================== Windows Components ====================
    
    @staticmethod
    def _get_windows_components() -> List[HardwareComponent]:
        """Get Windows-specific hardware components"""
        components = []
        
        # CPU ID
        cpu_id = HardwareID._get_windows_cpu_id()
        if cpu_id:
            components.append(HardwareComponent("cpu", cpu_id, "wmic cpu"))
        
        # Disk Serial
        disk_serial = HardwareID._get_windows_disk_serial()
        if disk_serial:
            components.append(HardwareComponent("disk", disk_serial, "wmic diskdrive"))
        
        # Machine UUID
        machine_uuid = HardwareID._get_windows_machine_uuid()
        if machine_uuid:
            components.append(HardwareComponent("machine", machine_uuid, "wmic csproduct"))
        
        # Motherboard Serial
        mb_serial = HardwareID._get_windows_motherboard_serial()
        if mb_serial:
            components.append(HardwareComponent("motherboard", mb_serial, "wmic baseboard"))
        
        # BIOS Serial
        bios_serial = HardwareID._get_windows_bios_serial()
        if bios_serial:
            components.append(HardwareComponent("bios", bios_serial, "wmic bios"))
        
        return components
    
    @staticmethod
    def _get_windows_cpu_id() -> Optional[str]:
        """Get CPU ID on Windows"""
        try:
            output = subprocess.check_output(
                'wmic cpu get processorid',
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            lines = output.strip().split('\n')
            if len(lines) > 1:
                return lines[1].strip()
        except Exception as e:
            logger.debug(f"Failed to get Windows CPU ID: {e}")
        return None
    
    @staticmethod
    def _get_windows_disk_serial() -> Optional[str]:
        """Get disk serial on Windows"""
        try:
            output = subprocess.check_output(
                'wmic diskdrive get serialnumber',
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            lines = output.strip().split('\n')
            for line in lines[1:]:
                serial = line.strip()
                if serial and serial != 'SerialNumber':
                    return serial
        except Exception as e:
            logger.debug(f"Failed to get Windows disk serial: {e}")
        return None
    
    @staticmethod
    def _get_windows_machine_uuid() -> Optional[str]:
        """Get machine UUID on Windows"""
        try:
            output = subprocess.check_output(
                'wmic csproduct get uuid',
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            lines = output.strip().split('\n')
            if len(lines) > 1:
                uuid_val = lines[1].strip()
                if uuid_val and uuid_val != 'UUID':
                    return uuid_val
        except Exception as e:
            logger.debug(f"Failed to get Windows machine UUID: {e}")
        return None
    
    @staticmethod
    def _get_windows_motherboard_serial() -> Optional[str]:
        """Get motherboard serial on Windows"""
        try:
            output = subprocess.check_output(
                'wmic baseboard get serialnumber',
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            lines = output.strip().split('\n')
            if len(lines) > 1:
                serial = lines[1].strip()
                if serial and serial != 'SerialNumber' and serial != 'To be filled by O.E.M.':
                    return serial
        except Exception as e:
            logger.debug(f"Failed to get Windows motherboard serial: {e}")
        return None
    
    @staticmethod
    def _get_windows_bios_serial() -> Optional[str]:
        """Get BIOS serial on Windows"""
        try:
            output = subprocess.check_output(
                'wmic bios get serialnumber',
                shell=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            lines = output.strip().split('\n')
            if len(lines) > 1:
                serial = lines[1].strip()
                if serial and serial != 'SerialNumber' and serial != 'To be filled by O.E.M.':
                    return serial
        except Exception as e:
            logger.debug(f"Failed to get Windows BIOS serial: {e}")
        return None
    
    # ==================== macOS Components ====================
    
    @staticmethod
    def _get_macos_components() -> List[HardwareComponent]:
        """Get macOS-specific hardware components"""
        components = []
        
        # Platform UUID (IOPlatformUUID)
        platform_uuid = HardwareID._get_macos_platform_uuid()
        if platform_uuid:
            components.append(HardwareComponent("machine", platform_uuid, "ioreg"))
        
        # Hardware UUID
        hw_uuid = HardwareID._get_macos_hardware_uuid()
        if hw_uuid:
            components.append(HardwareComponent("hw_uuid", hw_uuid, "system_profiler"))
        
        # Serial Number
        serial = HardwareID._get_macos_serial_number()
        if serial:
            components.append(HardwareComponent("serial", serial, "system_profiler"))
        
        # CPU Brand (hashed)
        cpu_brand = HardwareID._get_macos_cpu_brand()
        if cpu_brand:
            cpu_hash = hashlib.md5(cpu_brand.encode()).hexdigest()[:16]
            components.append(HardwareComponent("cpu", cpu_hash, "sysctl"))
        
        # Disk Serial
        disk_serial = HardwareID._get_macos_disk_serial()
        if disk_serial:
            components.append(HardwareComponent("disk", disk_serial, "system_profiler"))
        
        return components
    
    @staticmethod
    def _get_macos_platform_uuid() -> Optional[str]:
        """Get IOPlatformUUID on macOS"""
        try:
            output = subprocess.check_output(
                ['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'],
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            
            for line in output.split('\n'):
                if 'IOPlatformUUID' in line:
                    # Extract UUID from line like: "IOPlatformUUID" = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
                    match = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', line)
                    if match:
                        return match.group(1)
        except Exception as e:
            logger.debug(f"Failed to get macOS platform UUID: {e}")
        return None
    
    @staticmethod
    def _get_macos_hardware_uuid() -> Optional[str]:
        """Get Hardware UUID on macOS"""
        try:
            output = subprocess.check_output(
                ['system_profiler', 'SPHardwareDataType'],
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode()
            
            for line in output.split('\n'):
                if 'Hardware UUID' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        return parts[1].strip()
        except Exception as e:
            logger.debug(f"Failed to get macOS hardware UUID: {e}")
        return None
    
    @staticmethod
    def _get_macos_serial_number() -> Optional[str]:
        """Get serial number on macOS"""
        try:
            output = subprocess.check_output(
                ['system_profiler', 'SPHardwareDataType'],
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode()
            
            for line in output.split('\n'):
                if 'Serial Number' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        return parts[1].strip()
        except Exception as e:
            logger.debug(f"Failed to get macOS serial number: {e}")
        return None
    
    @staticmethod
    def _get_macos_cpu_brand() -> Optional[str]:
        """Get CPU brand string on macOS"""
        try:
            output = subprocess.check_output(
                ['sysctl', '-n', 'machdep.cpu.brand_string'],
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode().strip()
            return output if output else None
        except Exception as e:
            logger.debug(f"Failed to get macOS CPU brand: {e}")
        return None
    
    @staticmethod
    def _get_macos_disk_serial() -> Optional[str]:
        """Get disk serial on macOS"""
        try:
            # Try NVMe first (Apple Silicon and newer Macs)
            output = subprocess.check_output(
                ['system_profiler', 'SPNVMeDataType'],
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode()
            
            for line in output.split('\n'):
                if 'Serial Number' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        serial = parts[1].strip()
                        if serial:
                            return serial
            
            # Fallback to SATA
            output = subprocess.check_output(
                ['system_profiler', 'SPSerialATADataType'],
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode()
            
            for line in output.split('\n'):
                if 'Serial Number' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        serial = parts[1].strip()
                        if serial:
                            return serial
                            
        except Exception as e:
            logger.debug(f"Failed to get macOS disk serial: {e}")
        return None
    
    # ==================== Linux Components ====================
    
    @staticmethod
    def _get_linux_components() -> List[HardwareComponent]:
        """Get Linux-specific hardware components"""
        components = []
        
        # Machine ID
        machine_id = HardwareID._get_linux_machine_id()
        if machine_id:
            components.append(HardwareComponent("machine", machine_id, "/etc/machine-id"))
        
        # Product UUID (from DMI)
        product_uuid = HardwareID._get_linux_product_uuid()
        if product_uuid:
            components.append(HardwareComponent("product_uuid", product_uuid, "dmi"))
        
        # CPU ID
        cpu_id = HardwareID._get_linux_cpu_id()
        if cpu_id:
            components.append(HardwareComponent("cpu", cpu_id, "/proc/cpuinfo"))
        
        # Disk Serial
        disk_serial = HardwareID._get_linux_disk_serial()
        if disk_serial:
            components.append(HardwareComponent("disk", disk_serial, "lsblk"))
        
        # Board Serial
        board_serial = HardwareID._get_linux_board_serial()
        if board_serial:
            components.append(HardwareComponent("board", board_serial, "dmi"))
        
        return components
    
    @staticmethod
    def _get_linux_machine_id() -> Optional[str]:
        """Get machine ID on Linux"""
        paths = [
            '/etc/machine-id',
            '/var/lib/dbus/machine-id'
        ]
        
        for path in paths:
            try:
                with open(path, 'r') as f:
                    machine_id = f.read().strip()
                    if machine_id:
                        return machine_id
            except (FileNotFoundError, PermissionError):
                continue
        
        return None
    
    @staticmethod
    def _get_linux_product_uuid() -> Optional[str]:
        """Get product UUID on Linux"""
        paths = [
            '/sys/class/dmi/id/product_uuid',
            '/sys/devices/virtual/dmi/id/product_uuid'
        ]
        
        for path in paths:
            try:
                with open(path, 'r') as f:
                    uuid_val = f.read().strip()
                    if uuid_val and uuid_val != 'None':
                        return uuid_val
            except (FileNotFoundError, PermissionError):
                continue
        
        # Try dmidecode as fallback
        try:
            output = subprocess.check_output(
                ['sudo', 'dmidecode', '-s', 'system-uuid'],
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode().strip()
            if output and output != 'Not Settable':
                return output
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _get_linux_cpu_id() -> Optional[str]:
        """Get CPU ID on Linux"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                content = f.read()
                
                # Try to find CPU serial
                for line in content.split('\n'):
                    if line.lower().startswith('serial'):
                        parts = line.split(':')
                        if len(parts) > 1:
                            return parts[1].strip()
                
                # Fallback: hash model name
                for line in content.split('\n'):
                    if 'model name' in line.lower():
                        parts = line.split(':')
                        if len(parts) > 1:
                            model = parts[1].strip()
                            return hashlib.md5(model.encode()).hexdigest()[:16]
                            
        except (FileNotFoundError, PermissionError) as e:
            logger.debug(f"Failed to read /proc/cpuinfo: {e}")
        
        return None
    
    @staticmethod
    def _get_linux_disk_serial() -> Optional[str]:
        """Get disk serial on Linux"""
        # Try lsblk first
        try:
            output = subprocess.check_output(
                ['lsblk', '-o', 'SERIAL', '-n', '-d'],
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            
            for line in output.strip().split('\n'):
                serial = line.strip()
                if serial:
                    return serial
        except Exception:
            pass
        
        # Try /dev/disk/by-id
        try:
            disk_by_id = '/dev/disk/by-id'
            if os.path.exists(disk_by_id):
                for disk in sorted(os.listdir(disk_by_id)):
                    # Prefer ata or nvme disks
                    if disk.startswith(('ata-', 'nvme-', 'scsi-')):
                        # Extract serial from disk name
                        return hashlib.md5(disk.encode()).hexdigest()[:16]
        except Exception:
            pass
        
        # Try hdparm (requires root)
        try:
            output = subprocess.check_output(
                ['sudo', 'hdparm', '-I', '/dev/sda'],
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            
            for line in output.split('\n'):
                if 'Serial Number' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        return parts[1].strip()
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _get_linux_board_serial() -> Optional[str]:
        """Get board serial on Linux"""
        paths = [
            '/sys/class/dmi/id/board_serial',
            '/sys/devices/virtual/dmi/id/board_serial'
        ]
        
        for path in paths:
            try:
                with open(path, 'r') as f:
                    serial = f.read().strip()
                    if serial and serial != 'None' and serial != 'To be filled by O.E.M.':
                        return serial
            except (FileNotFoundError, PermissionError):
                continue
        
        return None
    
    # ==================== Common Methods ====================
    
    @staticmethod
    def _get_hostname() -> Optional[str]:
        """Get hostname (all platforms)"""
        try:
            return platform.node()
        except Exception:
            return None
    
    @staticmethod
    def get_system_info() -> Dict:
        """
        ดึงข้อมูลระบบทั้งหมด
        
        Returns:
            Dictionary ของข้อมูลระบบ
        """
        # Generate HWID to populate cache
        hwid = HardwareID.generate()
        
        components_dict = {}
        if HardwareID._cached_components:
            for comp in HardwareID._cached_components:
                components_dict[comp.name] = {
                    "value": comp.value,
                    "source": comp.source,
                    "reliable": comp.reliable
                }
        
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'mac_address': HardwareID._get_mac_address(),
            'hardware_id': hwid,
            'hardware_id_short': HardwareID.generate_short(),
            'components': components_dict,
            'component_count': len(components_dict)
        }
    
    @staticmethod
    def verify_hardware_id(stored_hwid: str, current_hwid: str = None) -> Tuple[bool, str]:
        """
        ตรวจสอบว่า Hardware ID ตรงกันหรือไม่
        
        Args:
            stored_hwid: Hardware ID ที่เก็บไว้
            current_hwid: Hardware ID ปัจจุบัน (ถ้าไม่ระบุจะสร้างใหม่)
        
        Returns:
            Tuple of (is_match, message)
        """
        if current_hwid is None:
            current_hwid = HardwareID.generate()
        
        if stored_hwid == current_hwid:
            return True, "Hardware ID matches"
        
        # Check short version match (for backward compatibility)
        if len(stored_hwid) == 16:
            if stored_hwid == current_hwid[:16].upper():
                return True, "Hardware ID matches (short format)"
        
        return False, "Hardware ID mismatch"
    
    @staticmethod
    def clear_cache():
        """Clear cached HWID"""
        HardwareID._cached_hwid = None
        HardwareID._cached_components = None


# ==================== Convenience Functions ====================

def get_hardware_id() -> str:
    """Get current hardware ID"""
    return HardwareID.generate()


def get_hardware_id_short() -> str:
    """Get short hardware ID (16 characters)"""
    return HardwareID.generate_short()


def verify_hardware(stored_hwid: str) -> bool:
    """Verify hardware ID"""
    is_match, _ = HardwareID.verify_hardware_id(stored_hwid)
    return is_match


def get_system_info() -> Dict:
    """Get system information"""
    return HardwareID.get_system_info()


def get_platform() -> str:
    """Get current platform name"""
    return HardwareID.get_platform().value


# ==================== CLI Interface ====================

if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("dLNk IDE - Hardware ID Generator")
    print("=" * 60)
    print()
    
    info = HardwareID.get_system_info()
    
    print(f"Platform: {info['platform']} ({info['platform_release']})")
    print(f"Architecture: {info['architecture']}")
    print(f"Hostname: {info['hostname']}")
    print()
    print(f"Hardware ID: {info['hardware_id']}")
    print(f"Hardware ID (Short): {info['hardware_id_short']}")
    print()
    print("Components detected:")
    for name, comp in info['components'].items():
        reliability = "✓" if comp['reliable'] else "○"
        print(f"  {reliability} {name}: {comp['value'][:32]}... (from {comp['source']})")
    print()
    print(f"Total components: {info['component_count']}")
