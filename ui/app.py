"""
=============================================================
ANTARMUKA STREAMLIT — EcoMobility Assistant
=============================================================

Jalankan dengan: streamlit run ui/app.py
=============================================================
"""

import sys
import os
from pathlib import Path

# Agar bisa import dari folder src/
sys.path.append(str(Path(__file__).parent.parent / "src"))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─── Konfigurasi Halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌿 EcoMobility Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2ecc71;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #95a5a6;
        font-size: 1rem;
    }
    .info-box {
        background-color: #ecf0f1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("<h1 class='main-title'>🌿 EcoMobility Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Sistem Tanya-Jawab tentang Transportasi Berkelanjutan</p>", unsafe_allow_html=True)
st.divider()

# ─── Sidebar: Info & Konfigurasi ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Konfigurasi")

    top_k = st.slider(
        "📊 Jumlah dokumen relevan (top-k)",
        min_value=1, max_value=10, value=3,
        help="Berapa banyak chunk yang diambil dari vector database untuk konteks"
    )

    show_context = st.checkbox("📚 Tampilkan konteks yang digunakan", value=True)
    show_prompt = st.checkbox("🔧 Tampilkan prompt ke LLM", value=False)

    st.divider()
    st.header("ℹ️ Info Sistem")

    st.markdown("""
    **📌 Kelompok:** Dava, Arizal, Alivia
    **🌍 Domain:** Transportasi Berkelanjutan & Mobilitas Ramah Lingkungan
    **🤖 LLM:** Google Gemini 2.5 Flash
    **💾 Vector DB:** ChromaDB
    **🧬 Embedding:** SentenceTransformer (multilingual-MiniLM)
    **📝 Stack:** From Scratch + LangChain Components
    """)

    st.divider()
    st.info("💡 **Tip:** Mulai dengan pertanyaan spesifik tentang transportasi berkelanjutan. Contoh:\n- Apa itu kendaraan listrik?\n- Bagaimana cara mengurangi emisi transportasi?\n- Apa manfaat transportasi publik?")


# ─── Load Vector Store (cached agar tidak reload setiap query) ───────────────
@st.cache_resource
def load_vs():
    """Load vector store sekali saja, di-cache untuk performa."""
    try:
        from query import load_vectorstore
        return load_vectorstore("sustainable_transport"), None
    except FileNotFoundError as e:
        return None, f"Vector database tidak ditemukan: {e}"
    except Exception as e:
        return None, f"Error saat load vector store: {e}"


# ─── Main Content ──────────────────────────────────────────────────────────────
vectorstore, error = load_vs()

if error:
    st.error(f"⚠️ {error}")
    st.info("""
    **Solusi:**
    1. Jalankan terlebih dahulu: `python src/indexing.py`
    2. Pastikan folder `data/` berisi dokumen (PDF, CSV, Excel)
    3. Restart aplikasi Streamlit
    """)
    st.stop()

st.success("✅ Vector database berhasil dimuat dan siap digunakan!")

# ─── Chat Interface ───────────────────────────────────────────────────────────
# Simpan riwayat chat di session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.write(msg["content"])
        if msg["role"] == "assistant" and show_context and "contexts" in msg:
            with st.expander("📚 Konteks yang digunakan"):
                for i, ctx in enumerate(msg["contexts"], 1):
                    score_pct = int(ctx['score'] * 100)
                    st.markdown(f"**[{i}] Relevansi: {score_pct}%** | `{ctx['source']}`")
                    st.text(ctx["content"][:300] + "...")
                    st.divider()

# Input pertanyaan baru
if question := st.chat_input("💬 Ketik pertanyaan Anda tentang transportasi berkelanjutan..."):

    # Tampilkan pertanyaan user
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.write(question)

    # Generate jawaban
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Mencari informasi relevan... 🤖 Menghasilkan jawaban..."):
            try:
                from query import answer_question
                result = answer_question(question, vectorstore, top_k=top_k)

                st.write(result["answer"])

                # Tampilkan konteks jika diaktifkan
                if show_context:
                    with st.expander("📚 Konteks yang digunakan"):
                        for i, ctx in enumerate(result["contexts"], 1):
                            score_pct = int(ctx['score'] * 100)
                            st.markdown(f"**[{i}] Relevansi: {score_pct}%** | `{ctx['source']}`")
                            st.text(ctx["content"][:300] + "...")
                            st.divider()

                # Tampilkan prompt jika diaktifkan
                if show_prompt:
                    with st.expander("🔧 Prompt yang dikirim ke LLM"):
                        st.code(result["prompt"], language="text")

                # Simpan ke riwayat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "contexts": result["contexts"]
                })

            except Exception as e:
                error_msg = f"❌ Error: {e}\n\nPastikan:\n1. GEMINI_API_KEY sudah di-set di file `.env`\n2. Koneksi internet stabil\n3. Kuota API key tidak habis"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ─── Tombol Reset Chat ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.divider()
st.caption("🌿 EcoMobility Assistant — Sistem RAG untuk Transportasi Berkelanjutan | UTS Data Engineering")

