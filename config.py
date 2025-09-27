# config.py
TOKEN = ""
API_BASE_URL = ""
API_KEY = ""

# 管理員 ID
ADMIN_ID = 
R18_ROLE_IDS = [] 

# AI 角色定義檔案
ROLE_FILE = "role.txt"

# 讀取 role.txt 內容作為 AI_ROLE
try:
    with open(ROLE_FILE, "r", encoding="utf-8") as f:
        AI_ROLE = f.read().strip()
except FileNotFoundError:
    AI_ROLE = "你是一個有禮貌的聊天助理。"

# 使用的模型
MODEL_NAME = "gpt-3.5-turbo"
