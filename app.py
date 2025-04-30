# We'll update the GPT evaluation function to return structured sections and also redesign the Streamlit layout.

structured_dashboard_code = """
import streamlit as st
import requests
import openai

# Load API keys
openai.api_key = st.secrets["OPENAI_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

headers = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json"
}

def search_creator_online(query):
    url = "https://google.serper.dev/search"
    data = {"q": query}
    res = requests.post(url, json=data, headers=headers)
    return res.json()

def extract_links_and_bios(results):
    links = {}
    bios = []
    for result in results.get("organic", []):
        link = result.get("link", "")
        snippet = result.get("snippet", "")
        bios.append(snippet)
        if "youtube.com" in link:
            links["YouTube"] = link
        elif "linkedin.com" in link:
            links["LinkedIn"] = link
        elif "tiktok.com" in link:
            links["TikTok"] = link
        elif "instagram.com" in link:
            links["Instagram"] = link
        elif "twitter.com" in link:
            links["Twitter"] = link
        elif "substack.com" in link:
            links["Substack"] = link
        elif "podcasts.apple.com" in link:
            links["Podcast"] = link
        elif "medium.com" in link:
            links["Medium"] = link
        else:
            if "Website" not in links:
                links["Website"] = link
    return links, bios

def evaluate_creator_with_gpt_structured(bio_text):
    prompt = f'''
You are an expert brand evaluator at HubSpot. Review the following content and return your evaluation as structured markdown with clear formatting for Streamlit display.

Content:
\"\"\"
{bio_text}
\"\"\"

Output in the following markdown structure:

### 🌐 Creator Overview
Short summary of who the creator is and their platforms.

### 🧠 Content Snapshot
Summarize tone, themes, and style in 2–3 sentences.

### 🎯 Audience Fit: Growth Gabby
- **Fit Score:** Strong / Medium / Weak
- **Why:** (Short explanation)

### 🧯 Brand Safety & HEART Values
- **Brand Risk Level:** Green / Yellow / Red
- **Why:** (Explain risk level in 2–3 sentences)
- **Humble:** Yes/No – reason
- **Empathetic:** Yes/No – reason
- **Adaptable:** Yes/No – reason
- **Remarkable:** Yes/No – reason
- **Transparent:** Yes/No – reason

### ✅ Final Recommendation
- **Decision:** ✅ Proceed / ⚠️ Conditional / 🛑 Decline
- **Why:** Short rationale (2–3 sentences)
'''

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content

# STREAMLIT UI
st.set_page_config(page_title="🧠 Creator Evaluation Tool", layout="wide")
st.title("🧠 Creator Evaluation Tool (Growth Gabby Fit)")
st.markdown("Evaluate a creator’s audience fit, tone, and values based on public content — without needing a media kit.")

creator_input = st.text_input("🔍 Enter a creator name, handle, or website:")

if st.button("Run Evaluation") and creator_input:
    with st.spinner("🔎 Searching for online presence..."):
        results = search_creator_online(creator_input)
        links, bios = extract_links_and_bios(results)
        full_bio_text = " ".join(bios[:5])  # limit to 5 search snippets

    st.markdown("## 🌐 Creator Overview")
    cols = st.columns(3)
    i = 0
    for platform, url in links.items():
        cols[i % 3].markdown(f"**{platform}:** [{url}]({url})")
        i += 1

    st.divider()

    with st.spinner("🤖 Running structured GPT evaluation..."):
        evaluation = evaluate_creator_with_gpt_structured(full_bio_text)

    st.markdown("## 📋 Evaluation Dashboard")
    st.markdown(evaluation)

    st.divider()
    st.caption("Created by Omar @ HubSpot | Powered by OpenAI + Serper.dev")
"""

with open("/mnt/data/app.py", "w") as f:
    f.write(structured_dashboard_code)

"Your app now uses a structured layout with detailed Brand Risk explanations and visual improvements!"
