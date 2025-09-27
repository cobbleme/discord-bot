# config.py
TOKEN = "MTQwMDY5MzIzMTA3OTAwMjE1Mg.GwTpfN.tGVMYbheTXLnajCbxhDduwpFKRTFM5dkLGEBnM"
API_BASE_URL = "https://api.chatanywhere.org/v1/chat/completions"
API_KEY = "sk-oqwoGqHp8JkkLhm7lQGskikSs56disdB207ReSMNe5Viv9ub"

# 管理員 ID
ADMIN_ID = 896248532032421918
R18_ROLE_IDS = [1406554349991235615] 

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
