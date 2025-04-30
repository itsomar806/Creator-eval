# Here's a polished version of the app with better UI, section dividers, emojis, and highlight formatting.

pretty_app_code = """
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

# Serper search
def search_creator_online(query):
    url = "https://google.serper.dev/search"
    data = {"q": query}
    res = requests.post(url, json=data, headers=headers)
    return res.json()

# Extract links and bios
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

# GPT eval
def evaluate_creator_with_gpt(bio_text):
    prompt = f\"\"\"
You are an expert in brand partnerships at HubSpot. A creator's bio and snippets of their content are provided below.

Your task is to evaluate them for a potential partnership based on these five categories:

1. **Creator Overview**: What do you know about them? What platforms are they on?
2. **Content Snapshot**: What topics do they cover, what's their tone, and what is their content style?
3. **Audience Fit: Growth Gabby Persona**:
   - Growth Gabby is a 35–55-year-old Founder, CRO, or RevOps leader.
   - She's focused on growth, automation, innovation, and customer experience.
   - Score fit as: Strong / Medium / Weak — and explain why.
4. **Brand Safety & HEART Values**:
   - HEART = Humble, Empathetic, Adaptable, Remarkable, Transparent.
   - Note any red flags or misalignments.
   - Assign a Brand Risk level (Red / Yellow / Green).
   - For each HEART value, mark Yes/No with a short reason.
5. **Final Recommendation**:
   - ✅ Proceed / ⚠️ Conditional / 🛑 Decline
   - Include a 2–3 sentence rationale.

Here’s the content to evaluate:
\"\"\"
{bio_text}
\"\"\"
\"\"\"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message["content"]

# STREAMLIT UI
st.set_page_config(page_title="🧠 Creator Evaluation Tool", layout="wide")
st.title("🧠 Creator Evaluation Tool (Growth Gabby Fit)")
st.markdown("Use this tool to evaluate if a creator is a strong fit for HubSpot partnerships — no media kit required.")

creator_input = st.text_input("🔍 Enter a creator name, handle, or website:")

if st.button("Run Evaluation") and creator_input:
    with st.spinner("🔎 Searching for online presence..."):
        results = search_creator_online(creator_input)
        links, bios = extract_links_and_bios(results)
        full_bio_text = " ".join(bios[:5])  # limit to first 5 snippets

    st.markdown("## 🌐 Creator Overview")
    for platform, url in links.items():
        st.markdown(f"- **{platform}:** [{url}]({url})")

    st.divider()

    with st.spinner("🤖 Evaluating creator fit and brand alignment..."):
        evaluation = evaluate_creator_with_gpt(full_bio_text)

    st.markdown("## 📋 Evaluation Dashboard")
    st.markdown(evaluation)

    st.divider()
    st.caption("Created by Omar @ HubSpot | Powered by OpenAI + Serper.dev")
"""

with open("/mnt/data/app.py", "w") as f:
    f.write(pretty_app_code)

"Your Streamlit app is now updated with a cleaner UI and full dashboard layout!"
