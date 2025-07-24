# README - PhantomStealer

---

### Developed by: MR MONSIF H4CK3R  
### Disclaimer: This tool is for authorized research and red team use only. Unauthorized use is illegal.

---

## Overview

PhantomStealer is an advanced credential harvesting tool designed to extract stored passwords and other sensitive data from browsers like Microsoft Edge and Google Chrome, as well as Windows credentials and Wi-Fi profiles. It compiles this data into detailed reports and sends them securely via Telegram.

---

## Features

- Extracts saved passwords and usernames from Microsoft Edge and Google Chrome  
- Retrieves Windows saved credentials  
- Extracts Wi-Fi profiles and their passwords  
- Generates detailed reports and sends them to Telegram  
- Runs stealthily without console window  
- Supports persistence and anti-forensics techniques  
- Includes screenshot capture to complement data exfiltration

---

## Known Issue

- **Chrome Password Decryption:**  
Due to recent updates in Google Chrome’s encryption methods, the current decryption logic may fail to decrypt some Chrome passwords. This is a known limitation and requires updating the AES decryption mechanism or extraction of Chrome's "Local State" master key correctly.

---

## Usage

1. Update your Telegram Bot token and Chat ID in the script.  
2. Run the script on a target Windows machine with the required permissions.  
3. The tool will collect credentials and send reports via Telegram periodically.  
4. Convert to executable with PyInstaller for deployment:
 
   ```bash
   pyinstaller --onefile --noconsole --icon your_icon.ico phantom_stealer.py
