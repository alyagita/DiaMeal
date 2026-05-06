import pandas as pd
import numpy as np

def rmse(menu, target_range):
    nutrisi = ["kalori", "karbohidrat", "protein", "lemak", "serat"]  # daftar nutrisi yang dihitung
    error = 0  # inisialisasi total error

    for n in nutrisi:
        min_n, max_n = target_range[n]  # ambil batas bawah & atas dari target
        nilai_menu = menu.get(n, 0) if isinstance(menu, dict) else menu[n]  # ambil nilai nutrisi dari menu

        if nilai_menu < min_n:
            error += ((min_n - nilai_menu) / min_n) ** 2  # kalau kurang dari min → hitung selisih kuadrat ternormalisasi
        elif nilai_menu > max_n:
            error += ((nilai_menu - max_n) / max_n) ** 2  # kalau lebih dari max → hitung selisih kuadrat ternormalisasi
        else:
            error += 0  # kalau masih dalam range → tidak ada error

    return np.sqrt(error / len(nutrisi))  # hitung RMSE

def mae(menu, target_range):
    nutrisi = ["kalori", "karbohidrat", "protein", "lemak", "serat"]
    error = 0

    for n in nutrisi:
        min_n, max_n = target_range[n]
        nilai_menu = menu.get(n, 0) if isinstance(menu, dict) else menu[n]

        if nilai_menu < min_n:
            error += abs((min_n - nilai_menu) / min_n)
        elif nilai_menu > max_n:
            error += abs((nilai_menu - max_n) / max_n)
        else:
            error += 0

    return error / len(nutrisi)

def rank_menu(df, target):
    df = df.copy()  # copy dataframe agar tidak mengubah data asli
    df["rmse"] = df.apply(lambda x: rmse(x, target), axis=1)  # hitung RMSE tiap baris (menu)
    return df.sort_values("rmse").reset_index(drop=True)  # urutkan dari RMSE terkecil (terbaik)

# Fungsi Utama
def rekomendasi_menu(file_excel, target_subkategori):

    xls = pd.ExcelFile(file_excel)  # baca file excel

    sarapan     = pd.read_excel(xls, "Sarapan")      # ambil data menu sarapan
    makan_siang = pd.read_excel(xls, "Makan Siang")  # ambil data makan siang
    makan_malam = pd.read_excel(xls, "Makan Malam")  # ambil data makan malam
    sayur       = pd.read_excel(xls, "Sayur")        # ambil data sayur
    buah        = pd.read_excel(xls, "Buah")         # ambil data buah
    nasi        = pd.read_excel(xls, "Nasi")         # ambil data nasi

    # ranking menu di tiap subkategori berdasarkan RMSE
    sub = {
        "menu_sarapan":  rank_menu(sarapan,     target_subkategori["menu_sarapan"]),
        "sayur_sarapan": rank_menu(sayur,       target_subkategori["sayur_sarapan"]),
        "nasi_sarapan":  rank_menu(nasi,        target_subkategori["nasi_sarapan"]),
        "buah_sarapan":  rank_menu(buah,        target_subkategori["buah_sarapan"]),
        "buah_pagi":     rank_menu(buah,        target_subkategori["buah_pagi"]),
        "menu_siang":    rank_menu(makan_siang, target_subkategori["menu_siang"]),
        "sayur_siang":   rank_menu(sayur,       target_subkategori["sayur_siang"]),
        "nasi_siang":    rank_menu(nasi,        target_subkategori["nasi_siang"]),
        "buah_siang":    rank_menu(buah,        target_subkategori["buah_siang"]),
        "buah_sore":     rank_menu(buah,        target_subkategori["buah_sore"]),
        "menu_malam":    rank_menu(makan_malam, target_subkategori["menu_malam"]),
        "sayur_malam":   rank_menu(sayur,       target_subkategori["sayur_malam"]),
        "nasi_malam":    rank_menu(nasi,        target_subkategori["nasi_malam"]),
        "buah_malam":    rank_menu(buah,        target_subkategori["buah_malam"]),
    }

    hasil = []  # list untuk menyimpan hasil rekomendasi

    # set untuk memastikan menu tidak terduplikasi
    used_menu_sarapan  = set()
    used_sayur_sarapan = set()
    used_buah_sarapan  = set()
    used_buah_pagi     = set()
    used_menu_siang    = set()
    used_sayur_siang   = set()
    used_buah_siang    = set()
    used_buah_sore     = set()
    used_menu_malam    = set()
    used_sayur_malam   = set()
    used_buah_malam    = set()

    for i in range(5):  # generate 5 rekomendasi menu
        satu_hari = {}  # dictionary untuk 1 hari

        def get_unused_menu(df, used_set, nama_kolom="nama_menu"):
            # ambil menu terbaik yang belum pernah dipakai
            for idx in range(len(df)):
                menu_name = df.iloc[idx][nama_kolom]  # ambil nama menu
                if menu_name not in used_set:  # cek apakah sudah pernah dipakai
                    used_set.add(menu_name)  # tandai sebagai sudah dipakai
                    return df.iloc[idx].to_dict()  # kembalikan menu
            return df.iloc[0].to_dict()  # kalau habis, ambil yang paling atas

        # isi menu per waktu makan
        satu_hari["menu_sarapan"]  = get_unused_menu(sub["menu_sarapan"],  used_menu_sarapan)
        satu_hari["sayur_sarapan"] = get_unused_menu(sub["sayur_sarapan"], used_sayur_sarapan)
        satu_hari["buah_sarapan"]  = get_unused_menu(sub["buah_sarapan"],  used_buah_sarapan)
        satu_hari["buah_pagi"]     = get_unused_menu(sub["buah_pagi"],     used_buah_pagi)
        satu_hari["menu_siang"]    = get_unused_menu(sub["menu_siang"],    used_menu_siang)
        satu_hari["sayur_siang"]   = get_unused_menu(sub["sayur_siang"],   used_sayur_siang)
        satu_hari["buah_siang"]    = get_unused_menu(sub["buah_siang"],    used_buah_siang)
        satu_hari["buah_sore"]     = get_unused_menu(sub["buah_sore"],     used_buah_sore)
        satu_hari["menu_malam"]    = get_unused_menu(sub["menu_malam"],    used_menu_malam)
        satu_hari["sayur_malam"]   = get_unused_menu(sub["sayur_malam"],   used_sayur_malam)
        satu_hari["buah_malam"]    = get_unused_menu(sub["buah_malam"],    used_buah_malam)

        # nasi tidak perlu unik (boleh sama)
        for waktu in ["sarapan", "siang", "malam"]:
            key = f"nasi_{waktu}"
            satu_hari[key] = sub[key].iloc[0].to_dict()  # ambil nasi terbaik

        # konversi tipe numpy ke float biasa
        for key in satu_hari:
            satu_hari[key] = {
                k: (float(v) if isinstance(v, (np.integer, np.floating)) else v)
                for k, v in satu_hari[key].items()
            }
        
        # Menampilkan MAE dan RMSE
        for key in satu_hari:
            if key != "targets" and isinstance(satu_hari[key], dict):
                target = target_subkategori.get(key)
                if target:
                    satu_hari[key]["rmse"] = rmse(satu_hari[key], target)
                    satu_hari[key]["mae"] = mae(satu_hari[key], target)

        satu_hari["targets"] = target_subkategori  # simpan target nutrisi
        hasil.append(satu_hari)  # simpan hasil 1 hari

    return hasil  # return 5 rekomendasi