import pandas as pd
import numpy as np

NUTRISI_KEYS = ["kalori", "karbohidrat", "protein", "lemak", "serat"]

SUBKATEGORI_ORDER = [
    "menu_sarapan", "sayur_sarapan", "nasi_sarapan", "buah_sarapan",
    "buah_pagi",
    "menu_siang", "sayur_siang", "nasi_siang", "buah_siang",
    "buah_sore",
    "menu_malam", "sayur_malam", "nasi_malam", "buah_malam",
]

SUBKATEGORI_NASI = {"nasi_sarapan", "nasi_siang", "nasi_malam"}

# Hitung total penalti satu menu terhadap target nutrisi subkategori
# penalti dihitung per nutrisi: selisih nilai dengan batas min/max target
# jika nilai dalam range, penaltinya 0
def hitung_penalti(menu_dict, target_range):
    total_penalti = 0.0
    for nama_nutrisi in NUTRISI_KEYS:
        min_n, max_n = target_range[nama_nutrisi]
        nilai = float(menu_dict.get(nama_nutrisi, 0))
        if nilai < min_n:
            total_penalti += abs(nilai - min_n) / min_n
        elif nilai > max_n:
            total_penalti += abs(nilai - max_n) / max_n
    return total_penalti


# Hitung nilai fitness dari total penalti
# semakin kecil penalti, semakin besar fitness, semakin baik menu tersebut
def hitung_fitness(total_penalti):
    if total_penalti == 0:
        return float('inf')
    return (1.0 / total_penalti) * 1000.0

def hitung_mae(kandungan, target_range):
    total_error = 0.0
    for nama_nutrisi in NUTRISI_KEYS:
        min_n, max_n = target_range[nama_nutrisi]
        nilai = float(kandungan.get(nama_nutrisi, 0))
        if nilai < min_n:
            total_error += abs((nilai - min_n) / min_n)
        elif nilai > max_n:
            total_error += abs((nilai - max_n) / max_n)
    return total_error / len(NUTRISI_KEYS)

# Hitung RMSE menu terhadap target nutrisi
# digunakan sebagai metrik evaluasi per menu dan per kategori waktu makan
def hitung_rmse(kandungan, target_range):
    total_error = 0.0
    for nama_nutrisi in NUTRISI_KEYS:
        min_n, max_n = target_range[nama_nutrisi]
        nilai = float(kandungan.get(nama_nutrisi, 0))
        if nilai < min_n:
            total_error += ((nilai - min_n) / min_n) ** 2
        elif nilai > max_n:
            total_error += ((nilai - max_n) / max_n) ** 2
    return np.sqrt(total_error / len(NUTRISI_KEYS))

# Konversi tipe data numpy ke tipe Python biasa
# diperlukan agar tidak error saat data dikirim ke template HTML
def bersihkan_menu(menu_dict):
    return {
        kolom: (float(nilai) if isinstance(nilai, (np.integer, np.floating)) else nilai)
        for kolom, nilai in menu_dict.items()
    }


# Buat key unik dari nama_menu + porsi
# digunakan untuk mendeteksi duplikat antar menu
def key_unik(menu_dict):
    nama  = str(menu_dict.get("nama_menu", "")).strip()
    porsi = str(menu_dict.get("porsi", "")).strip()
    return (nama, porsi)


