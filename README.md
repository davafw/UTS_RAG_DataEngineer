# 🌿 EcoMobility Assistant — RAG System untuk Transportasi Berkelanjutan

**Retrieval-Augmented Generation (RAG) untuk Sistem Tanya-Jawab Cerdas tentang Transportasi Berkelanjutan**

UTS Data Engineering — D4 Teknologi Rekayasa Perangkat Lunak

---

## 👥 Identitas Kelompok

| Nama | NIM | Peran |
|------|-----|-------|
| Dava | [NIM] | Project Lead & Backend |
| Arizal | [NIM] | Data Engineer |
| Alivia | [NIM] | Data Processing & QA |

**Topik Domain:** Transportasi Berkelanjutan & Mobilitas Ramah Lingkungan  
**Stack yang Dipilih:** From Scratch (LangChain Components)  
**LLM yang Digunakan:** Google Gemini 2.5 Flash  
**Vector DB yang Digunakan:** ChromaDB  

---

## 📋 Deskripsi Proyek

**EcoMobility Assistant** adalah sistem RAG yang mampu menjawab pertanyaan pengguna tentang transportasi berkelanjutan dan mobilitas ramah lingkungan berdasarkan dokumen lokal yang telah diindeks.

Sistem ini menggabungkan:
- 📄 **Document Ingestion** — Membaca PDF, CSV, dan Excel
- 🔤 **Text Processing** — Chunking dengan ukuran optimal
- 📊 **Vector Embedding** — Menggunakan sentence-transformers multilingual
- 🔍 **Semantic Search** — Similarity search di ChromaDB
- 🤖 **LLM Generation** — Jawaban kontekstual via Gemini API

---

## 🏗️ Arsitektur Sistem

### Pipeline Indexing (Offline)
```
Dokumen Sumber (PDF/CSV/Excel)
          ⬇
📖 Document Loader → Baca & parse dokumen
          ⬇
✂️ Text Splitter → Chunking (1000 chars, 100 overlap)
          ⬇
🧬 Embedding Model → SentenceTransformer multilingual
          ⬇
🔗 ChromaDB → Simpan embeddings + metadata
```

### Pipeline Query (Online)
```
❓ User Query
     ⬇
🧬 Query Embedding → Ubah pertanyaan ke vektor
     ⬇
🔍 Similarity Search → Cari top-3 dokumen relevan
     ⬇
📝 Prompt Construction → Gabungkan konteks + pertanyaan
     ⬇
🤖 LLM (Gemini) → Generate jawaban
     ⬇
✅ Jawaban + Sources → Kembalikan ke user
```

---

## 📂 Struktur Folder

```
rag-ecomobility-uts/
├── data/                           # Dokumen sumber
│   ├── GlobalEVOutlook2025.pdf
│   ├── WB_WDI_EN_GHG_CO2_*.csv
│   ├── Wawasan Transportasi *.pdf
│   └── EV Data Explorer 2025.xlsx
├── src/
│   ├── indexing.py                # 🔧 Pipeline indexing (document loader + chunking)
│   ├── query.py                   # 🔧 Pipeline query (retrieval + generation)
│   ├── embeddings.py              # 🔧 Konfigurasi embedding model
│   └── utils.py                   # Fungsi helper (Gemini API integration)
├── ui/
│   └── app.py                     # 🔧 Streamlit interface
├── evaluation/
│   ├── evaluasi.py                # 📊 Evaluation framework untuk 10 pertanyaan
│   └── hasil_evaluasi.json        # Hasil evaluasi (auto-generated)
├── my_vector_db/                  # ChromaDB persistent storage
├── .env.example                   # Template environment variables
├── .gitignore
├── requirements.txt               # Python dependencies
└── README.md                      # Dokumentasi ini
```

---

## 🚀 Quick Start

### 1️⃣ Setup & Dependencies

