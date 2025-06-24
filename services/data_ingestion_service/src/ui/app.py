import streamlit as st
import requests
import pandas as pd


FASTAPI_URL = "http://localhost:8003"  # change if deployed elsewhere

st.set_page_config(page_title="Genie Mentor: Data Ingestion Portal", layout="centered")

st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        color: #3f51b5;
    }
    .section-title {
        font-size: 1.5rem;
        margin-top: 2rem;
        color: #1a237e;
        font-weight: 600;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #90caf9;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📁 Genie Mentor - RAG Ingestion Dashboard</div>', unsafe_allow_html=True)

# --------- File Upload Section ---------
st.markdown('<div class="section-title">📤 Upload File to Google Drive</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a PDF or PPTX file", type=["pdf", "pptx"])
if uploaded_file and st.button("Upload to Drive 🚀"):
    with st.spinner("Uploading..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        try:
            response = requests.post(f"{FASTAPI_URL}/api/upload-file", files=files)
            if response.status_code == 200:
                res = response.json()
                if res.get("file_exists"):
                    st.warning(f"{res['message']}")
                else:
                    st.success(f"✅ Uploaded: {res['file_name']}")
                    st.info(f"Google Drive ID: {res['file_id']}")
            else:
                st.error(f"❌ Upload failed: {response.text}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# --------- Ingestion Trigger Section ---------
st.markdown('<div class="section-title">🔄 Trigger Ingestion from Drive</div>', unsafe_allow_html=True)

force_reprocess = st.checkbox("Force reprocessing of files", value=False)
if st.button("Trigger Ingestion 🔁"):
    with st.spinner("Ingesting files..."):
        try:
            res = requests.post(
                f"{FASTAPI_URL}/api/trigger-ingestion",
                json={"force_reprocess": force_reprocess}
            )
            if res.status_code == 200:
                files_processed = res.json()
                if not files_processed:
                    st.info("📭 No new files were ingested.")
                else:
                    st.success("✅ Ingestion Completed.")
                    st.markdown("**Files Processed:**")
                    df = pd.DataFrame(files_processed)
                    df["status"] = df["status"].str.capitalize()
                    df["icon"] = df["status"].apply(lambda x: "✅" if x.lower() == "processed" else "⏭️")
                    df["display"] = df["icon"] + " " + df["filename"] + " — " + df["status"]
                    st.markdown("### 🗂️ Processed Files Summary")
                    st.write(df["display"].to_frame(name="Result"))
            else:
                st.error(f"❌ Ingestion failed: {res.text}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# --------- Health Check ---------
st.markdown('<div class="section-title">🔍 API Health</div>', unsafe_allow_html=True)
if st.button("Check API Health 💡"):
    try:
        res = requests.get(f"{FASTAPI_URL}/health")
        if res.status_code == 200:
            st.success("✅ API is up and running.")
            st.json(res.json())
        else:
            st.error("❌ API is unreachable.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
