import sqlite3
import re
from typing import List, Dict, Set

class BackwardChainingEngine:
    def __init__(self, db_path='resep_masakan.db'):
        self.db_path = db_path
        self.min_match = 1  
        self.max_results = 10  
        
        print(f"✅ Backward Chaining Engine initialized")
        print(f"   Database: {db_path}")
        print(f"   Min match: {self.min_match} bahan")
        print(f"   Max results: {self.max_results} resep")
    
    def _connect_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _normalize(self, text: str) -> str:
        if not text: return ""
        return text.strip().lower().replace('_', ' ')
    
    def _parse_bahan(self, bahan_string: str) -> Set[str]:
        if not bahan_string:
            return set()
        bahan_list = re.split(r'[;,\n\r|]+', bahan_string)
        
        return set([self._normalize(b) for b in bahan_list if b.strip()])
    
    def recommend(self, detected_ingredients: List[str]) -> List[Dict]:
        
        print("\n" + "="*70)
        print("🔍 BACKWARD CHAINING - RECIPE RECOMMENDATION")
        print("="*70)
        
        #Normalize input (Evidence)
        detected_set = set([self._normalize(ing) for ing in detected_ingredients])
        
        print(f"Bahan terdeteksi: {detected_set}")
        
        if len(detected_set) == 0:
            print("Tidak ada bahan terdeteksi!")
            return []
        
        #Get kategori prioritas
        conn = self._connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT kategori FROM resep WHERE kategori IS NOT NULL")
        kategori_db = cursor.fetchall()
        list_kategori = set([self._normalize(k['kategori']) for k in kategori_db if k['kategori']])

        kategori_prioritas = detected_set.intersection(list_kategori)
        
        #Query semua resep
        cursor.execute("SELECT * FROM resep")
        all_recipes = cursor.fetchall()
        
        #Backward Chaining Loop
        kandidat = []
        
        for resep in all_recipes:
            bahan_db_raw = resep['bahan_pokok'] if resep['bahan_pokok'] else ""
            bahan_db_set = self._parse_bahan(bahan_db_raw)
            
            if not bahan_db_set:
                continue
        
            bahan_cocok = []
            for d_ing in detected_set:
                for b_db in bahan_db_set:
                    # Cek substring (Flexible)
                    if d_ing in b_db or b_db in d_ing:
                        bahan_cocok.append(b_db)
                        break
            bahan_cocok_set = set(bahan_cocok)
            match_count = len(bahan_cocok_set)
        
            # ATURAN BACKWARD CHAINING:
            if match_count >= self.min_match:
                persentase = int((match_count / len(bahan_db_set)) * 100)
                if persentase > 100: persentase = 100
                
                # Hitung skor (untuk ranking)
                kategori_resep = self._normalize(resep['kategori']) if resep['kategori'] else ""
                skor = match_count
                if kategori_resep in kategori_prioritas:
                    skor += 50  
                
                kandidat.append({
                    'nama': resep['nama_resep'],
                    'skor': skor,
                    'persentase': persentase,
                    'bahan_lengkap': resep['bahan_lengkap'],
                    'langkah': resep['langkah_memasak'],
                    'bahan_cocok': sorted(list(bahan_cocok_set)), # Menggunakan bahan_cocok_set, bukan irisan
                    'kategori': resep['kategori'] if resep['kategori'] else "Umum",
                    'match_count': match_count,
                    'total_bahan': len(bahan_db_set)
                })
        
        conn.close()
        
        kandidat.sort(key=lambda x: (x['skor'], x['persentase']), reverse=True)
        top_recommendations = kandidat[:self.max_results]
        
        print(f"✅Ditemukan {len(kandidat)} resep yang cocok")
        return top_recommendations
    
if __name__ == "__main__":
    engine = BackwardChainingEngine(db_path='resep_masakan.db')
    test_bahan = ["Daging_Ayam", "Telur ", "\nBawang_Merah"] 
    results = engine.recommend(test_bahan)
    
    if results:
        print("\nTest Berhasil: Rekomendasi ditemukan.")
    else:
        print("\nTest Gagal: Tidak ada hasil.")