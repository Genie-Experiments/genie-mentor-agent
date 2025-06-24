# Data Ingestion Service

This service ingests PDF and PPTX documents from a specified Google Drive folder, performs semantic chunking, embeds the content using a language model, and stores the embeddings in ChromaDB. It includes a Streamlit UI for monitoring file ingestion status.

---

## 🚀 Features

* ✅ Google Drive integration (via Service Account)
* ✅ Semantic chunking using LlamaIndex
* ✅ Embedding with `all-MiniLM-L6-v2`
* ✅ Storage in **ChromaDB**
* ✅ Tracking of already processed files
* ✅ Friendly **Streamlit UI** for upload monitoring

---

## 📂 Project Structure (key parts)

project-root/
│
├── main.py                               ← Entry point
├── requirements.txt
├── src/
│   ├── api/
│   │   └── routes.py                     ← FastAPI route definitions
│   │
│   ├── core/
│   │   └── config.py                     ← Env loading, settings
│   │
│   ├── schemas/
│   │   └── models.py                     ← Pydantic models (requests/responses)
│   │
│   ├── services/
│   │   └── drive_ingestion.py           ← Main ingestion logic
│   │
│   └── ui/
│       └── app.py                        ← Streamlit UI for monitoring
├── secrets/
│   └── promising-keep-416609-4d97f7c36ae1.json  ← 🔒 Service account (not committed)
└── ingestion_state/
    └── KB_processed_files_history.txt   ← Processed files tracker


---

## ⚙️ Environment Variables

Create a `.env` file in the root of your project and define the following:

```env
# Path to your Google Service Account JSON (not committed to repo)
GOOGLE_SERVICE_ACCOUNT_FILE="services/data_ingestion_service/secrets/promising-keep-416609-4d97f7c36ae1.json"

# Path to the tracker file that keeps track of processed files
KB_PROCESSED_FILES="services/data_ingestion_service/ingestion_state/KB_processed_files_history.txt"

# Google Drive folder ID from which files will be fetched
KB_DATA_STORAGE_DRIVE_ID=" " #secret
```

> ⚠️ Do **NOT** commit the `.json` service account file to source control.

---

## 🧠 Dependencies

Install required libraries:

```bash
pip install -r requirements.txt
```


## ▶️ Running the Ingestion

### 1. Run from CLI

```bash
uvicorn services.data_ingestion_service.src.main:app --loop asyncio --reload
```

This will:

* Connect to the Google Drive folder
* Download `.pdf` and `.pptx` files
* Chunk and embed them
* Persist in Chroma
* Track what’s been processed

### 2. Run Streamlit UI 

```bash
streamlit run services/data_ingestion_service/ui/app.py
```

* See file upload status
* Preview processed file logs
* Trigger ingestion (optional interactive interface)

---

## 📎 Notes

* The ingestion process skips already processed files unless forced.
* Temporary files are auto-deleted after processing.
* Logs are printed via Python’s `logging` module.
* Chroma DB persists embeddings locally under the specified directory

---
