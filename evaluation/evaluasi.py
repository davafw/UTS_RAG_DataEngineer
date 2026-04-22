"""
=============================================================
EVALUATION FRAMEWORK - EcoMobility Assistant
=============================================================

Script untuk evaluasi performa sistem RAG dengan 10 pertanyaan test
Hasil evaluasi disimpan dalam format yang bisa diexport ke Excel/CSV

Jalankan dengan: python evaluation/evaluasi.py
=============================================================
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

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

    def export_results(self, output_path="evaluation/hasil_evaluasi.json"):
        """Export hasil evaluasi ke JSON"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        export_data = {
            "metadata": {
                "system_name": "EcoMobility Assistant",
                "domain": "Sustainable Transportation",
                "evaluation_date": datetime.now().isoformat(),
                "total_questions": len(self.results),
                "avg_score": sum([r.get("skor_relevansi", 0) for r in self.results if r.get("skor_relevansi")]) / max(1, len([r for r in self.results if r.get("skor_relevansi")])),
            },
            "results": self.results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Hasil evaluasi disimpan ke: {output_path}")


# Test questions yang direkomendasikan untuk Sustainable Transportation
TEST_QUESTIONS = [
    (
        "Apa yang dimaksud dengan transportasi berkelanjutan?",
        "Transportasi berkelanjutan adalah sistem transportasi yang dapat memenuhi kebutuhan mobilitas saat ini tanpa mengorbankan kemampuan generasi mendatang, dengan fokus pada efisiensi energi dan minimalisasi dampak lingkungan."
    ),
    (
        "Bagaimana cara mengurangi emisi karbon dari sektor transportasi?",
        "Dapat dilakukan melalui: transisi ke kendaraan listrik, penggunaan bahan bakar alternatif, peningkatan transportasi publik, optimasi rute perjalanan, dan promosi moda transportasi aktif seperti bersepeda."
    ),
    (
        "Apa itu kendaraan listrik (EV) dan apa keuntungannya dibanding kendaraan konvensional?",
        "EV adalah kendaraan yang menggunakan motor listrik sebagai penggeraknya. Keuntungan: emisi nol saat digunakan, biaya operasional lebih rendah, suara lebih senyap, dan performa torsi yang lebih baik."
    ),
    (
        "Peran apa yang dimainkan transportasi publik dalam mencapai mobilitas berkelanjutan?",
        "Transportasi publik mengurangi jumlah kendaraan pribadi, menurunkan emisi per penumpang, menghemat energi, mengurangi kemacetan, dan meningkatkan aksesibilitas untuk semua segmen masyarakat."
    ),
    (
        "Tantangan utama apa dalam transisi ke transportasi berkelanjutan di Indonesia?",
        "Tantangan mencakup: infrastruktur charging terbatas, biaya investasi awal tinggi, kesadaran masyarakat masih rendah, terbatasnya pilihan kendaraan ramah lingkungan, dan kurangnya dukungan kebijakan yang konsisten."
    ),
    (
        "Bagaimana teknologi membantu dalam pengembangan transportasi berkelanjutan?",
        "Teknologi mendukung melalui: IoT untuk optimasi traffic, AI untuk prediksi demand, smart grid untuk charging, autonomous vehicles untuk efisiensi, dan platform sharing economy untuk utilisasi kendaraan maksimal."
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
        "Apa peluang bisnis dalam ekonomi transportasi berkelanjutan?",
        "Peluang: produksi EV dan komponen, infrastruktur charging, battery technology, layanan mobility-as-a-service (MaaS), financing solutions, dan smart traffic management systems."
    ),
]


if __name__ == "__main__":
    evaluator = RAGEvaluator()

    # Run evaluation
    evaluator.run_evaluation(TEST_QUESTIONS)

    # Export results
    evaluator.export_results()

    print("\n✅ Evaluasi selesai!")
