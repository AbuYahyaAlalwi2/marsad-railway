import os
import time
import requests
import json
from huggingface_hub import HfApi

OR_KEY = os.environ.get("OR_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = "AbuYahya2/marsad-security-dataset-v1"

def collect_and_push():
    print("🔄 بدء دورة الجمع والتحديث...")
    headers = {
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://railway.app",
        "X-Title": "Marsad Worker"
    }
    payload = {
        "model": "apodex/apodex-1.1-mini:free",
        "messages": [{"role": "user", "content": "Generate a new cybersecurity tip."}]
    }
    
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            api = HfApi(token=HF_TOKEN)
            new_data = json.dumps({"prompt": "Cyber Tip", "response": content}) + "\n"
            api.upload_file(
                path_or_fileobj=new_data.encode(),
                path_in_repo="data/live_updates.jsonl",
                repo_id=REPO_ID,
                repo_type="dataset"
            )
            print("✅ تم التحديث بنجاح على Hugging Face.")
        else:
            print(f"❌ فشل الجمع: {resp.text}")
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    while True:
        collect_and_push()
        time.sleep(3600)
