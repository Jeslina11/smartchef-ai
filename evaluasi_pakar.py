import sqlite3
import pandas as pd
import re # Tambahkan import re
from backward_chaining import BackwardChainingEngine

def run_evaluation(n_samples=1050):
    engine = BackwardChainingEngine(db_path='resep_masakan.db')
    engine.max_results = 500
    conn = sqlite3.connect('resep_masakan.db')
    # Mengambil semua resep atau sebanyak n_samples
    query = f"SELECT nama_resep, bahan_pokok FROM resep ORDER BY id LIMIT {n_samples}"
    df_test = pd.read_sql_query(query, conn)
    conn.close()
    results = []
    
    print(f"\n🧪 Memulai Evaluasi Sistem Pakar pada {len(df_test)} sampel resep...")
    print("-" * 70)

    for index, row in df_test.iterrows():
        nama_asli = row['nama_resep']
        
        # --- PERBAIKAN DI SINI: Gunakan Regex agar sinkron dengan Engine ---
        raw_bahan = row['bahan_pokok'] if row['bahan_pokok'] else ""
        # Memotong berdasarkan koma, titik koma, baris baru, atau pipe
        bahan_fakta = [
            b.strip().lower().replace('_', ' ') 
            for b in re.split(r'[;,\n\r|]+', raw_bahan) 
            if b.strip()
        ]
        
        # Jalankan rekomendasi
        rekomendasi = engine.recommend(bahan_fakta)
        
        ditemukan = False
        posisi = -1
        persentase = 0
        
        for i, rek in enumerate(rekomendasi):
            # Cek kecocokan nama resep dengan pembersihan spasi
            if " ".join(rek['nama'].lower().split()) == " ".join(nama_asli.lower().split()):
                ditemukan = True
                posisi = i + 1 
                persentase = rek['persentase']
                break
        
        results.append({
            'nama_resep': nama_asli,
            'status': 'Berhasil' if ditemukan else 'Gagal',
            'peringkat': posisi if ditemukan else '-',
            'match_persen': persentase
        })

    df_results = pd.DataFrame(results)
    total_berhasil = len(df_results[df_results['status'] == 'Berhasil'])
    akurasi = (total_berhasil / len(df_results)) * 100
    avg_match = df_results[df_results['match_persen'] > 0]['match_persen'].mean()

    print("\n" + "="*70)
    print("📊 HASIL EVALUASI SISTEM PAKAR (FINAL)")
    print("="*70)
    print(f"Total Sampel Diuji    : {len(df_results)}")
    print(f"Total Berhasil        : {total_berhasil}")
    print(f"Total Gagal           : {len(df_results) - total_berhasil}")
    print(f"Akurasi Rekomendasi   : {akurasi:.2f}%")
    print(f"Rata-rata Match (%)   : {avg_match:.2f}%")
    print("="*70)
    
    df_results.to_csv('hasil_evaluasi_pakar.csv', index=False)
    print("✅ Hasil evaluasi detail disimpan di 'hasil_evaluasi_pakar.csv'")

if __name__ == "__main__":
    run_evaluation(n_samples=1050)