# Jalankan PSO untuk satu subkategori
# jumlah partikel = jumlah resep, iterasi maksimum = jumlah resep
def pso_satu_subkategori(dataset, target_sub, nama_sub,
                          w_min, w_max, c1, c2):

    jumlah_resep = len(dataset)
    jumlah_partikel = jumlah_resep * 1
    x_min        = 0
    x_max        = jumlah_resep - 1
    iterasi_maks = jumlah_resep

    # Seed dipasang agar hasil PSO konsisten setiap run
    np.random.seed(42)

    # Inisialisasi posisi partikel secara acak dan kecepatan awal = 0
    posisi_partikel    = np.round(x_min + np.random.random(jumlah_partikel) * (x_max - x_min)).astype(float)
    kecepatan_partikel = np.zeros(jumlah_partikel, dtype=float)

    # Inisialisasi pbest dari posisi awal tiap partikel
    pbest_posisi  = posisi_partikel.copy()
    pbest_fitness = np.zeros(jumlah_partikel, dtype=float)

    for i in range(jumlah_partikel):
        indeks_menu      = int(round(np.clip(posisi_partikel[i], x_min, x_max)))
        menu             = dataset.iloc[indeks_menu].to_dict()
        penalti          = hitung_penalti(menu, target_sub)
        pbest_fitness[i] = hitung_fitness(penalti)

    # Inisialisasi gbest dari pbest dengan fitness terbesar
    indeks_terbaik = int(np.argmax(pbest_fitness))
    gbest_posisi   = pbest_posisi[indeks_terbaik]
    gbest_fitness  = pbest_fitness[indeks_terbaik]

    # simpan menu yang pernah dikunjungi tiap partikel
    visit_partikel = [set() for _ in range(jumlah_partikel)]
        
    # Iterasi PSO
    for iterasi in range(iterasi_maks):

        # Bobot inersia menurun linier setiap iterasi (LVIW)
        w = (w_max - w_min) * (iterasi_maks - iterasi) / iterasi_maks + w_min

        for i in range(jumlah_partikel):
            r1 = np.random.random()
            r2 = np.random.random()

            # Hitung kecepatan baru
            kecepatan_baru = (
                w  * kecepatan_partikel[i]
                + c1 * r1 * (pbest_posisi[i] - posisi_partikel[i])
                + c2 * r2 * (gbest_posisi    - posisi_partikel[i])
            )
            kecepatan_partikel[i] = kecepatan_baru

            # Perbarui posisi, bulatkan ke integer, pastikan dalam batas
            posisi_partikel[i] = np.clip(
                round(posisi_partikel[i] + kecepatan_baru),
                x_min, x_max
            )

            # Hitung fitness menu pada posisi baru
            indeks_menu  = int(round(posisi_partikel[i]))
            menu         = dataset.iloc[indeks_menu].to_dict()
            penalti_baru = hitung_penalti(menu, target_sub)
            fitness_baru = hitung_fitness(penalti_baru)

            visit_partikel[i].add(indeks_menu)

            # Perbarui pbest jika fitness baru lebih baik
            if fitness_baru > pbest_fitness[i]:
                pbest_fitness[i] = fitness_baru
                pbest_posisi[i]  = posisi_partikel[i]

        # Perbarui gbest setelah semua partikel diupdate
        for i in range(jumlah_partikel):
            if pbest_fitness[i] > gbest_fitness:
                gbest_fitness = pbest_fitness[i]
                gbest_posisi  = pbest_posisi[i]

    fitness_per_menu = {}

    for i in range(jumlah_partikel):
        for indeks_menu in visit_partikel[i]:
            menu = dataset.iloc[indeks_menu].to_dict()
            penalti = hitung_penalti(menu, target_sub)
            fitness = hitung_fitness(penalti)

            if indeks_menu not in fitness_per_menu:
                fitness_per_menu[indeks_menu] = fitness
            else:
                fitness_per_menu[indeks_menu] = max(fitness_per_menu[indeks_menu], fitness)
                
    # Urutkan menu dari fitness terbesar ke terkecil
    menu_terurut = sorted(fitness_per_menu.items(), key=lambda x: -x[1])

    # Susun daftar kandidat dan pool rekomendasi dari hasil pengurutan
    menu_sudah_ada   = set()
    semua_kandidat   = []
    pool_rekomendasi = []

    for indeks_menu, fitness_val in menu_terurut:
        menu  = bersihkan_menu(dataset.iloc[indeks_menu].to_dict())
        kunci = key_unik(menu)

        if kunci in menu_sudah_ada:
            continue

        menu_sudah_ada.add(kunci)

        penalti_menu        = float(hitung_penalti(menu, target_sub))
        menu["penalti"]     = penalti_menu
        menu["fitness_pso"] = hitung_fitness(penalti_menu)
        menu["rmse"]        = float(hitung_rmse(menu, target_sub))

        semua_kandidat.append(menu)
        pool_rekomendasi.append(menu)

    # Jika pool kurang dari 5, isi dengan menu rank-1
    while len(pool_rekomendasi) < 5:
        pool_rekomendasi.append(pool_rekomendasi[0])

    print(f"    [{nama_sub:15s}] iterasi_maks={iterasi_maks:3d} | "
          f"total_menu={len(semua_kandidat):2d} | "
          f"penalti_rank1={semua_kandidat[0]['penalti']:.4f} | "
          f"rmse_rank1={semua_kandidat[0]['rmse']:.4f} | "
          f"menu='{semua_kandidat[0].get('nama_menu','')}'")

    return pool_rekomendasi, semua_kandidat