```bash
# Clone repository
git clone https://github.com/[username]/rag-ecomobility-uts.git
cd rag-ecomobility-uts

# Buat virtual environment
python -m venv venv

# Aktifkan venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Konfigurasi API Key

```bash
# Copy template .env
cp .env.example .env

# Edit .env dan isi GEMINI_API_KEY
# GEMINI_API_KEY=sk_live_xxxxxxxxxxxx
```

**Cara mendapat API key Gemini gratis:**
1. Kunjungi: https://aistudio.google.com/app/apikey
2. Klik "Create API Key"
3. Copy dan paste ke `.env`

### 3️⃣ Jalankan Indexing (Sekali Saja)

```bash
python src/indexing.py
```

Output:
```
📄 Membaca PDF: GlobalEVOutlook2025.pdf
📊 Membaca CSV: WB_WDI_EN_GHG_CO2_MT_CE_AR5.csv
📗 Membaca Excel: EV Data Explorer 2025.xlsx
Memasukkan 1234 data dari GlobalEVOutlook2025.pdf ke ChromaDB...
✅ Indexing Multi-Dokumen Selesai!
```

### 4️⃣ Jalankan Sistem RAG

#### Option A: Streamlit UI (Recommended)
```bash
streamlit run ui/app.py
```
Buka browser: `http://localhost:8501`

#### Option B: CLI Query
```bash
python src/query.py
```

---

## 📝 Penggunaan

### Contoh 1: Melalui Streamlit UI
1. Ketik pertanyaan di chat box
2. Sistem akan menampilkan:
   - ✅ Jawaban dari LLM
   - 📚 Konteks dokumen relevan (dengan skor similarity)
   - 🔗 Sumber dokumen

### Contoh 2: Melalui Python Script
```python
from src.query import load_vectorstore, answer_question

# Load vector store
collection = load_vectorstore()

# Ask question
result = answer_question(
    "Apa definisi transportasi berkelanjutan?",
    collection,
    top_k=3
)

print(result["answer"])
# Output: "Transportasi berkelanjutan adalah..."

# Lihat sumber
for ctx in result["contexts"]:
    print(f"Score: {ctx['score']:.4f} | {ctx['source']}")
```

---

## 🔧 Konfigurasi Parameter

Edit langsung di kode atau di `src/indexing.py`:

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `CHUNK_SIZE` | 1000 | Ukuran setiap chunk teks (karakter) |
| `CHUNK_OVERLAP` | 100 | Overlap antar chunk untuk kontinuitas konteks |
| `TOP_K` | 3 | Jumlah dokumen relevan yang diambil dari vector DB |
| `COLLECTION_NAME` | sustainable_transport | Nama collection di ChromaDB |
| `EMBEDDING_MODEL` | paraphrase-multilingual-MiniLM-L12-v2 | Model embedding multilingual |

---

## 📊 Evaluasi Sistem

### Jalankan Evaluasi 10 Pertanyaan

```bash
python evaluation/evaluasi.py
```

Script akan:
1. Mengajukan 10 pertanyaan test tentang transportasi berkelanjutan
2. Menampilkan jawaban sistem + sumber dokumen
3. Meminta scoring manual (1-5) dari Anda
4. Export hasil ke `evaluation/hasil_evaluasi.json`

### 10 Pertanyaan Evaluasi

1. Apa yang dimaksud dengan transportasi berkelanjutan?
2. Bagaimana cara mengurangi emisi karbon dari sektor transportasi?
3. Apa itu kendaraan listrik (EV) dan apa keuntungannya?
4. Peran apa yang dimainkan transportasi publik dalam mobilitas berkelanjutan?
5. Tantangan utama apa dalam transisi transportasi berkelanjutan di Indonesia?
6. Bagaimana teknologi membantu pengembangan transportasi berkelanjutan?
7. Apa kontribusi sektor transportasi terhadap perubahan iklim global?
8. Solusi transportasi apa untuk area urban dengan kepadatan tinggi?
9. Bagaimana kebijakan mempengaruhi adopsi kendaraan ramah lingkungan?
10. Apa peluang bisnis dalam ekonomi transportasi berkelanjutan?

