import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Setup path
sys.path.append(str(Path(__file__).parent.parent / "src"))
load_dotenv()

# ─── CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="EcoMobility Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── SESSION STATE ──────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Fungsi untuk membuat obrolan baru
def start_new_chat():
    if st.session_state.messages:
        # Gunakan pesan pertama user sebagai judul
        user_msg = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        title = user_msg[0][:25] + "..." if user_msg else "Percakapan Lama"
        
        # Simpan ke riwayat
        st.session_state.chat_history.append({
            "title": title,
            "messages": st.session_state.messages.copy()
        })
    # Reset pesan aktif
    st.session_state.messages = []

# ─── CSS (ADAPTIVE & MINIMALIST BUTTONS) ────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* --- SIDEBAR CUSTOMIZATION --- */
    [data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, 0.2); }

    .sidebar-title { text-align: center; margin-bottom: 2rem; }
    .sidebar-title .icon { font-size: 2.8rem; }
    .sidebar-title .main { font-size: 1.4rem; font-weight: 700; color: #4CAF50; }
    .sidebar-title .sub { font-size: 1rem; opacity: 0.7; }

    /* Sidebar Card Style (Info, Tentang, Tips) */
    .sidebar-card {
        background-color: rgba(128, 128, 128, 0.05);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    .card-title { font-weight: 600; font-size: 0.9rem; margin-bottom: 10px; color: #4CAF50; }

    /* --- ELEGANT BUTTON OVERRIDE --- */
    /* Membuat tombol terlihat seperti kartu minimalis */
    div.stButton > button {
        background-color: rgba(128, 128, 128, 0.05) !important;
        color: inherit !important;
        border: 1px solid rgba(128, 128, 128, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.7rem 1rem !important;
        width: 100% !important;
        text-align: left !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        margin-bottom: 10px;
    }

    div.stButton > button:hover {
        border-color: #4CAF50 !important;
        color: #4CAF50 !important;
        background-color: rgba(76, 175, 80, 0.05) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }

    /* --- MAIN UI --- */
    .status-badge {
        position: absolute; top: 20px; right: 20px;
        background: rgba(128, 128, 128, 0.1);
        padding: 5px 15px; border-radius: 20px; font-size: 0.8rem;
        display: flex; align-items: center; gap: 8px;
    }
    .dot { height: 8px; width: 8px; background-color: #4CAF50; border-radius: 50%; box-shadow: 0 0 5px #4CAF50; }

    .assistant-bubble {
        background-color: rgba(76, 175, 80, 0.1);
        border-radius: 20px; padding: 25px; margin: 20px 0;
        border: 1px solid rgba(76, 175, 80, 0.2);
        display: flex; gap: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────
with st.sidebar:
    # Judul Sidebar
    st.markdown("""
        <div class="sidebar-title">
            <div class="icon">🌿</div>
            <div class="main">EcoMobility</div>
            <div class="sub">Assistant</div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Navigasi Obrolan (Tampilan baru yang elegan)
    st.button("💬 Percakapan Baru", on_click=start_new_chat, use_container_width=True)
    
    # Dropdown atau list riwayat jika ada
    if st.session_state.chat_history:
        with st.expander("🕒 Riwayat Percakapan", expanded=False):
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                if st.button(f"📄 {chat['title']}", key=f"hist_{i}"):
                    st.session_state.messages = chat['messages']
                    st.rerun()

    st.divider()

    # 2. Info Aplikasi (Tetap seperti sebelumnya)
    st.markdown("""
        <div class="sidebar-card">
            <div class="card-title">ℹ️ Info Aplikasi</div>
            <p style='font-size:0.85rem; opacity:0.8;'>Sistem tanya-jawab transportasi berkelanjutan.</p>
        </div>
    """, unsafe_allow_html=True)

    # 3. Konfigurasi (Tetap seperti sebelumnya)
    st.markdown("### ⚙️ Konfigurasi")
    top_k = st.slider("Jumlah dokumen relevan", 1, 10, 3)
    show_context = st.toggle("Tampilkan konteks", True)
    show_prompt = st.toggle("Tampilkan prompt", False)

    # 4. Tentang Sistem (Tetap seperti sebelumnya)
    st.markdown("""
        <div class="sidebar-card">
            <div class="card-title">📖 Tentang Sistem</div>
            <ul style='font-size:0.82rem; padding-left:15px; opacity:0.8;'>
                <li>*📌 Kelompok:* Dava, Arizal, Alivia</li>
                <li>Transportasi Berkelanjutan</li>
                <li>Gemini 1.5 Flash</li>
                <li>ChromaDB</li>
                <li>SentenceTransformer (multilingual-MiniLM)</li>
                <li>From Scratch + LangChain Components</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # 5. Tips (Tetap seperti sebelumnya)
    st.markdown("""
        <div class="sidebar-card" style="background: rgba(76, 175, 80, 0.1);">
            <div class="card-title">💡 Tips</div>
            <p style='font-size:0.82rem; opacity:0.8;'>Gunakan pertanyaan spesifik untuk hasil terbaik.</p>
        </div>
    """, unsafe_allow_html=True)

# ─── MAIN UI ─────────────────────────────────────────

# Status Badge
st.markdown('<div class="status-badge"><span class="dot"></span> Sistem Online</div>', unsafe_allow_html=True)

# Header
st.markdown("""
    <div style="text-align: center; padding-top: 2rem;">
        <div style="color: #4CAF50; font-size: 2.8rem; font-weight: 700;">🌿 EcoMobility Assistant</div>
        <div style="opacity: 0.7; font-size: 1.1rem;">Sistem Tanya-Jawab Transportasi Berkelanjutan</div>
    </div>
""", unsafe_allow_html=True)

# ─── LOAD DATA & CHAT LOGIC ──────────────────────────
@st.cache_resource
def load_vs():
    try:
        from query import load_vectorstore
        return load_vectorstore("sustainable_transport"), None
    except Exception as e:
        return None, str(e)

vectorstore, error = load_vs()

# Tampilan Selamat Datang jika chat kosong
if not st.session_state.messages:
    st.markdown("""
        <div class="assistant-bubble">
            <div style="font-size: 24px; background: rgba(255,255,255,0.2); width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">🌿</div>
            <div>
                <strong>Halo! 👋</strong><br>
                Saya EcoMobility Assistant, siap membantu Anda.<br><br>
                Silakan ajukan pertanyaan Anda tentang mobilitas ramah lingkungan!
            </div>
        </div>
    """, unsafe_allow_html=True)

# Render pesan chat aktif
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🌿"):
        st.write(msg["content"])

# Chat Input
if question := st.chat_input("Tanyakan sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.write(question)

    with st.chat_message("assistant", avatar="🌿"):
        if error:
            st.error(error)
        else:
            with st.spinner("Mencari jawaban..."):
                try:
                    from query import answer_question
                    result = answer_question(question, vectorstore, top_k=top_k)
                    st.write(result["answer"])
                    
                    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
                    
                    if show_context:
                        with st.expander("📚 Konteks"):
                            for ctx in result.get("contexts", []):
                                st.caption(f"• {ctx['content'][:200]}...")
                except Exception as e:
                    st.error(f"Error: {e}")

# Footer
st.markdown("""
    <hr style="opacity: 0.1;">
    <center style="opacity: 0.5; font-size: 0.8rem; padding-bottom: 20px;">
        EcoMobility Assistant — RAG Transportasi Berkelanjutan
    </center>
""", unsafe_allow_html=True)