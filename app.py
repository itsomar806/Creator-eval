import streamlit as st
import requests
import openai
import json
import re

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

def estimate_followers(bio_snippets):
    text = " ".join(bio_snippets)
    matches = re.findall(r"(\\d+[\\.,]?\\d*[KM]?)\\s*(followers|subscribers|fans|audience)", text, re.IGNORECASE)
    total = 0
    for num, _ in matches:
        num = num.replace(",", "")
        if "K" in num:
            cleaned = float(num.replace("K", "")) * 1_000
        elif "M" in num:
            cleaned = float(num.replace("M", "")) * 1_000_000
        else:
            cleaned = float(num)
        total += int(cleaned)
    return int(total) if total > 0 else None

def evaluate_creator_with_gpt_structured(bio_text):
    prompt = f"""
You are an expert brand evaluator at HubSpot. Review the following content and return your evaluation as a dictionary with these fields:

creator_overview (str)
content_snapshot (str)
fit_score (str: Strong/Medium/Weak)
fit_reason (str)
brand_risk (str: Green/Yellow/Red)
risk_reason (str)
heart_values (dict: {{'Humble': 'Yes/No - reason', ...}})
recommendation (str: Proceed/Conditional/Decline)
recommendation_reason (str)

Content:
\"\"\"{bio_text}\"\"\"

Only return the JSON object. No intro or extra explanation.
"""
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
        follower_estimate = estimate_followers(bios)

    with st.spinner("🤖 Running GPT Evaluation..."):
        data = evaluate_creator_with_gpt_structured(full_bio_text)

    st.markdown("<h2 style='text-align: center;'>🌐 Creator Overview</h2>", unsafe_allow_html=True)
    if follower_estimate:
        st.markdown(f"<h4 style='text-align: center; color: gray;'>Estimated Total Following: {follower_estimate:,}</h4>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        st.markdown(
        "<div style='background-color:#FAFAFA; padding: 1.2rem; border-radius: 10px;'>", unsafe_allow_html=True,
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
        for platform, url in links.items():
            icon = platform_icons.get(platform, "🔗")
            st.markdown(f"{icon} [{platform}]({url})")
        "</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div style='background-color:#F3E8FF; padding: 1.2rem; border-radius: 10px;'>", unsafe_allow_html=True)
        st.markdown("<h4>🧠 Content Snapshot</h4>", unsafe_allow_html=True)
        st.markdown(f"<p>{data['content_snapshot']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
    <div style='background-color:#FFEFD6; padding: 1.2rem; border-radius: 10px;'>
        <h4>🎯 Audience Fit</h4>
        <p><strong>{data["fit_score"]}</strong> — {data["fit_reason"]}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    color_map = {"Green": "#D4EDDA", "Yellow": "#FFF3CD", "Red": "#F8D7DA"}
    risk_color = color_map.get(data["brand_risk"], "#FFFFFF")
    st.markdown(f"""
    <div style="background-color:{risk_color}; padding: 1rem; border-radius: 10px; text-align: center;">
        <h4>🧯 Brand Risk Level: {data['brand_risk']}</h4>
        <p>{data['risk_reason']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ❤️ HEART Values")
    heart_html = "<div style='padding: 1.2rem; background-color:#E6F2FF; border-radius: 10px;'>"
    for k, v in data["heart_values"].items():
        icon = "✅" if "Yes" in v else "❌"
        heart_html += f"<p style='margin: 0.5rem 0;'><strong>{k}:</strong> {icon} — {v}</p>"
    heart_html += "</div>"
    st.markdown(heart_html, unsafe_allow_html=True)

    st.divider()

    if "proceed" in data["recommendation"].lower():
        st.success(f"✅ Recommendation: Proceed\n\n{data['recommendation_reason']}")
    elif "conditional" in data["recommendation"].lower():
        st.warning(f"⚠️ Recommendation: Conditional\n\n{data['recommendation_reason']}")
    else:
        st.error(f"🛑 Recommendation: Decline\n\n{data['recommendation_reason']}")

    st.divider()
    st.caption("Created by Omar @ HubSpot | Powered by OpenAI + Serper.dev")