---

## 📈 Hasil Evaluasi

*(Akan diupdate setelah menjalankan evaluation/evaluasi.py)*

| No | Pertanyaan | Skor (1-5) | Catatan |
|----|-----------|-----------|--------|
| 1 | Definisi transportasi berkelanjutan | - | *pending* |
| 2 | Cara mengurangi emisi karbon | - | *pending* |
| ... | ... | ... | ... |

**Rata-rata Skor:** *pending*  
**Analisis:** *pending*

---

## 🛠️ Troubleshooting

### Error: "Vector DB tidak ditemukan"
```
Solusi: Jalankan python src/indexing.py terlebih dahulu
```

### Error: "GEMINI_API_KEY not found"
```
Solusi: 
1. Buat file .env dari .env.example
2. Isi GEMINI_API_KEY dengan API key dari aistudio.google.com
3. Restart aplikasi
```

### Model Gemini tidak tersedia
```
Solusi:
Sistem akan otomatis mencari model alternatif dari list yang tersedia.
Pastikan API key memiliki akses ke minimal satu model Gemini.
```

### ChromaDB collection error
```
Solusi: 
Hapus folder my_vector_db/ dan jalankan indexing.py kembali
rm -rf my_vector_db/
python src/indexing.py
```

---

## 🎓 Konsep Data Engineering yang Diterapkan

| Komponen RAG | Konsep DE | Implementasi |
|-------------|----------|--------------|
| Document Loader | Data Ingestion | PyPDFLoader, CSVLoader |
| Text Splitter | Data Transformation | Chunking dengan overlap |
| Embedding | Feature Engineering | SentenceTransformer |
| Vector DB | Data Storage & Indexing | ChromaDB persistent |
| Retriever | Data Query | Similarity search (vector) |
| LLM | Data Presentation | Prompt engineering |

---

## 📚 Teknologi yang Digunakan

- **Language:** Python 3.8+
- **Framework RAG:** LangChain Community + Custom From Scratch
- **Embedding:** SentenceTransformers (multilingual-MiniLM)
- **Vector DB:** ChromaDB
- **LLM:** Google Gemini 2.5 Flash API
- **UI:** Streamlit
- **Data Processing:** Pandas, PyPDF2

---

## 📦 Dependencies

Lihat `requirements.txt` untuk versi lengkap:

```
langchain-community
langchain-core
langchain-text-splitters
chromadb
google-genai
streamlit
python-dotenv
pandas
openpyxl
```

Install dengan:
```bash
pip install -r requirements.txt
```

---

## ⚠️ Integritas Akademik

- ✅ Diizinkan: Menggunakan library open-source dan dokumentasi resmi
- ✅ Diizinkan: Diskusi konsep dengan tim lain (tanpa share kode)
- ✅ Diizinkan: Menggunakan AI assistant untuk pembelajaran
- ❌ DILARANG: Menyalin kode kelompok lain
- ❌ DILARANG: Push API key ke GitHub (gunakan `.env`)

---

## 🔗 Referensi

### Documentation
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Streamlit Docs](https://docs.streamlit.io/)

### Paper & Articles
- Global EV Outlook 2025 (IEA)
- Global Energy Review 2025 (IEA)
- World Bank Development Indicators

### Tutorial Referensi
- [Building RAG Apps - LangChain](https://python.langchain.com/docs/use_cases/question_answering/)
- [Embedding Models](https://www.sbert.net/)
- [ChromaDB + LangChain](https://www.trychroma.com/)

---

## 📞 Kontak & Support

Untuk pertanyaan atau issues:
- 📧 Email Dosen: [email dosen]
- 💬 Grup Kelas: [link grup]

---

## 📋 Lisensi & Catatan

Proyek ini adalah bagian dari UTS Data Engineering 2026.  
Diizinkan untuk keperluan akademik dan pembelajaran.

---

**Last Updated:** 2026-04-22  
**Status:** Backend Development in Progress
