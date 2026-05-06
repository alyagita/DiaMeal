def hitung_kebutuhan(jk, bb, tb, usia, aktivitas):
    # Hitung Berat Badan Ideal (BBI)
    if (jk == "Pria" and tb < 160) or (jk == "Wanita" and tb < 150):
        bbi = tb - 100
    else:
        bbi = 0.90 * (tb - 100)

    # Tentukan status gizi
    if bb < bbi - (0.10 * bbi): # batas bawah
        status = "Kurus"
    elif bb > bbi + (0.10 * bbi): #batas atas
        status = "Gemuk"
    else:
        status = "Normal"

    # Hitung kebutuhan kalori dasar
    kalori = bbi * (30 if jk == "Pria" else 25)

    # Koreksi kalori berdasarkan usia
    if usia >= 70:
        kalori = kalori - (0.20 * kalori)
    elif usia >= 60:
        kalori = kalori - (0.15 * kalori)
    elif usia >= 50:
        kalori = kalori - (0.10 * kalori)
    elif usia >= 40:
        kalori = kalori - (0.05 * kalori)

    # Koreksi kalori berdasarkan aktivitas
    if aktivitas == "Istirahat":
        kalori = kalori + (0.10 * kalori)
    elif aktivitas == "Ringan":
        kalori = kalori + (0.20 * kalori)
    elif aktivitas == "Sedang":
        kalori = kalori + (0.30 * kalori)
    elif aktivitas == "Berat":
        kalori = kalori + (0.40 * kalori)
    elif aktivitas == "Sangat Berat":
        kalori = kalori + (0.50 * kalori)

    # Tentukan range kalori berdasarkan status gizi
    if status == "Gemuk":
        kalori_min = kalori - (0.30 * kalori)
        kalori_max = kalori - (0.20 * kalori)
    elif status == "Kurus":
        kalori_min = kalori + (0.20 * kalori)
        kalori_max = kalori + (0.30 * kalori)
    else:
        kalori_min = kalori
        kalori_max = kalori

    # Cek batas minimum kalori
    if jk == "Wanita":
        if kalori_min < 1000:
            kalori_min = 1000
    else:
        if kalori_min < 1200:
            kalori_min = 1200

    # Dictionary distribusi kalori per waktu makan
    distribusi = {
        "Sarapan": 0.20,
        "Camilan Pagi": 0.10,
        "Makan Siang": 0.30,
        "Camilan Sore": 0.15,
        "Makan Malam": 0.25
    }

    # Dictionary hitung kebutuhan nutrisi harian
    nutrisi = {
        "kalori": (kalori_min, kalori_max),
        "karbohidrat": (
            (0.45 * kalori_min) / 4,
            (0.65 * kalori_max) / 4
        ),
        "protein": (
            (0.10 * kalori_min) / 4,
            (0.20 * kalori_max) / 4
        ),
        "lemak": (
            (0.20 * kalori_min) / 9,
            (0.25 * kalori_max) / 9
        ),
        "serat": (25, 35)
    }

    # Proses perhitungan kebutuhan nutrisi per waktu makan
    per_waktu = {}
    for waktu, persen in distribusi.items():
        per_waktu[waktu] = {
            "kalori": (
                nutrisi["kalori"][0] * persen, # 0 kalori minimum harian
                nutrisi["kalori"][1] * persen  # 1 kalori maksimum harian
            ),
            "karbohidrat": (
                nutrisi["karbohidrat"][0] * persen,
                nutrisi["karbohidrat"][1] * persen
            ),
            "protein": (
                nutrisi["protein"][0] * persen,
                nutrisi["protein"][1] * persen
            ),
            "lemak": (
                nutrisi["lemak"][0] * persen,
                nutrisi["lemak"][1] * persen
            ),
            "serat": (
                nutrisi["serat"][0] * persen,
                nutrisi["serat"][1] * persen
            )
        }
     
    # Mendefinisikan proporsi isi piring (untuk waktu makan utama)
    PROPORSI_NASI = 1 / 3      # 33.3% makanan pokok
    PROPORSI_SAYUR = 1 / 3     # 33.3% sayur
    PROPORSI_LAUK = 1 / 6      # 16.7% menu utama (lauk)
    PROPORSI_BUAH = 1 / 6      # 16.7% buah
    
    # fungsi untuk membagi target nutrisi berdasarkan proporsi isi piring
    def bagi_target(target_kategori, proporsi):
        return {
            "kalori": (
                target_kategori["kalori"][0] * proporsi, # batas bawah
                target_kategori["kalori"][1] * proporsi # batas atas
            ),
            "karbohidrat": (
                target_kategori["karbohidrat"][0] * proporsi,
                target_kategori["karbohidrat"][1] * proporsi
            ),
            "protein": (
                target_kategori["protein"][0] * proporsi,
                target_kategori["protein"][1] * proporsi
            ),
            "lemak": (
                target_kategori["lemak"][0] * proporsi,
                target_kategori["lemak"][1] * proporsi
            ),
            "serat": (
                target_kategori["serat"][0] * proporsi,
                target_kategori["serat"][1] * proporsi
            )
        }
    
    # Dictionary perhitungan untuk setiap sub-kategori makanan 
    target_subkategori = {
        # SARAPAN
        "nasi_sarapan": bagi_target(per_waktu["Sarapan"], PROPORSI_NASI),
        "sayur_sarapan": bagi_target(per_waktu["Sarapan"], PROPORSI_SAYUR),
        "menu_sarapan": bagi_target(per_waktu["Sarapan"], PROPORSI_LAUK),
        "buah_sarapan": bagi_target(per_waktu["Sarapan"], PROPORSI_BUAH),
        
        # CAMILAN PAGI (hanya buah, tanpa pembagian)
        "buah_pagi": per_waktu["Camilan Pagi"],
        
        # MAKAN SIANG
        "nasi_siang": bagi_target(per_waktu["Makan Siang"], PROPORSI_NASI),
        "sayur_siang": bagi_target(per_waktu["Makan Siang"], PROPORSI_SAYUR),
        "menu_siang": bagi_target(per_waktu["Makan Siang"], PROPORSI_LAUK),
        "buah_siang": bagi_target(per_waktu["Makan Siang"], PROPORSI_BUAH),
        
        # CAMILAN SORE (hanya buah, tanpa pembagian)
        "buah_sore": per_waktu["Camilan Sore"],
        
        # MAKAN MALAM
        "nasi_malam": bagi_target(per_waktu["Makan Malam"], PROPORSI_NASI),
        "sayur_malam": bagi_target(per_waktu["Makan Malam"], PROPORSI_SAYUR),
        "menu_malam": bagi_target(per_waktu["Makan Malam"], PROPORSI_LAUK),
        "buah_malam": bagi_target(per_waktu["Makan Malam"], PROPORSI_BUAH),
    }
    
    return nutrisi, per_waktu, target_subkategori
    # nutrisi -> kebutuhan nutrisi harian
    # per_waktu -> kebutuhan nutrisi per kategori waktu makan
    # target_subkategori -> kebutuhan nutrisi yang per sub kategori waktu makan (pembagian isi piring)