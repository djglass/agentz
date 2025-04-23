import os
import shutil
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import TextLoader
from pathlib import Path
import re

INDEX_DIR = "agentz_state/rag_index"
BACKUP_DIR = "agentz_state/rag_index_archive"
DOCS_DIR = "agentz/data"
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
all_docs = []

# Archive old index
if os.path.exists(INDEX_DIR):
    print("📦 Archiving existing index...")
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    shutil.move(INDEX_DIR, BACKUP_DIR)

def infer_policy_type(filename):
    return filename.replace("_Policy.txt", "").replace("_", " ")

def parse_firewall_config(path):
    docs = []
    with open(path, "r") as f:
        raw = f.read()
    rules = re.findall(r'rule "(.*?)" \{(.*?)\}', raw, re.DOTALL)
    for name, body in rules:
        meta = {"rule_name": name}
        meta.update(dict(re.findall(r'(from|to|application|action)\s+\[?"?([^\"]+)', body)))
        content = f"Firewall Rule: {name}\n" + body.strip()
        docs.append(Document(page_content=content, metadata=meta))
    return docs

# Ingest all files
for file_path in Path(DOCS_DIR).rglob("*"):
    if file_path.name == "systems.csv":
        print(f"💻 Ingesting systems: {file_path.name}")
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            if pd.isna(row.get("Asset Tag")):
                print(f"⚠️ Skipping row with missing Asset Tag: {row}")
                continue
            doc_text = "\n".join([f"{k}: {v}" for k, v in row.items()])
            meta = {
                "source": str(file_path),
                "system_id": row["Asset Tag"]
            }
            all_docs.append(Document(page_content=doc_text, metadata=meta))

    elif file_path.name == "end_user_devices.csv":
        print(f"📱 Ingesting end-user devices: {file_path.name}")
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            system_id = row.get("Asset Tag")
            if pd.isna(system_id):
                print(f"⚠️ Skipping device with no Asset Tag: {row.get('Hostname', 'unknown')}")
                continue
        doc_text = "\n".join([f"{k}: {v}" for k, v in row.items()])
        meta = {
            "source": str(file_path),
            "system_id": system_id,
            "device_type": row.get("Device Type", "").lower()
        }
        all_docs.append(Document(page_content=doc_text, metadata=meta))


    elif file_path.name == "network_infra.csv":
        print(f"🌐 Ingesting network infra: {file_path.name}")
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            if pd.isna(row.get("Asset Tag")):
                print(f"⚠️ Skipping network device with no Asset Tag: {row.get('Hostname', 'unknown')}")
                continue
            doc_text = "\n".join([f"{k}: {v}" for k, v in row.items()])
            meta = {
                "source": str(file_path),
                "system_id": row["Asset Tag"],
                "device_type": row.get("Device Type", "").lower()
            }
            all_docs.append(Document(page_content=doc_text, metadata=meta))

    elif file_path.suffix == ".txt":
        if "firewall" in file_path.name.lower():
            print(f"🧱 Parsing firewall rules: {file_path.name}")
            all_docs.extend(parse_firewall_config(file_path))
        else:
            print(f"📄 Loading policy: {file_path.name}")
            loader = TextLoader(str(file_path))
            docs = loader.load()
            for doc in docs:
                doc.metadata["policy_type"] = infer_policy_type(file_path.stem)
            all_docs.extend(docs)

# Split and index
print("✂️ Splitting and embedding documents...")
short_docs = [doc for doc in all_docs if len(doc.page_content) < splitter._chunk_size]
long_docs = [doc for doc in all_docs if len(doc.page_content) >= splitter._chunk_size]
split_long = splitter.split_documents(long_docs)
split_docs = split_long + short_docs

print(f"📊 Total docs: {len(all_docs)}, split into {len(split_docs)} chunks.")
vectorstore = FAISS.from_documents(split_docs, embedding)
vectorstore.save_local(INDEX_DIR)
print(f"✅ Vectorstore saved to {INDEX_DIR}")
