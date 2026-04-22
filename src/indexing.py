# indexing.py
import os
import glob
import pandas as pd
import chromadb
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embeddings import get_embedding_functions

def baca_dokumen(file_path):
    """Fungsi cerdas untuk mendeteksi tipe file dan mengekstrak isinya"""
    ekstensi = os.path.splitext(file_path)[1].lower()
    
    # 1. Jika file PDF
    if ekstensi == '.pdf':
        print(f"📄 Membaca PDF: {os.path.basename(file_path)}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Potong-potong teks PDF
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return text_splitter.split_documents(documents)
    
    # 2. Jika file CSV
    elif ekstensi == '.csv':
        print(f"📊 Membaca CSV: {os.path.basename(file_path)}")
        # CSVLoader otomatis membaca per baris dan menyertakan nama kolom
        loader = CSVLoader(file_path, encoding='utf-8')
        return loader.load()
    
    # 3. Jika file Excel
    elif ekstensi in ['.xls', '.xlsx']:
        print(f"📗 Membaca Excel: {os.path.basename(file_path)}")
        # Kita gunakan Pandas untuk membaca Excel secara bersih
        df = pd.read_excel(file_path).fillna("") # fillna("") agar sel kosong tidak error
        
        docs = []
        # Mengubah setiap baris Excel menjadi satu dokumen naratif
        for index, row in df.iterrows():
            # Menggabungkan Nama Kolom : Nilai Baris (contoh -> Harga: 5000 | Stok: 10)
            konten = " | ".join([f"{col}: {val}" for col, val in row.items() if str(val).strip() != ""])
            
            # Buat format dokumen Langchain
            doc = Document(
                page_content=konten,
                metadata={"source": file_path, "baris_excel": index + 1}
            )
            docs.append(doc)
        return docs
    
    else:
        print(f"⚠️ Format {ekstensi} diabaikan: {os.path.basename(file_path)}")
        return []

def run_multi_indexing(folder_data, collection_name="sustainable_transport"):
    # 1. Inisialisasi Database
    chroma_client = chromadb.PersistentClient(path="./my_vector_db")
    ef = get_embedding_functions()
    collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=ef)

    # 2. Cari semua file di dalam folder
    # Simbol /* berarti mengambil semua file dengan segala ekstensi
    semua_file = glob.glob(os.path.join(folder_data, "*"))
    
    if not semua_file:
        print(f"Error: Folder {folder_data} kosong atau tidak ditemukan!")
        return

    # 3. Proses setiap file satu per satu
    for file_path in semua_file:
        # Panggil fungsi pintar kita
        chunks = baca_dokumen(file_path)
        
        if not chunks:
            continue # Lewati jika file tidak valid atau kosong

        # 4. Simpan ke Database (Metode Batching agar super cepat)
        print(f"Memasukkan {len(chunks)} data dari {os.path.basename(file_path)} ke ChromaDB...")
        
        all_documents = []
        all_ids = []
        all_metadatas = []

        for i, chunk in enumerate(chunks):
            all_documents.append(chunk.page_content)
            # Membuat ID unik gabungan nama file + nomor urut
            unik_id = f"{os.path.basename(file_path)}_chunk_{i}"
            all_ids.append(unik_id)
            all_metadatas.append(chunk.metadata)

        batch_size = 100
        for i in range(0, len(all_documents), batch_size):
            collection.add(
                documents=all_documents[i : i + batch_size],
                ids=all_ids[i : i + batch_size],
                metadatas=all_metadatas[i : i + batch_size]
            )
    
    print("\n✅ Indexing Multi-Dokumen Selesai! Anda siap bertanya ke semua dokumen.")

if __name__ == "__main__":
    # Ganti dengan folder tempat Anda menyimpan SEMUA file (PDF, CSV, Excel)
    folder_path = r"./data"
    
    run_multi_indexing(folder_path)