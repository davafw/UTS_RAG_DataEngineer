Jalankan indexing.py agar bisa membuat vector dan menyimpan data menggunakan chromadb
Perintah: python src/indexing.py

Sebelum menjalankan kode query.py perhatikan hal berikut
GEMINI_API_KEY = "masukkan API key" // sesuaikan API key dari GEMINI_API_KEY
query_user = "masukkan input user " // masukkan input dari user untuk melakukan query
hasil = tanya_gemini(query_user) // return hasil query dari gemini