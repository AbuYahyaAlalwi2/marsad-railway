import os
import time
import requests
import json
import random
from huggingface_hub import HfApi

OR_KEY = os.environ.get("OR_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = "AbuYahyaAlalwi2/marsad-security-dataset-v1"

# قائمة المهام الأمنية المتنوعة
TASKS = [
    {"type": "vuln_code", "prompt": "Generate a Python code snippet with a SQL Injection vulnerability."},
    {"type": "fix_code", "prompt": "Here is vulnerable code: 'cursor.execute(f\"SELECT * FROM users WHERE id={user_id}\")'. Provide the secure fixed version using parameterized queries."},
    {"type": "explanation", "prompt": "Explain how Cross-Site Scripting (XSS) works in modern web apps and list 3 prevention methods."},
    {"type": "deobfuscation", "prompt": "Deobfuscate this JS code conceptually: 'var _0x1a2b = function() { return \"malicious_payload\"; }'. Explain what it does."},
    {"type": "filtering", "prompt": "Analyze this log entry for anomalies: 'GET /admin/../etc/passwd HTTP/1.1'. Is it an attack? Why?"}
]

api = HfApi(token=HF_TOKEN)

def collect_and_push():
    # اختيار مهمة عشوائية لضمان التنوع
    task = random.choice(TASKS)
    print(f"🔄 [{task['type'].upper()}] جاري الجمع...")
    
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://railway.app",
        "X-Title": "Marsad Pro Worker"
    }
    
    payload = {
        "model": "meta-llama/llama-3-8b-instruct:free", # نموذج قوي ومجاني
        "messages": [{"role": "user", "content": task['prompt']}]
    }
    
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=20)
        
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            
            # تنسيق البيانات النهائية
            final_entry = json.dumps({
                "category": task['type'],
                "prompt": task['prompt'],
                "response": content,
                "timestamp": time.time()
            }, ensure_ascii=False) + "\n"
            
            # الرفع المباشر لـ Hugging Face
            api.upload_file(
                path_or_fileobj=final_entry.encode(),
                path_in_repo="data/pro_collection.jsonl",
                repo_id=REPO_ID,
                repo_type="dataset"
            )
            print(f"✅ تم رفع بيانات [{task['type']}] بنجاح.")
        else:
            print(f"⚠️ تأخير طفيف من API ({resp.status_code})، إعادة المحاولة بعد 5 ثوانٍ...")
            time.sleep(5)
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        time.sleep(10) # انتظار أطول عند الخطأ

if __name__ == "__main__":
    print("🚀 بدء محرك الجمع المتواصل (No-Sleep Mode)...")
    while True:
        collect_and_push()
        # لا يوجد time.sleep طويل؛ الدورة التالية تبدأ فور انتهاء السابقة
