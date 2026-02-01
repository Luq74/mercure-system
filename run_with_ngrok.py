import os
import sys
import time
import re
import subprocess
from pyngrok import ngrok, conf

# Configuration
TOKEN_FILE = "token_ngrok.txt"
BOT_FILE = "bot.py"
PORT = 5001

def get_auth_token():
    try:
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading {TOKEN_FILE}: {e}")
        sys.exit(1)

def main():
    # 1. Authenticate Ngrok
    print("Authenticating Ngrok...")
    NGROK_AUTH_TOKEN = get_auth_token()
    try:
        conf.get_default().auth_token = NGROK_AUTH_TOKEN
    except Exception as e:
        print(f"Error setting auth token: {e}")
        sys.exit(1)
    
    # 2. Start Ngrok Tunnel
    print("Starting Ngrok Tunnel...")
    try:
        # Close any existing tunnels
        ngrok.kill()
        
        # Start new tunnel
        tunnel = ngrok.connect(PORT)
        public_url = tunnel.public_url.replace("http://", "https://") # Ensure HTTPS
        print(f"Ngrok Tunnel Started: {public_url}")
    except Exception as e:
        print(f"Error starting Ngrok: {e}")
        sys.exit(1)

    # 3. Update bot.py with the new URL
    print(f"Updating {BOT_FILE} with new URL...")
    try:
        with open(BOT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to replace URL_BASE = "..."
        new_content = re.sub(
            r'URL_BASE\s*=\s*["\'].*?["\']',
            f'URL_BASE = "{public_url}"',
            content
        )
        
        with open(BOT_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print("URL updated successfully.")
        
    except Exception as e:
        print(f"Error updating {BOT_FILE}: {e}")
        ngrok.kill()
        sys.exit(1)

    # 4. Run bot.py
    print("Starting bot...")
    try:
        subprocess.run([sys.executable, BOT_FILE], check=True)
    except KeyboardInterrupt:
        print("\nStopping bot and Ngrok...")
    except Exception as e:
        print(f"Error running bot: {e}")
    finally:
        ngrok.kill()
        print("Ngrok stopped.")

if __name__ == "__main__":
    main()
