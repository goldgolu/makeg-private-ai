import os
import sys
import sqlite3
import subprocess
from utils import security, deployer
from games import airdrop, voice_commands

# कॉन्फ़िग
PASSWORD = "MakeG@Ultimate"  # अपना पासवर्ड बदलें
GAME_TEMPLATES = ["airdrop", "3d", "cricket", "racing"]

def main_menu():
    print("""
    ███╗░░░███╗░█████╗░██╗░░██╗███████╗░██████╗
    ████╗░████║██╔══██╗██║░██╔╝██╔════╝██╔════╝
    ██╔████╔██║███████║█████═╝░█████╗░░╚█████╗░
    ██║╚██╔╝██║██╔══██║██╔═██╗░██╔══╝░░░╚═══██╗
    ██║░╚═╝░██║██║░░██║██║░╚██╗███████╗██████╔╝
    ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝╚═════╝░
    """)
    
    # पासवर्ड चेक
    if not security.authenticate():
        sys.exit("🚫 अनधिकृत एक्सेस!")
    
    # मोड चुनें
    mode = input("चुनें (voice/text): ").lower()
    
    if mode == "voice":
        voice_commands.start_listening()
    else:
        handle_text_commands()

def handle_text_commands():
    while True:
        cmd = input("\nMakeG> ")
        
        # गेम सिस्टम
        if "game" in cmd:
            game_type = input("गेम का प्रकार: ")
            if game_type in GAME_TEMPLATES:
                airdrop.generate(game_type)
                deployer.to_telegram(game_type)
        
        # स्टोरेज मैनेजमेंट
        elif "delete" in cmd:
            target = cmd.split(" ")[1]
            security.wipe_data(target)
        
        # वेबसाइट बनाएं
        elif "website" in cmd:
            subprocess.run(["python", "utils/website_gen.py"])
        
        elif "exit" in cmd:
            break

if _name_ == "_main_":
    main_menu()
