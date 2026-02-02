import streamlit as st
import requests

# 1. SETUP
st.set_page_config(page_title="AI Insight Studio", layout="wide", page_icon="🧠")
API_URL = "http://127.0.0.1:8000"

# 2. CSS STYLES
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 1px solid #f0f0f0;
    }
    .entity-tag {
        display: inline-block; padding: 2px 8px; margin: 0 2px;
        border-radius: 6px; font-weight: 500; font-size: 0.9em;
    }
    .tag-ORG { background: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb; }
    .tag-PERSON { background: #f3e5f5; color: #7b1fa2; border: 1px solid #e1bee7; }
    .tag-GPE { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
    .tag-default { background: #fff3e0; color: #ef6c00; border: 1px solid #ffe0b2; }
    </style>
    """, unsafe_allow_html=True)

# 3. HELPER FUNCTION
def highlight_entities(text, entities):
    if not text or not entities: return text
    processed = text
    for ent in entities:
        word = ent['text']
        label = ent['label']
        cls = f"tag-{label}" if label in ["ORG", "PERSON", "GPE"] else "tag-default"
        html = f'<span class="entity-tag {cls}">{word} <small style="font-size:0.6em; opacity:0.7;">{label}</small></span>'
        processed = processed.replace(word, html)
    return processed

# 4. APP STRUCTURE
st.title("🧠 AI Insight Studio")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Input Source")
    input_type = st.radio("Mode:", ["Direct Text", "File Upload"])
    user_input = ""
    uploaded_file = None

    if input_type == "Direct Text":
        user_input = st.text_area("Enter text...", height=150)
    else:
        uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])

    analyze_btn = st.button("✨ Analyze Now", type="primary", use_container_width=True)

# --- TABS FOR MODES ---
tab1, tab2 = st.tabs(["📊 New Analysis", "💬 Chat with Data"])

# === TAB 1: ANALYSIS LOGIC ===
with tab1:
    if analyze_btn:
        if not user_input and not uploaded_file:
            st.warning("Please provide text or a file to analyze.")
        else:
            with st.spinner("🤖 Analyzing..."):
                try:
                    # Determine Endpoint
                    if uploaded_file:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(f"{API_URL}/analyze/file", files=files)
                    else:
                        response = requests.post(f"{API_URL}/analyze", json={"text": user_input})

                    if response.status_code == 200:
                        data = response.json()
                        st.toast("Analysis Complete!", icon="✅")

                        # Metrics
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            col = "#2ecc71" if data['sentiment'] == "positive" else "#e74c3c"
                            st.markdown(f'<div class="metric-card"><h4>Sentiment</h4><h2 style="color:{col}">{data["sentiment"].upper()}</h2></div>', unsafe_allow_html=True)
                        with c2:
                            st.markdown(f'<div class="metric-card"><h4>Score</h4><h2>{data["sentiment_score"]}</h2></div>', unsafe_allow_html=True)
                        with c3:
                            st.markdown(f'<div class="metric-card"><h4>Intent</h4><h3 style="color:#3498db">{data["intent"]}</h3></div>', unsafe_allow_html=True)
                        with c4:
                            st.markdown(f'<div class="metric-card"><h4>Entities</h4><h2>{len(data["entities"])}</h2></div>', unsafe_allow_html=True)

                        # PDF Download
                        with st.spinner("Generating PDF..."):
                            pdf = requests.post(f"{API_URL}/report/pdf", json=data)
                            if pdf.status_code == 200:
                                st.download_button("⬇️ Download PDF", data=pdf.content, file_name="report.pdf", mime="application/pdf")

                        st.divider()

                        # Visuals
                        t_vis, t_raw = st.tabs(["👁️ Visuals", "💾 JSON"])
                        with t_vis:
                            cl, cr = st.columns([2, 1])
                            with cl:
                                st.subheader("Contextual View")
                                disp_text = user_input if user_input else f"File Summary: {data['summary']}"
                                st.markdown(f'<div style="background:white; padding:20px; border-radius:10px; line-height:1.8;">{highlight_entities(disp_text, data["entities"])}</div>', unsafe_allow_html=True)
                            with cr:
                                st.subheader("Summary")
                                st.info(data['summary'])
                                st.subheader("Topics")
                                for t in data['topics']: st.markdown(f"**• {t.title()}**")
                        with t_raw:
                            st.json(data)
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")

                except Exception as e:
                    st.error(f"Connection Failed: {e}")

# === TAB 2: CHAT LOGIC ===
with tab2:
    st.header("💬 Ask your Knowledge Base")
    st.caption("Ask questions about any document you have ever analyzed.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question (e.g., 'What are the main complaints?')..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    res = requests.post(f"{API_URL}/memory/chat", json={"question": prompt})
                    if res.status_code == 200:
                        ans = res.json()["answer"]
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    else:
                        st.error("Backend Error")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")