import customtkinter as ctk
import dlnk_license_manager
import dlnk_db  # <--- NEW DATABASE MODULE
import subprocess
import threading
import time
import os
import sys
import webbrowser
from PIL import Image

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

TELEGRAM_LINK = "https://t.me/dlnkai" # บอส dLNk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("dLNk AI - ระบบอัจฉริยะ")
        self.geometry("500x550")
        self.resizable(False, False)
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # --- UI ELEMENTS ---
        
        # Logo (Keep logic)
        try:
            image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dlnk_logo.png")
            self.logo_image = ctk.CTkImage(Image.open(image_path), size=(200, 100))
            self.label_logo = ctk.CTkLabel(self, text="", image=self.logo_image)
            self.label_logo.grid(row=0, column=0, padx=20, pady=(30, 10))
        except Exception as e:
             self.label_title = ctk.CTkLabel(self, text="dLNk AI", font=("Roboto Medium", 36))
             self.label_title.grid(row=0, column=0, padx=20, pady=(30, 10))
             print(f"Logo load failed: {e}")

        
        self.label_subtitle = ctk.CTkLabel(self, text="ระบบปฏิบัติการระดับสูง (UNRESTRICTED)", font=("Prompt", 14), text_color="gray")
        self.label_subtitle.grid(row=1, column=0, padx=20, pady=(0, 20))

        # License Input
        self.entry_key = ctk.CTkEntry(self, placeholder_text="กรุณากรอกรหัสลิขสิทธิ์ (Key)", width=350, height=40, justify="center", font=("Prompt", 12))
        self.entry_key.grid(row=2, column=0, padx=20, pady=10)

        # Status Label
        self.label_status = ctk.CTkLabel(self, text="รอการเชื่อมต่อ...", text_color="gray", font=("Prompt", 12))
        self.label_status.grid(row=3, column=0, padx=20, pady=5)

        # Login Button
        self.button_login = ctk.CTkButton(self, text="เข้าสู่ระบบ", command=self.login_event, width=200, height=50, font=("Prompt Bold", 18), fg_color="#00FF00", text_color="black", hover_color="#00CC00")
        self.button_login.grid(row=4, column=0, padx=20, pady=20)
        
        # Contact Admin
        self.button_contact = ctk.CTkButton(self, text="[ ติดต่อทีมงาน ]", command=self.open_telegram, width=150, height=30, fg_color="transparent", border_width=1, text_color="gray", font=("Prompt", 12))
        self.button_contact.grid(row=5, column=0, padx=20, pady=(0, 20))

        # --- LOGIC VARIABLES ---
        self.proxy_process = None
        
        # Check for saved key
        if os.path.exists("dlnk_key.txt"):
            with open("dlnk_key.txt", "r") as f:
                saved_key = f.read().strip()
                self.entry_key.insert(0, saved_key)

    def open_telegram(self):
        webbrowser.open(TELEGRAM_LINK)

    def login_event(self):
        key = self.entry_key.get().strip()
        
        if not key:
            self.label_status.configure(text="[ERROR] Key required.", text_color="red")
            return

        self.button_login.configure(state="disabled", text="VERIFYING...")
        self.label_status.configure(text="Validating Neural Credentials...", text_color="yellow")
        
        # Run validation in separate thread to not freeze UI
        threading.Thread(target=self.validate_and_launch, args=(key,)).start()

    def validate_and_launch(self, key):
        time.sleep(1) 
        
        # 1. READ SERVER CONFIG
        SERVER_URL = "http://127.0.0.1:5000"
        if os.path.exists("server_ip.txt"):
            with open("server_ip.txt", "r") as f:
                SERVER_URL = f.read().strip()
        
        # 2. CALL ONLINE VERIFICATION
        try:
            hwid = os.getenv('COMPUTERNAME', 'Unknown')
            import requests
            r = requests.post(f"{SERVER_URL}/verify", json={"key": key, "hwid": hwid}, timeout=3)
            
            if r.status_code == 200:
                # SUCCESS
                self.label_status.configure(text=f"[AUTHORIZED] Welcome!", text_color="#00FF00")
                
                # Save key
                with open("dlnk_key.txt", "w") as f:
                    f.write(key)
                
                # Launch App
                self.perform_launch_sequence()
            else:
                # FAILED
                msg = r.json().get('message', 'Unknown Error')
                self.label_status.configure(text=f"[DENIED] {msg}", text_color="red")
                self.button_login.configure(state="normal", text="TRY AGAIN")
                
        except Exception as e:
            self.label_status.configure(text=f"[NETWORK ERROR] Cannot reach Server", text_color="red")
            self.button_login.configure(state="normal", text="RETRY CONNECT")

    def perform_launch_sequence(self):
        self.label_status.configure(text="Starting MITM Engine...", text_color="cyan")
        
        # 1. Start Proxy (Hidden)
        try:
           self.proxy_process = subprocess.Popen(
               ["python", "mitm_https_proxy.py"], # Relative path, assuming same dir
               stdout=subprocess.DEVNULL,
               stderr=subprocess.DEVNULL,
               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
           )
           time.sleep(2) # Wait for proxy startup
        except Exception as e:
            self.label_status.configure(text=f"[ERROR] Proxy Start Failed: {e}", text_color="red")
            return

        self.label_status.configure(text="Injecting VS Code Process...", text_color="cyan")
        time.sleep(1)

        # 2. Launch VS Code
        vscode_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\dLNk IDE\Code.exe"),
            r"C:\Program Files\dLNk IDE\Code.exe",
             r"C:\Program Files (x86)\dLNk IDE\Code.exe"
        ]
        
        vscode_exe = None
        for path in vscode_paths:
            if os.path.exists(path):
                vscode_exe = path
                break
        
        if vscode_exe:
            try:
                subprocess.Popen([
                    vscode_exe,
                    "--proxy-server=http://localhost:8081",
                    "--ignore-certificate-errors",
                    "--user-data-dir=dlnk_vscode_profile" # Use relative profile
                ])
                self.label_status.configure(text="[สถานะ] ระบบพร้อมใช้งานแล้ว", text_color="#00FF00")
                self.button_login.configure(text="กำลังทำงาน")
                
            except Exception as e:
                self.label_status.configure(text=f"[เกิดข้อผิดพลาด] ไม่สามารถเริ่ม VS Code ได้: {e}", text_color="red")
        else:
             self.label_status.configure(text="[เกิดข้อผิดพลาด] ไม่พบ VS Code ในเครื่อง", text_color="red")

if __name__ == "__main__":
    # Normal GUI Mode
    app = App()
    app.mainloop()
