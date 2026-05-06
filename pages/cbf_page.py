from flask import Blueprint, render_template, redirect, url_for, session
import os
import sys

# Menentukan base directory project (folder utama)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Menambahkan folder 'modules' ke path agar bisa import file di dalamnya
sys.path.insert(0, os.path.join(BASE_DIR, 'modules'))

# Import fungsi hitung kebutuhan nutrisi dan rekomendasi CBF
from nutrisi import hitung_kebutuhan
from cbf import rekomendasi_menu

# Membuat blueprint Flask untuk fitur CBF
cbf_bp = Blueprint('cbf', __name__, url_prefix='/cbf')

@cbf_bp.route("/generate")
def generate_cbf():
    # Cek apakah data user sudah ada di session
    if 'user_data' not in session:
        return redirect(url_for('input.input_data'))

    # Ambil data user dari session
    user_data = session['user_data']

    # Membuat fingerprint untuk membedakan input user
    fingerprint = (
        f"{user_data['jk']}_{user_data['bb']}_{user_data['tb']}_"
        f"{user_data['usia']}_{user_data['aktivitas']}"
    )

    # Jika hasil sebelumnya masih valid (input sama), tidak perlu generate ulang
    if (
        'cbf_hasil' in session and
        'cbf_fingerprint' in session and
        session['cbf_fingerprint'] == fingerprint
    ):
        return redirect(url_for('cbf.rekomendasi_cbf', rec_num=1, meal='sarapan'))

    try:
        # Hitung kebutuhan nutrisi harian, per waktu makan, dan subkategori
        nutrisi, per_waktu, target_subkategori = hitung_kebutuhan(
            user_data["jk"], user_data["bb"], user_data["tb"],
            user_data["usia"], user_data["aktivitas"]
        )

        # Menentukan lokasi file dataset resep.xlsx
        EXCEL_PATH = os.path.join(BASE_DIR, "resep.xlsx")

        # Generate rekomendasi menu menggunakan metode CBF
        hasil = rekomendasi_menu(EXCEL_PATH, target_subkategori)

        # Simpan hasil ke session agar bisa digunakan di halaman lain
        session['cbf_hasil']       = hasil
        session['cbf_nutrisi']     = nutrisi
        session['cbf_fingerprint'] = fingerprint
        session.modified = True  # tandai session berubah

        # Redirect ke halaman hasil rekomendasi pertama (sarapan)
        return redirect(url_for('cbf.rekomendasi_cbf', rec_num=1, meal='sarapan'))

    except Exception as e:
        # Menampilkan error jika terjadi kesalahan
        import traceback
        traceback.print_exc()
        return f"<h1>Error CBF</h1><pre>{traceback.format_exc()}</pre>", 500


@cbf_bp.route("/<int:rec_num>/<meal>")
def rekomendasi_cbf(rec_num, meal):
    # Cek apakah data user tersedia
    if 'user_data' not in session:
        return redirect(url_for('input.input_data'))

    # Cek apakah hasil CBF sudah ada
    if 'cbf_hasil' not in session:
        return redirect(url_for('cbf.generate_cbf'))

    try:
        # Ambil data dari session
        user_data = session['user_data']
        nutrisi   = session['cbf_nutrisi']
        hasil     = session['cbf_hasil']

        # Validasi nomor rekomendasi (harus dalam range)
        if rec_num < 1 or rec_num > len(hasil):
            rec_num = 1

        # Render halaman HTML untuk menampilkan rekomendasi
        return render_template(
            'cbf_rekomendasi.html',
            user_data=user_data,
            nutrisi=nutrisi,
            hasil=hasil,
            rec_num=rec_num,
            current_meal=meal,
        )
    except Exception as e:
        # Menampilkan error jika gagal render
        import traceback
        traceback.print_exc()
        return f"<h1>Error Rendering CBF</h1><pre>{traceback.format_exc()}</pre>", 500


@cbf_bp.route("/reset")
def reset_cbf():
    # Menghapus data hasil CBF dari session (reset)
    session.pop('cbf_hasil', None)
    session.pop('cbf_nutrisi', None)
    session.pop('cbf_fingerprint', None)
    session.modified = True

    # Redirect untuk generate ulang rekomendasi
    return redirect(url_for('cbf.generate_cbf'))


# Debug: memastikan blueprint berhasil diload
print("[CBF Blueprint] Loaded")