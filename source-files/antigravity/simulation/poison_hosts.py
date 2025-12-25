import os
import sys
import ctypes

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_ENTRY = "127.0.0.1 example.com"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def poison():
    print(f"[*] Poisoning Hosts File: {HOSTS_PATH}")
    try:
        with open(HOSTS_PATH, "r") as f:
            content = f.read()
            
        if REDIRECT_ENTRY in content:
            print("[!] Entry already exists. Skipping.")
        else:
            with open(HOSTS_PATH, "a") as f:
                f.write(f"\n{REDIRECT_ENTRY}\n")
            print("[+] Hosts file poisoned successfully.")
            
    except Exception as e:
        print(f"[!] Error: {e}")

def cleanup():
    print(f"[*] Cleaning up Hosts File...")
    try:
        with open(HOSTS_PATH, "r") as f:
            lines = f.readlines()
        
        with open(HOSTS_PATH, "w") as f:
            for line in lines:
                if REDIRECT_ENTRY not in line:
                    f.write(line)
        print("[+] Hosts file restored.")
    except Exception as e:
        print(f"[!] Error during cleanup: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        if is_admin():
            cleanup()
            input("Press Enter to exit...")
        else:
             ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        if is_admin():
            poison()
            input("Press Enter to exit...")
        else:
            # Re-run the program with admin rights
            print("[*] Requesting Admin privileges...")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
