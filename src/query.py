import chromadb
from embeddings import get_embedding_functions
# from utils import get_llm_client
from utils import get_gemini_response


GEMINI_API_KEY = "masukkan API key"

def tanya_gemini(pertanyaan,collection_name="edukasi_rag"):
    # Hubungkan ke database yang sudah di index sebelumnya
    chroma_client = chromadb.PersistentClient(path="./my_vector_db")
    ef = get_embedding_functions()

    try:
        # gunakan get_collection
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=ef
        )
    except Exception as e:
        return "Error: Database tidak ditemukan. Pastikan anda sudah menjalankan indexing.py dengan sukses"
   
    # Proses retrival (Pencarian teks relevan)
    print(f"Mencari jawaban untuk: '{pertanyaan}'")
    results = collection.query(
        query_texts=[pertanyaan],
        n_results=15
    )
    konteks = "\n\n---\n\n".join(results['documents'][0])
    print(f"\n[INFO] Mencari jawaban untuk: {pertanyaan}")

    # print sebagian konteks untuk memastikan pencarian
    print("\n[DEBUG] Konteks yang dikirim ke LLM:")
    print(konteks[:200] + "...\n")

    # -proses generation (kirim ke gemini)
    # buat satu string prompt yang utuh
    full_prompt = f"""
    Anda adalah asisten cerdas. Gunakan KONTEKS di bawah ini untuk menjawab pertanyaan pengguna.
    Jika jawaban tidak ada di dalam KONTEKS, katakan saja bahwa informasi tersebut tidak tersedia di dokumen.
    JAWABLAH DALAM BAHASA INDONESIA

    KONTEKS:
    {konteks}

    PERTANYAAN:
    {pertanyaan}

    JAWABAN:
    """
    try:
        jawaban = get_gemini_response(str(full_prompt),GEMINI_API_KEY)
        return jawaban
    except Exception as e:
        return f"Terjadi kesalahan pada API Gemini: {str(e)}"


# Bagian untuk menjalankan testing
if __name__ == "__main__":
    # Ganti pertanyaan sesuai dengan isi dokumen
    query_user = "Apa isi utama dari laporan Global EV Outlook 2025? "

    hasil = tanya_gemini(query_user)

    print("================ JAWABAN  GEMINI ================")
    print(hasil)
    print("=========================================")


