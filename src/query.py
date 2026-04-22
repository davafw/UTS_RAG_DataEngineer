import os
import chromadb
from embeddings import get_embedding_functions
from utils import get_gemini_response
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "masukkan API key")

def load_vectorstore(collection_name="sustainable_transport"):
    """Load ChromaDB vectorstore yang sudah di-index"""
    try:
        chroma_client = chromadb.PersistentClient(path="./my_vector_db")
        ef = get_embedding_functions()
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=ef
        )
        return collection
    except Exception as e:
        raise FileNotFoundError(f"Vector DB tidak ditemukan: {e}")


def answer_question(pertanyaan, collection, top_k=3):
    """
    Pipeline query lengkap: retrieval + generation dengan Gemini

    Args:
        pertanyaan: Query dari user
        collection: ChromaDB collection
        top_k: Jumlah dokumen relevan yang diambil

    Returns:
        dict dengan keys: answer, contexts, prompt
    """
    try:
        # Step 1: Retrieval (cari dokumen relevan)
        print(f"🔍 Mencari dokumen relevan untuk: '{pertanyaan}'")
        results = collection.query(
            query_texts=[pertanyaan],
            n_results=top_k
        )

        # Siapkan konteks dari hasil retrieval
        retrieved_docs = results.get('documents', [[]])[0]
        retrieved_distances = results.get('distances', [[]])[0]
        retrieved_metadatas = results.get('metadatas', [[]])[0]

        if not retrieved_docs:
            return {
                "answer": "Maaf, tidak ada dokumen relevan yang ditemukan untuk pertanyaan Anda.",
                "contexts": [],
                "prompt": ""
            }

        # Gabungkan semua konteks menjadi satu string
        konteks_list = []
        for i, (doc, distance, metadata) in enumerate(zip(retrieved_docs, retrieved_distances, retrieved_metadatas)):
            konteks_list.append(doc)

        konteks = "\n\n---\n\n".join(konteks_list)

        # Step 2: Prompt Construction
        full_prompt = f"""Anda adalah asisten cerdas yang ahli dalam transportasi berkelanjutan dan mobilitas ramah lingkungan.
Gunakan KONTEKS di bawah ini untuk menjawab pertanyaan pengguna dengan akurat dan detail.

Jika jawaban tidak ada di dalam KONTEKS, katakan saja bahwa informasi tersebut tidak tersedia di dalam dokumen.
SELALU JAWAB DALAM BAHASA INDONESIA dan sertakan referensi dari sumber dokumen jika relevan.

KONTEKS:
{konteks}

PERTANYAAN:
{pertanyaan}

JAWABAN:"""

        # Step 3: Generation (kirim ke Gemini)
        print(f"🤖 Menghasilkan jawaban dengan Gemini...")
        jawaban = get_gemini_response(full_prompt, GEMINI_API_KEY)

        # Siapkan data konteks untuk ditampilkan
        contexts_display = []
        for i, (doc, distance, metadata) in enumerate(zip(retrieved_docs, retrieved_distances, retrieved_metadatas)):
            score = 1 - (distance / 2)  # Convert distance to similarity score (0-1)
            source = metadata.get('source', 'Unknown')
            contexts_display.append({
                'content': doc,
                'score': score,
                'source': source
            })

        return {
            "answer": jawaban,
            "contexts": contexts_display,
            "prompt": full_prompt
        }

    except Exception as e:
        return {
            "answer": f"Error dalam proses query: {str(e)}",
            "contexts": [],
            "prompt": ""
        }


def tanya_gemini(pertanyaan, collection_name="sustainable_transport"):
    """Legacy function untuk backward compatibility"""
    try:
        collection = load_vectorstore(collection_name)
        result = answer_question(pertanyaan, collection, top_k=5)
        return result["answer"]
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    """Testing CLI untuk query system"""
    try:
        collection = load_vectorstore()

        # Test dengan 3 pertanyaan sample
        test_queries = [
            "Apa definisi transportasi berkelanjutan?",
            "Bagaimana cara mengurangi emisi karbon dari transportasi?",
            "Apa itu kendaraan listrik dan manfaatnya?"
        ]

        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"❓ Pertanyaan: {query}")
            print(f"{'='*60}")

            result = answer_question(query, collection, top_k=3)

            print(f"\n✅ Jawaban:\n{result['answer']}")

            print(f"\n📚 Sumber Dokumen ({len(result['contexts'])} dokumen):")
            for i, ctx in enumerate(result['contexts'], 1):
                print(f"  [{i}] Score: {ctx['score']:.4f} | {ctx['source']}")

    except Exception as e:
        print(f"Error: {e}")
        print("Pastikan sudah menjalankan indexing.py terlebih dahulu!")

