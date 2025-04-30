import streamlit as st
import requests
import openai

st.set_page_config(page_title="🧠 Creator Evaluation Tool", layout="wide")
st.title("🧠 Creator Evaluation Tool (Growth Gabby Fit)")

# Load API keys from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

# Search headers
headers = {
    "X-API-KEY": SERPER_API_KEY,
    "Content-Type": "application/json"
}

# Helper: Run search using Serper.dev
def search_creator_online(query):
    url = "https://google.serper.dev/search"
    data = {"q": query}
    res = requests.post(url, json=data, headers=headers)
    return res.json()

# Helper: Extract social links
def extract_social_links_from_results(results):
    social_links = {
        "YouTube": None,
        "Instagram": None,
        "TikTok": None,
        "LinkedIn": None,
        "Twitter": None,
        "Website": None
    }

    for result in results.get("organic", []):
        link = result.get("link", "").lower()
        if "youtube.com" in link and not social_links["YouTube"]:
            social_links["YouTube"] = result["link"]
        elif "instagram.com" in link and not social_links["Instagram"]:
            social_links["Instagram"] = result["link"]
        elif "tiktok.com" in link and not social_links["TikTok"]:
            social_links["TikTok"] = result["link"]
        elif "linkedin.com" in link and not social_links["LinkedIn"]:
            social_links["LinkedIn"] = result["link"]
        elif "twitter.com" in link and not social_links["Twitter"]:
            social_links["Twitter"] = result["link"]
        elif not social_links["Website"]:
            social_links["Website"] = result["link"]

    return social_links

# MAIN APP
creator_input = st.text_input("Enter a creator name, handle, or website:")

if st.button("Evaluate") and creator_input:
    with st.spinner("🔎 Searching for creator presence..."):
        results = search_creator_online(creator_input)
        links = extract_social_links_from_results(results)

    st.subheader("🌐 Online Presence")
    for platform, url in links.items():
        if url:
            st.markdown(f"**{platform}:** [{url}]({url})")

    st.info("✅ Next step will involve analyzing content and assessing Growth Gabby alignment... Coming soon!")

    st.markdown("---")
    st.caption("Powered by OpenAI + Serper.dev")
