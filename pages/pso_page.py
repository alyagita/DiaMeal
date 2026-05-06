from flask import Blueprint, render_template, redirect, url_for, session
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # naik 2 level dari file ini untuk dapat root project
sys.path.insert(0, os.path.join(BASE_DIR, 'modules')) # tambahkan folder modules ke path supaya bisa di-import

from nutrisi import hitung_kebutuhan # fungsi untuk hitung kebutuhan nutrisi harian user
from pso import rekomendasi_menu_pso # fungsi utama PSO untuk cari kombinasi menu terbaik

pso_bp = Blueprint('pso', __name__, url_prefix='/pso') # daftarkan blueprint dengan prefix URL /pso


# Konversi dict ke object dengan dot notation
# Diperlukan agar template HTML bisa akses data dengan h.menu_sarapan.nama_menu dll
def dict_to_object(d):
    class DictObject:
        def __init__(self, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    setattr(self, key, dict_to_object(value)) # kalau valuenya dict, rekursif konversi juga
                elif isinstance(value, list):
                    setattr(self, key, [
                        dict_to_object(item) if isinstance(item, dict) else item # kalau item dalam list adalah dict, konversi juga
                        for item in value
                    ])
                else:
                    setattr(self, key, value) # kalau bukan dict/list, langsung set sebagai atribut biasa

        def __getitem__(self, key):
            return getattr(self, key) # supaya object bisa diakses pakai bracket notation: obj['key']

        def get(self, key, default=None):
            return getattr(self, key, default) # supaya object punya method .get() seperti dict

        def items(self):
            return self.__dict__.items() # supaya object bisa di-loop seperti dict

        def keys(self):
            return self.__dict__.keys() # supaya object punya method .keys() seperti dict

    return DictObject(d)

def deserialize_hasil(serialized):
    return [dict_to_object(item) for item in serialized] # konversi tiap item hasil PSO dari dict ke object

# Jalankan PSO sekali per sesi
# Jika user sama dan hasil sudah ada, langsung redirect ke rekomendasi
@pso_bp.route("/generate")
def generate_pso():
    print("\n" + "=" * 60)
    print("GENERATE PSO DIPANGGIL")
    print("=" * 60)

    if 'user_data' not in session: # kalau user belum isi data diri, lempar ke halaman input
        return redirect(url_for('input.input_data'))

    user_data = session['user_data']
    fingerprint = (
        f"{user_data['jk']}_{user_data['bb']}_{user_data['tb']}_"
        f"{user_data['usia']}_{user_data['aktivitas']}"
    ) # gabungkan data user jadi satu string unik sebagai identitas, buat cek apakah user berubah atau tidak

    # Cek apakah hasil PSO sudah ada untuk user yang sama
    if (
        'pso_hasil' in session and
        'pso_fingerprint' in session and
        session['pso_fingerprint'] == fingerprint # fingerprint cocok = user sama, tidak perlu run PSO lagi
    ):
        print("Hasil PSO sudah ada, langsung tampilkan!")
        return redirect(url_for('pso.rekomendasi_pso', rec_num=1, meal='sarapan'))

    # Jalankan PSO
    print(f"Menjalankan PSO untuk user: {fingerprint}")
    try:
        nutrisi, per_waktu, target_subkategori = hitung_kebutuhan(
            user_data["jk"], user_data["bb"], user_data["tb"],
            user_data["usia"], user_data["aktivitas"]
        ) # hitung kebutuhan kalori dan nutrisi harian berdasarkan data user

        EXCEL_PATH = os.path.join(BASE_DIR, "resep.xlsx") # path ke file database resep
        hasil = rekomendasi_menu_pso(
            EXCEL_PATH, nutrisi, target_subkategori
        ) # jalankan PSO, hasilnya adalah 5 kombinasi menu rekomendasi

        session['pso_hasil']       = hasil # simpan hasil rekomendasi ke session
        session['pso_nutrisi']     = nutrisi # simpan info nutrisi ke session untuk ditampilkan di halaman hasil
        session['pso_fingerprint'] = fingerprint # simpan fingerprint user supaya bisa dicek nanti
        session.modified = True # beritahu Flask bahwa session berubah supaya disimpan

        print("Hasil PSO disimpan ke session!")
        return redirect(url_for('pso.rekomendasi_pso', rec_num=1, meal='sarapan'))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<h1>Error saat menjalankan PSO</h1><pre>{traceback.format_exc()}</pre>", 500 # tampilkan traceback lengkap di browser kalau ada error


# Tampilkan hasil rekomendasi PSO dari session
@pso_bp.route("/<int:rec_num>/<meal>")
def rekomendasi_pso(rec_num, meal):
    if 'user_data' not in session: # belum isi data diri
        return redirect(url_for('input.input_data'))
    if 'pso_hasil' not in session: # belum generate PSO
        return redirect(url_for('pso.generate_pso'))

    try:
        user_data = session['user_data']
        nutrisi   = session['pso_nutrisi']
        hasil     = deserialize_hasil(session['pso_hasil']) # konversi hasil dari dict (session) ke object supaya bisa diakses di template

        if rec_num < 1 or rec_num > len(hasil): # kalau nomor rekomendasi di URL tidak valid, fallback ke rekomendasi 1
            rec_num = 1

        return render_template(
            'pso_rekomendasi.html',
            user_data=user_data,
            nutrisi=nutrisi,
            hasil=hasil,
            rec_num=rec_num,
            current_meal=meal, # waktu makan yang sedang aktif ditampilkan (sarapan/siang/malam)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<h1>Error Rendering</h1><pre>{traceback.format_exc()}</pre>", 500


# Reset hasil PSO dari session agar PSO di-run ulang
@pso_bp.route("/reset")
def reset_pso():
    session.pop('pso_hasil', None) # hapus hasil rekomendasi
    session.pop('pso_nutrisi', None) # hapus data nutrisi
    session.pop('pso_fingerprint', None) # hapus fingerprint supaya PSO mau jalan ulang
    session.modified = True
    print("[PSO] Session di-reset")
    return redirect(url_for('pso.generate_pso'))


print("[PSO Blueprint] Loaded")