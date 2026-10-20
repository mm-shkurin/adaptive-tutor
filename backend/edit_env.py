"""
Quick script to edit .env file
"""

import os

env_path = os.path.join(os.path.dirname(__file__), '.env')

if not os.path.exists(env_path):
    print(f"[ERROR] .env not found at {env_path}")
    print("Run: python create_env.py first")
    exit(1)

print(f"[INFO] Opening .env: {env_path}")
print()
print("[INSTRUCTIONS]")
print("1. Replace YOUR_UNIFIED_KEY_HERE with your unified API key")
print("2. Get the key at: http://localhost:3001 -> Keys")
print("3. Save and close the file")
print()

# Open with notepad
os.system(f"notepad {env_path}")

print()
print("[OK] Done! Now run: python test_freellmapi.py")
