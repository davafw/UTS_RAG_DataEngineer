# utils.py
from google import genai
from google.genai import types

def get_gemini_response(prompt, api_key):
    # Inisialisasi Client
    client = genai.Client(api_key=api_key)
    
    try:
        # Coba model paling standar
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        
        # Jika Error 404 (Model Not Found)
        if "404" in error_msg:
            print("\n[INFO] Model standar tidak ditemukan. Mencari model yang tersedia...")
            try:
                # LIST semua model yang diizinkan oleh API Key Anda
                model_list = list(client.models.list())
                available_names = [m.name for m in model_list]
                
                if available_names:
                    # Ambil model pertama yang mengandung kata 'gemini'
                    target_model = next((n for n in available_names if "gemini" in n), available_names[0])
                    print(f"[FIX] Menggunakan model alternatif: {target_model}")
                    
                    # Coba panggil ulang dengan model yang ditemukan
                    res = client.models.generate_content(model=target_model, contents=prompt)
                    return res.text
            except:
                return "Error: Tidak dapat menemukan model apa pun di project ini."
        
        # Jika Error 429 (Quota)
        if "429" in error_msg:
            return "Error: Kuota habis atau sedang cooldown. Tunggu 1-2 menit."
            
        return f"Terjadi kesalahan: {error_msg}"