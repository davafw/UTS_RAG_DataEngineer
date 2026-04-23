"""
EVALUATION FRAMEWORK - EcoMobility Assistant
Evaluasi performa sistem RAG dengan 10 pertanyaan test
Hasil evaluasi disimpan dalam format yang bisa diexport ke Excel/CSV

python evaluation/evaluasi.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import csv

# Setup path agar bisa import dari src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from query import load_vectorstore, answer_question


class RAGEvaluator:
    """Class untuk evaluasi sistem RAG dengan scoring framework"""

    def __init__(self, collection_name="sustainable_transport"):
        self.collection = load_vectorstore(collection_name)
        self.results = []

    def evaluate_single(self, question_num, question, ideal_answer=None, top_k=3):
        """
        Evaluasi satu pertanyaan

        Args:
            question_num: Nomor pertanyaan (1-10)
            question: Pertanyaan yang diajukan
            ideal_answer: Jawaban ideal/referensi (untuk perbandingan manual)
            top_k: Jumlah dokumen yang diambil

        Returns:
            dict dengan hasil evaluasi
        """
        print(f"\n{'='*70}")
        print(f"📋 PERTANYAAN {question_num}: {question}")
        print(f"{'='*70}")

        try:
            result = answer_question(question, self.collection, top_k=top_k)

            system_answer = result["answer"]
            contexts = result["contexts"]

            # Display hasil
            print(f"\n🤖 JAWABAN SISTEM:")
            print(system_answer)

            if contexts:
                print(f"\n📚 SUMBER DOKUMEN ({len(contexts)} dokumen):")
                for i, ctx in enumerate(contexts, 1):
                    print(f"  [{i}] Score: {ctx['score']:.4f} | {ctx['source']}")
                    print(f"      Preview: {ctx['content'][:150]}...")

            if ideal_answer:
                print(f"\n✅ JAWABAN IDEAL (referensi):")
                print(ideal_answer)

            # Minta manual scoring dari user
            print("\n" + "="*70)
            score = input("📊 Berikan skor relevansi (1-5, atau tekan Enter untuk skip): ").strip()

            if score:
                try:
                    score = int(score)
                    if 1 <= score <= 5:
                        score = score
                    else:
                        score = None
                except:
                    score = None

            notes = input("📝 Catatan/feedback (opsional, tekan Enter untuk skip): ").strip()

            evaluation_record = {
                "no": question_num,
                "pertanyaan": question,
                "jawaban_sistem": system_answer,
                "jawaban_ideal": ideal_answer or "-",
                "skor_relevansi": score,
                "jumlah_sumber": len(contexts),
                "sumber_dokumen": [ctx['source'] for ctx in contexts],
                "catatan": notes,
                "timestamp": datetime.now().isoformat()
            }

            self.results.append(evaluation_record)
            return evaluation_record

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return None

    def run_evaluation(self, test_questions):
        """
        Jalankan evaluasi untuk semua test questions

        Args:
            test_questions: List of tuples (question, ideal_answer)
        """
        print("\n" + "="*70)
        print("🚀 MEMULAI EVALUASI SISTEM RAG - EcoMobility Assistant")
        print(f"Total pertanyaan: {len(test_questions)}")
        print("="*70)

        for i, (question, ideal_answer) in enumerate(test_questions, 1):
            self.evaluate_single(i, question, ideal_answer, top_k=3)

        # Summary
        self.print_summary()

    def print_summary(self):
        """Tampilkan ringkasan hasil evaluasi"""
        print("\n" + "="*70)
        print("📊 RINGKASAN HASIL EVALUASI")
        print("="*70)

        scored_results = [r for r in self.results if r and r.get("skor_relevansi")]

        if not scored_results:
            print("⚠️ Belum ada pertanyaan yang di-score")
            return

        total_questions = len(self.results)
        scored_questions = len(scored_results)
        scores = [r["skor_relevansi"] for r in scored_results]
        avg_score = sum(scores) / len(scores) if scores else 0

        print(f"\nTotal pertanyaan diuji: {total_questions}")
        print(f"Pertanyaan dengan skor: {scored_questions}/{total_questions}")
        print(f"\n⭐ Rata-rata skor relevansi: {avg_score:.2f}/5.0")

        # Distribution
        score_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for score in scores:
            score_dist[score] += 1

        print("\n📈 Distribusi Skor:")
        for score, count in sorted(score_dist.items()):
            bar = "█" * count
            print(f"  {score}⭐ : {bar} ({count})")

    # Export hasil evaluasi ke JSON
    def export_json(self, output_path="evaluation/hasil_evaluasi.json"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        scored = [r["skor_relevansi"] for r in self.results if r.get("skor_relevansi")]
        avg_score = sum(scored) / len(scored) if scored else 0

        export_data = {
            "metadata": {
                "system_name": "EcoMobility Assistant",
                "evaluation_date": datetime.now().isoformat(),
                "total_questions": len(self.results),
                "avg_score": avg_score
            },
            "results": self.results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✅ JSON disimpan: {output_path}")
        # Export hasil evaluasi ke CSV
    def export_results(self, output_path="evaluation/hasil_evaluasi.csv"):
        """Export hasil evaluasi ke CSV + rata-rata skor"""

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Hitung rata-rata skor
        scored = [r["skor_relevansi"] for r in self.results if r.get("skor_relevansi")]
        avg_score = sum(scored) / len(scored) if scored else 0

        # Header CSV
        fieldnames = [
            "no",
            "pertanyaan",
            "jawaban_sistem",
            "jawaban_ideal",
            "skor_relevansi",
            "jumlah_sumber",
            "sumber_dokumen",
            "catatan",
            "timestamp"
        ]

        with open(output_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for r in self.results:
                if r:
                    # ubah list sumber jadi string
                    r["sumber_dokumen"] = ", ".join(r["sumber_dokumen"])
                    writer.writerow(r)

            # Tambah baris rata-rata di bawah
            writer.writerow({})
            writer.writerow({
                "pertanyaan": "RATA-RATA SKOR",
                "skor_relevansi": f"{avg_score:.2f}"
            })

        print(f"\n✅ Hasil evaluasi disimpan ke CSV: {output_path}")
        print(f"⭐ Rata-rata skor: {avg_score:.2f}")


# Test questions dan jawaban ideal untuk evaluasi
TEST_QUESTIONS = [
    (
        "Apa pengertian transportasi menurut UU Nomor 22 Tahun 2009?",
        "Perpindahan orang dan/atau barang dari satu tempat ke tempat lain dengan menggunakan kendaraan di ruang lalu lintas jalan."
    ),
    (
        "Apa penemuan pada tahun 3500 SM yang menjadi cikal bakal transportasi modern?",
        "Penemuan roda"
    ),
    (
        "Sebutkan tiga komponen utama yang saling terkait dalam transportasi berkelanjutan!",
        "Lingkungan, masyarakat, dan ekonomi."
    ),
    (
        "Apa kepanjangan dari istilah MKT atau TDM dalam manajemen transportasi?",
        "Manajemen Kebutuhan Transportasi atau Transport Demand Management"
    ),
    (
        "Tantangan utama apa dalam transisi ke transportasi berkelanjutan di Indonesia?",
        "Tantangan mencakup: infrastruktur charging terbatas, biaya investasi awal tinggi, kesadaran masyarakat masih rendah, terbatasnya pilihan kendaraan ramah lingkungan, dan kurangnya dukungan kebijakan yang konsisten."
    ),
    (
        "Berdasarkan data tahun 2025, provinsi mana di Indonesia yang memiliki jumlah total kendaraan bermotor paling banyak?",
        "Jawa Barat (dengan total lebih dari 28 juta unit)"
    ),
    (
        "Apa kontribusi sektor transportasi terhadap perubahan iklim global?",
        "Transportasi menyumbang sekitar 24% dari emisi CO2 global, dengan mayoritas berasal dari transportasi jalan. Ini menjadikan sektor transportasi sebagai target penting dalam upaya mitigasi perubahan iklim."
    ),
    (
        "Solusi transportasi apa yang cocok untuk daerah urban dengan kepadatan tinggi?",
        "Bus rapid transit (BRT), metro ringan (LRT), angkutan personal yang ramah lingkungan, bike-sharing, pedestrian-friendly infrastructure, dan integrated multimodal transportation system."
    ),
    (
        "Bagaimana polisi transportasi mempengaruhi adopsi kendaraan ramah lingkungan?",
        "Kebijakan seperti: insentif pajak untuk EV, larangan kendaraan berbahan bakar fosil tertentu, standar emisi ketat, investasi infrastruktur charging, dan subsidi untuk transportasi publik mendorong transisi hijau."
    ),
    (
        "Apa tujuan utama dari sistem transportasi berkelanjutan?",
        "Menciptakan sistem yang memenuhi kebutuhan mobilitas sekaligus meminimalkan dampak negatif terhadap lingkungan dan meningkatkan kualitas hidup masyarakat."
    ),
]


if __name__ == "__main__":
    evaluator = RAGEvaluator()

    # Run evaluation
    evaluator.run_evaluation(TEST_QUESTIONS)

    # Export results
    evaluator.export_json()
    evaluator.export_results()

    print("\n✅ Evaluasi selesai!")
