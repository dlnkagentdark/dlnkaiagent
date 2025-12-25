import json
import base64
import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# MASTER SECRET KEY (In a real scenario, obfuscate this!)
# This seed allows us to deterministically generate the encryption key
# so both the Admin Generator and the Client Launcher can derive the same key.
MASTER_SECRET = b"dLNk-AI-TOP-SECRET-MASTER-KEY-2025"
SALT = b"dlnk-static-salt"

def get_fernet():
    """Derive the Fernet key from the Master Secret."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(MASTER_SECRET))
    return Fernet(key)

def generate_license(days_valid=30, owner="Unknown"):
    """
    Generates an encrypted license key string.
    """
    f = get_fernet()
    
    expiry_date = (datetime.datetime.now() + datetime.timedelta(days=days_valid)).strftime("%Y-%m-%d")
    
    data = {
        "owner": owner,
        "expiry": expiry_date,
        "features": ["dark_mode", "god_mode", "unrestricted_ai"],
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Serialize to JSON then bytes
    json_data = json.dumps(data).encode('utf-8')
    
    # Encrypt
    token = f.encrypt(json_data)
    
    # Return as a string (the License Key)
    return token.decode('utf-8')

def validate_license(license_key_str):
    """
    Validates a license key.
    Returns: (is_valid, message, data_dict)
    """
    f = get_fernet()
    
    try:
        # Decrypt
        decrypted_data = f.decrypt(license_key_str.encode('utf-8'))
        data = json.loads(decrypted_data)
        
        # Check Expiry
        expiry_str = data.get("expiry")
        if not expiry_str:
            return False, "Invalid License Format: No expiry date", {}
            
        expiry_date = datetime.datetime.strptime(expiry_str, "%Y-%m-%d")
        if datetime.datetime.now() > expiry_date:
            return False, f"License Expired on {expiry_str}", data
            
        return True, "License Valid", data
        
    except Exception as e:
        return False, f"Invalid License Key: {str(e)}", {}

if __name__ == "__main__":
    # Internal Test
    test_key = generate_license(days=365, owner="AdminTest")
    print(f"Generated Test Key: {test_key}")
    valid, msg, info = validate_license(test_key)
    print(f"Validation: {valid} - {msg} - {info}")