# Fungsi untuk menghasilkan 5 rekomendasi menu harian dengan PSO
def rekomendasi_menu_pso(file_excel, kebutuhan_harian, target_subkategori=None,
                          w_min=0.4, w_max=0.8, c1=1.0, c2=1.0):

    xls        = pd.ExcelFile(file_excel)
    sarapan_df = pd.read_excel(xls, "Sarapan")
    siang_df   = pd.read_excel(xls, "Makan Siang")
    malam_df   = pd.read_excel(xls, "Makan Malam")
    sayur_df   = pd.read_excel(xls, "Sayur")
    buah_df    = pd.read_excel(xls, "Buah")
    nasi_df    = pd.read_excel(xls, "Nasi")

    dataset_per_sub = {
        "menu_sarapan":  sarapan_df,
        "sayur_sarapan": sayur_df,
        "nasi_sarapan":  nasi_df,
        "buah_sarapan":  buah_df,
        "buah_pagi":     buah_df.copy(),
        "menu_siang":    siang_df,
        "sayur_siang":   sayur_df.copy(),
        "nasi_siang":    nasi_df.copy(),
        "buah_siang":    buah_df.copy(),
        "buah_sore":     buah_df.copy(),
        "menu_malam":    malam_df,
        "sayur_malam":   sayur_df.copy(),
        "nasi_malam":    nasi_df.copy(),
        "buah_malam":    buah_df.copy(),
    }

    print("\n" + "=" * 80)
    print("  MEMULAI OPTIMASI PSO")
    print("=" * 80)
    print(f"  w_min={w_min} | w_max={w_max} | c1={c1} | c2={c2}")
    print("=" * 80 + "\n")

    pool_per_sub     = {}
    kandidat_per_sub = {}

    for nama_sub in SUBKATEGORI_ORDER:
        pool_menu, semua_kandidat = pso_satu_subkategori(
            dataset_per_sub[nama_sub],
            target_subkategori[nama_sub],
            nama_sub,
            w_min=w_min, w_max=w_max, c1=c1, c2=c2
        )
        pool_per_sub[nama_sub]     = pool_menu # yang digunakan untuk 5 rekomendasi
        kandidat_per_sub[nama_sub] = semua_kandidat

    print(f"\n  PSO selesai")
    print(f"  Menyusun 5 kombinasi rekomendasi\n")

    hasil = []

    # Catat menu yang sudah dipakai per subkategori agar tidak duplikat
    menu_terpakai = {nama_sub: set() for nama_sub in SUBKATEGORI_ORDER}

    for rank in range(1, 6):
        menu_hari_ini = {}

        for nama_sub in SUBKATEGORI_ORDER:
            pool_menu = pool_per_sub[nama_sub]

            # Nasi selalu pakai rank-1 untuk semua rekomendasi
            if nama_sub in SUBKATEGORI_NASI:
                menu_hari_ini[nama_sub] = pool_menu[0]
                continue

            # Pilih menu yang belum pernah dipakai di rank sebelumnya
            menu_terpilih = None
            for menu in pool_menu:
                kunci = key_unik(menu)
                if kunci not in menu_terpakai[nama_sub]:
                    menu_terpilih = menu
                    menu_terpakai[nama_sub].add(kunci)
                    break

            # Jika semua menu di pool sudah terpakai, fallback ke rank-1
            if menu_terpilih is None:
                menu_terpilih = pool_menu[0]
                print(f"    [{nama_sub}] Rank {rank}: pool habis, menggunakan menu rank-1")

            menu_hari_ini[nama_sub] = menu_terpilih

        menu_hari_ini["targets"] = {
            "menu_sarapan":  target_subkategori["menu_sarapan"],
            "sayur_sarapan": target_subkategori["sayur_sarapan"],
            "nasi_sarapan":  target_subkategori["nasi_sarapan"],
            "buah_sarapan":  target_subkategori["buah_sarapan"],
            "buah_pagi":     target_subkategori["buah_pagi"],
            "menu_siang":    target_subkategori["menu_siang"],
            "sayur_siang":   target_subkategori["sayur_siang"],
            "nasi_siang":    target_subkategori["nasi_siang"],
            "buah_siang":    target_subkategori["buah_siang"],
            "buah_sore":     target_subkategori["buah_sore"],
            "menu_malam":    target_subkategori["menu_malam"],
            "sayur_malam":   target_subkategori["sayur_malam"],
            "nasi_malam":    target_subkategori["nasi_malam"],
            "buah_malam":    target_subkategori["buah_malam"],
        }


        # Hitung RMSE dan MAE per menu individual
        for nama_sub in SUBKATEGORI_ORDER:
            menu_hari_ini[nama_sub]["rmse"] = float(
                hitung_rmse(menu_hari_ini[nama_sub], target_subkategori[nama_sub])
            )
            menu_hari_ini[nama_sub]["mae"] = float(
                hitung_mae(menu_hari_ini[nama_sub], target_subkategori[nama_sub])
            )

        menu_hari_ini["rank"] = rank

        print(f"  Rekomendasi #{rank}")
        print(f"    Lauk Sarapan  : {menu_hari_ini['menu_sarapan'].get('nama_menu','')} ({menu_hari_ini['menu_sarapan'].get('porsi','')})")
        print(f"    Sayur Sarapan : {menu_hari_ini['sayur_sarapan'].get('nama_menu','')} ({menu_hari_ini['sayur_sarapan'].get('porsi','')})")
        print(f"    Nasi Sarapan  : {menu_hari_ini['nasi_sarapan'].get('nama_menu','')} ({menu_hari_ini['nasi_sarapan'].get('porsi','')})")
        print(f"    Buah Sarapan  : {menu_hari_ini['buah_sarapan'].get('nama_menu','')} ({menu_hari_ini['buah_sarapan'].get('porsi','')})")
        print(f"    Camilan Pagi  : {menu_hari_ini['buah_pagi'].get('nama_menu','')} ({menu_hari_ini['buah_pagi'].get('porsi','')})")
        print(f"    Lauk Siang    : {menu_hari_ini['menu_siang'].get('nama_menu','')} ({menu_hari_ini['menu_siang'].get('porsi','')})")
        print(f"    Sayur Siang   : {menu_hari_ini['sayur_siang'].get('nama_menu','')} ({menu_hari_ini['sayur_siang'].get('porsi','')})")
        print(f"    Nasi Siang    : {menu_hari_ini['nasi_siang'].get('nama_menu','')} ({menu_hari_ini['nasi_siang'].get('porsi','')})")
        print(f"    Buah Siang    : {menu_hari_ini['buah_siang'].get('nama_menu','')} ({menu_hari_ini['buah_siang'].get('porsi','')})")
        print(f"    Camilan Sore  : {menu_hari_ini['buah_sore'].get('nama_menu','')} ({menu_hari_ini['buah_sore'].get('porsi','')})")
        print(f"    Lauk Malam    : {menu_hari_ini['menu_malam'].get('nama_menu','')} ({menu_hari_ini['menu_malam'].get('porsi','')})")
        print(f"    Sayur Malam   : {menu_hari_ini['sayur_malam'].get('nama_menu','')} ({menu_hari_ini['sayur_malam'].get('porsi','')})")
        print(f"    Nasi Malam    : {menu_hari_ini['nasi_malam'].get('nama_menu','')} ({menu_hari_ini['nasi_malam'].get('porsi','')})")
        print(f"    Buah Malam    : {menu_hari_ini['buah_malam'].get('nama_menu','')} ({menu_hari_ini['buah_malam'].get('porsi','')})\n")

        hasil.append(menu_hari_ini)

    print("=" * 80)
    print(f"  5 REKOMENDASI BERHASIL DIBUAT")
    print("=" * 80 + "\n")

    return hasil # return 5 rekomendasi