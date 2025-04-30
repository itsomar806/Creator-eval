import streamlit as st
import requests
import openai
import json

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
    prompt = f\You are an expert brand evaluator at HubSpot. Review the following content and return your evaluation as a dictionary with these fields:

creator_overview (str)
content_snapshot (str)
fit_score (str: Strong/Medium/Weak)
fit_reason (str)
brand_risk (str: Green/Yellow/Red)
risk_reason (str)
heart_values (dict: {"Humble": "Yes/No - reason", ...})
recommendation (str: Proceed/Conditional/Decline)
recommendation_reason (str)

Content:
\\\"\\\"\\\"{bio_text}\\\"\\\"\\\"
Only return the JSON object. No intro or extra explanation.\"""  # triple-double quotes with escaped block
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return json.loads(response.choices[0].message.content)

# STREAMLIT UI
st.set_page_config(page_title="🧠 Creator Evaluation Tool", layout="wide")
st.title("🧠 Creator Evaluation Tool (Growth Gabby Fit)")

creator_input = st.text_input("🔍 Enter a creator name, handle, or website:")

if st.button("Run Evaluation") and creator_input:
    with st.spinner("🔎 Searching for online presence..."):
        results = search_creator_online(creator_input)
        links, bios = extract_links_and_bios(results)
        full_bio_text = " ".join(bios[:5])

    st.markdown("## 🌐 Creator Overview")
    platform_icons = {
        "YouTube": "📺",
        "LinkedIn": "🔗",
        "Instagram": "📸",
        "TikTok": "🎵",
        "Twitter": "🐦",
        "Substack": "✉️",
        "Podcast": "🎙️",
        "Medium": "📝",
        "Website": "🌐"
    }
    cols = st.columns(3)
    i = 0
    for platform, url in links.items():
        icon = platform_icons.get(platform, "🔗")
        cols[i % 3].markdown(f"{icon} [{platform}]({url})")
        i += 1

    st.divider()

    with st.spinner("🤖 Running GPT Evaluation..."):
        data = evaluate_creator_with_gpt_structured(full_bio_text)

    st.markdown("<h2 style='text-align: center;'>📋 Evaluation Dashboard</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.markdown(f"### 🧠 Content Snapshot\\n{data['content_snapshot']}")
    col2.markdown(f"### 🎯 Audience Fit\\n**{data['fit_score']}** — {data['fit_reason']}")

    st.divider()

    color_map = {"Green": "#D4EDDA", "Yellow": "#FFF3CD", "Red": "#F8D7DA"}
    risk_color = color_map.get(data["brand_risk"], "#FFFFFF")
    risk_block = f'''
    <div style="background-color:{risk_color}; padding: 1rem; border-radius: 10px; text-align: center;">
        <h3>🧯 Brand Risk Level: {data['brand_risk']}</h3>
        <p>{data['risk_reason']}</p>
    </div>
    '''
    st.markdown(risk_block, unsafe_allow_html=True)

    st.markdown("### ❤️ HEART Values")
    st.markdown("<div style='padding: 1rem; background-color:#F0F8FF; border-left: 5px solid #007BFF;'>", unsafe_allow_html=True)
    for k, v in data["heart_values"].items():
        icon = "✅" if "Yes" in v else "❌"
        st.markdown(f"<p><strong>{k}:</strong> {icon} — {v}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    if "proceed" in data["recommendation"].lower():
        st.success(f"✅ Recommendation: Proceed\\n\\n{data['recommendation_reason']}")
    elif "conditional" in data["recommendation"].lower():
        st.warning(f"⚠️ Recommendation: Conditional\\n\\n{data['recommendation_reason']}")
    else:
        st.error(f"🛑 Recommendation: Decline\\n\\n{data['recommendation_reason']}")

    st.divider()
    st.caption("Created by Omar @ HubSpot | Powered by OpenAI + Serper.dev")
