"""
Скрипт для создания .env файла с шаблоном
Запустите: python create_env.py
"""

import os

env_content = """# AdaptiveTutor Backend Environment Variables

# FreeLLMAPI Configuration
FREE_LLM_API_URL=http://localhost:3001/v1
FREE_LLM_API_KEY=YOUR_UNIFIED_KEY_HERE

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/adaptive_tutor

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Server
PORT=8000
HOST=0.0.0.0
"""

env_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(env_path):
    print(f"[WARNING] File .env already exists at {env_path}")
    print("   If you want to overwrite, delete it first.")
    overwrite = input("Overwrite? (y/n): ")
    if overwrite.lower() != 'y':
        print("Cancelled.")
        exit(0)

with open(env_path, 'w', encoding='utf-8') as f:
    f.write(env_content)

print(f"[OK] File .env created: {env_path}")
print()
print("[IMPORTANT] Open .env and replace YOUR_UNIFIED_KEY_HERE with your unified API key")
print("   Get the key at http://localhost:3001 -> Keys")
