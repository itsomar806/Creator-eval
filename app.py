# This will generate a visually enhanced Streamlit app layout with:
# - Risk level badge
# - HEART emoji checkmarks
# - Visual recommendation banners
# - Column layouts for cleaner spacing

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
You are an expert brand evaluator at HubSpot. Review the following content and return your evaluation as a dictionary with these fields:

creator_overview (str)
content_snapshot (str)
fit_score (str: Strong/Medium/Weak)
fit_reason (str)
brand_risk (str: Green/Yellow/Red)
risk_reason (str)
heart_values (dict: {{"Humble": "Yes/No - reason", ...}})
recommendation (str: Proceed/Conditional/Decline)
recommendation_reason (str)

Content:
\"\"\"
{bio_text}
\"\"\"
Only return the JSON object. No intro or extra explanation.
'''

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    import json
    return json.loads(response.choices[0].message.content)

# STREAMLIT UI
st.set_page_config(page_title="🧠 Creator Evaluation Tool", layout="wide")
st.title("🧠 Creator Evaluation Tool (Growth Gabby Fit)")
st.markdown("Evaluate a creator’s audience fit, tone, and values based on public content — no media kit required.")

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

    with st.spinner("🤖 Running GPT Evaluation..."):
        data = evaluate_creator_with_gpt_structured(full_bio_text)

    # 🧠 Evaluation Dashboard
    st.markdown("## 📋 Evaluation Dashboard")
    st.markdown(f"**🧠 Content Snapshot:** {data['content_snapshot']}")
    st.markdown(f"**🎯 Audience Fit (Growth Gabby):** {data['fit_score']} — {data['fit_reason']}")

    st.markdown("---")
    st.markdown(f"### 🧯 Brand Risk Level: {'🟢' if data['brand_risk']=='Green' else '🟡' if data['brand_risk']=='Yellow' else '🔴'} {data['brand_risk']}")
    st.markdown(data["risk_reason"])

    st.markdown("### ❤️ HEART Values")
    for k, v in data["heart_values"].items():
        icon = "✅" if "Yes" in v else "❌"
        st.markdown(f"- **{k}:** {icon} – {v}")

    st.divider()

    if "proceed" in data["recommendation"].lower():
        st.success(f"✅ Recommendation: Proceed\n\n{data['recommendation_reason']}")
    elif "conditional" in data["recommendation"].lower():
        st.warning(f"⚠️ Recommendation: Conditional\n\n{data['recommendation_reason']}")
    else:
        st.error(f"🛑 Recommendation: Decline\n\n{data['recommendation_reason']}")

    st.divider()
    st.caption("Created by Omar @ HubSpot | Powered by OpenAI + Serper.dev")
