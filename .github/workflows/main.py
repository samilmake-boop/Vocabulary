import os
import json
import base64
import requests
from openai import OpenAI

# ==========================================
# 1. LOAD SECRETS FROM GITHUB ENVIRONMENT
# ==========================================
QWEN_API_KEY = os.environ.get("DASHSCOPE_API_KEY")
WP_SITE_URL = os.environ.get("WP_SITE_URL")
WP_USERNAME = os.environ.get("WP_USERNAME")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")

# ==========================================
# 2. LOAD RAW DATA FROM TEXT FILE
# ==========================================
def load_raw_data():
    with open("raw_data.txt", "r", encoding="utf-8") as file:
        return file.read()

# ==========================================
# 3. QWEN SEO AGENT LOGIC
# ==========================================
def generate_seo_article(raw_data):
    print("🤖 Qwen Cloud Agent is writing the article...")
    
    client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    prompt = f"""
    You are an expert SEO Content Writer and a Bilingual (English/Punjabi) Language Teacher.
    Transform the raw vocabulary data below into a highly readable, SEO-optimized HTML article.

    RAW DATA:
    {raw_data}

    SEO & FORMATTING RULES:
    1. DO NOT use <h1> tags. WordPress handles the H1. Start with <h2>.
    2. Use <h2> for main sections, <h3> for sub-sections.
    3. Use <strong> for English words and <em> for Punjabi words.
    4. Use <ul> and <li> for lists (Synonyms, Antonyms, Phrases).
    5. Keep the Punjabi (Gurmukhi) text EXACTLY as provided.
    6. Add a brief, engaging intro paragraph before the first <h2>.
    7. Output clean HTML only. NO markdown blocks (no ```html).

    OUTPUT FORMAT:
    Return ONLY a valid JSON object with these keys:
    1. "title": SEO-optimized H1 Title.
    2. "excerpt": 150-character SEO meta description.
    3. "content": Full clean HTML content.
    """

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" },
        temperature=0.2
    )
    
    result = json.loads(response.choices[0].message.content)
    return result['title'], result['excerpt'], result['content']

# ==========================================
# 4. WORDPRESS INTEGRATION
# ==========================================
def save_to_wordpress(title, excerpt, content):
    print("🚀 Uploading to WordPress...")
    
    url = f"{WP_SITE_URL}/wp-json/wp/v2/posts"
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'title': title,
        'excerpt': excerpt,
        'content': content,
        'status': 'draft' 
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        post_data = response.json()
        print(f"✅ SUCCESS! Draft saved.")
        print(f"🔗 Edit link: {post_data['link']}")
    else:
        print(f"❌ FAILED. Status: {response.status_code}")
        print(f"Error: {response.text}")

# ==========================================
# 5. EXECUTE
# ==========================================
if __name__ == "__main__":
    try:
        raw_text = load_raw_data()
        t, e, c = generate_seo_article(raw_text)
        save_to_wordpress(t, e, c)
    except Exception as e:
        print(f"An error occurred: {e}")
