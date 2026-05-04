import os
import cv2
import base64
import datetime
import numpy as np
from flask import Flask, render_template, request, url_for
from ultralytics import YOLO
from backward_chaining import BackwardChainingEngine

app = Flask(__name__)

# Konfigurasi Folder - Pastikan folder 'static/uploads' ada untuk menampilkan gambar di web
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 1. Load Model YOLOv11
print("="*70)
print("⏳ Memuat model YOLOv11...")
print("="*70)
try:
    model = YOLO('models/best.pt')  
    print(f"Model YOLO berhasil dimuat!")
    print(f"Total kelas: {len(model.names)}")
except Exception as e:
    print(f"GAGAL memuat model: {e}")
    model = None

# 2. Inisialisasi Sistem Pakar
print("\n" + "="*70)
print("Menginisialisasi Backward Chaining Engine...")
print("="*70)
engine = BackwardChainingEngine(db_path='resep_masakan.db')

print("\n" + "="*70)
print("SISTEM SIAP!")
print("="*70 + "\n")

def deteksi_bahan(gambar_path):
    """
    Melakukan deteksi objek, menghasilkan gambar visualisasi, 
    dan mengembalikan daftar bahan unik.
    """
    if model is None:
        return set(), None

    results = model.predict(
        source=gambar_path, 
        conf=0.15, 
        imgsz=800, 
        save=False, 
        max_det=30 
    )
    
    result = results[0] 
    bahan_terdeteksi = set()
    
    for box in result.boxes:
        class_id = int(box.cls[0])
        nama_bahan_raw = model.names[class_id]
        # Normalisasi: Bawang_Merah -> bawang merah
        nama_bersih = nama_bahan_raw.lower().replace("_", " ")
        bahan_terdeteksi.add(nama_bersih)
    img_visualisasi = result.plot()

    filename_hasil = "result_" + os.path.basename(gambar_path)
    path_hasil = os.path.join(app.config['UPLOAD_FOLDER'], filename_hasil)
    cv2.imwrite(path_hasil, img_visualisasi)

    return bahan_terdeteksi, filename_hasil

# ROUTES
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("\n" + "="*70)
        print("📤 PERMINTAAN BARU - Memproses Gambar...")
        print("="*70)
        
        file_gambar = request.files.get('file')
        camera_data = request.form.get('camera_data')
        path_simpan = ""

        # Handle Upload File
        if file_gambar and file_gambar.filename != '':
            filename = f"upload_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_gambar.filename}"
            path_simpan = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_gambar.save(path_simpan)
        
        # Handle Data Kamera (Base64)
        elif camera_data:
            try:
                header, encoded = camera_data.split(",", 1)
                data = base64.b64decode(encoded)
                filename = f"cam_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                path_simpan = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(path_simpan, "wb") as f:
                    f.write(data)
            except Exception as e:
                print(f"❌ Gagal memproses data kamera: {e}")

        if path_simpan:
            # Tahap 1: Deteksi Objek (YOLO)
            bahan_terdeteksi, file_visualisasi = deteksi_bahan(path_simpan)
            
            # Tahap 2: Rekomendasi Resep (Sistem Pakar Backward Chaining)
            print(f"🔍 Mencari resep berdasarkan bahan: {bahan_terdeteksi}")
            rekomendasi = engine.recommend(list(bahan_terdeteksi))
            
            # Kirim data ke result.html
            return render_template(
                'result.html', 
                bahan=list(bahan_terdeteksi), 
                resep_list=rekomendasi,
                gambar_asli=os.path.basename(path_simpan),
                gambar_deteksi=file_visualisasi
            )

    return render_template('index.html')

@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'model_loaded': model is not None,
        'engine_ready': engine is not None
    }

if __name__ == '__main__':
    # Gunakan host 0.0.0.0 agar bisa diakses di jaringan yang sama (untuk demo pakai HP)
    app.run(debug=True, host='0.0.0.0', port=5000)