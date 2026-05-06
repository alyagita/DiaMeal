# ============================================================================
# FILE: routes/pso_analisis.py
# Blueprint analisis RMSE & MAE PSO - bar chart + tabel per metrik
# ============================================================================

from flask import Blueprint, render_template, redirect, url_for, session
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'modules'))

pso_analisis_bp = Blueprint('pso_analisis', __name__, url_prefix='/pso/analisis')


def dict_to_object(d):
    class DictObject:
        def __init__(self, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    setattr(self, key, dict_to_object(value))
                elif isinstance(value, list):
                    setattr(self, key, [
                        dict_to_object(item) if isinstance(item, dict) else item
                        for item in value
                    ])
                else:
                    setattr(self, key, value)
        def __getitem__(self, key):
            return getattr(self, key)
        def get(self, key, default=None):
            return getattr(self, key, default)
    return DictObject(d)


def deserialize_hasil(serialized):
    return [dict_to_object(item) for item in serialized]


def img_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return f"data:image/png;base64,{b64}"


def buat_bar_chart(nilai_list, idx_terbaik, judul, ylabel):
    """Buat bar chart untuk RMSE atau MAE"""
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')

    # Normalisasi: nilai terkecil -> biru tua, terbesar -> biru muda
    min_v = min(nilai_list)
    max_v_n = max(nilai_list)
    span  = max_v_n - min_v if max_v_n != min_v else 1

    def nilai_to_color(val):
        t = (val - min_v) / span
        r = int(0x0F + t * (0xBD - 0x0F))
        g = int(0x28 + t * (0xE8 - 0x28))
        b = int(0x54 + t * (0xF5 - 0x54))
        return (r/255, g/255, b/255)

    bar_colors = [nilai_to_color(v) for v in nilai_list]

    x    = np.arange(5)
    bars = ax.bar(x, nilai_list, color=bar_colors, edgecolor='white',
                  linewidth=1.0, width=0.52, zorder=3)

    max_v = max(nilai_list)
    for bar, val in zip(bars, nilai_list):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_v * 0.012,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=9.5,
                fontweight='bold', color='#333')

    ax.set_xticks(x)
    ax.set_xticklabels([f'Rekomendasi {i+1}' for i in range(5)],
                       fontsize=10.5, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=11, fontweight='bold', color='#333')
    ax.set_title(judul, fontsize=13,
                 fontweight='bold', pad=14, color='#0F2854')
    ax.set_ylim(0, max_v * 1.18)
    ax.yaxis.grid(True, linestyle='--', alpha=0.45, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    return img_to_b64(fig)


# 14 subkategori dalam urutan kolom tabel
SUB_COLS = [
    ('Lauk Sarapan',  'menu_sarapan'),
    ('Sayur Sarapan', 'sayur_sarapan'),
    ('Nasi Sarapan',  'nasi_sarapan'),
    ('Buah Sarapan',  'buah_sarapan'),
    ('Buah Pagi',     'buah_pagi'),
    ('Lauk Siang',    'menu_siang'),
    ('Sayur Siang',   'sayur_siang'),
    ('Nasi Siang',    'nasi_siang'),
    ('Buah Siang',    'buah_siang'),
    ('Buah Sore',     'buah_sore'),
    ('Lauk Malam',    'menu_malam'),
    ('Sayur Malam',   'sayur_malam'),
    ('Nasi Malam',    'nasi_malam'),
    ('Buah Malam',    'buah_malam'),
]


@pso_analisis_bp.route('/')
def analisis():
    if 'pso_hasil' not in session:
        return redirect(url_for('pso.generate_pso'))

    hasil = deserialize_hasil(session['pso_hasil'])

    # ========================================================================
    # RMSE DATA
    # ========================================================================
    rows_rmse = []
    for i in range(5):
        cols = [getattr(hasil[i], key).rmse for _, key in SUB_COLS]
        rata = sum(cols) / len(cols)
        rows_rmse.append({'rek': i + 1, 'cols': cols, 'rata': rata})

    n_cols = len(SUB_COLS)
    min_cols_rmse = [min(rows_rmse[i]['cols'][j] for i in range(5)) for j in range(n_cols)]
    min_rata_rmse = min(r['rata'] for r in rows_rmse)
    idx_terbaik_rmse = min(range(5), key=lambda i: rows_rmse[i]['rata'])

    rata_list_rmse = [r['rata'] for r in rows_rmse]
    chart_rmse = buat_bar_chart(rata_list_rmse, idx_terbaik_rmse,
                                 'Grafik Rata-Rata RMSE Setiap Rekomendasi',
                                 'Rata-Rata RMSE')

    # ========================================================================
    # MAE DATA
    # ========================================================================
    rows_mae = []
    for i in range(5):
        cols = [getattr(hasil[i], key).mae for _, key in SUB_COLS]
        rata = sum(cols) / len(cols)
        rows_mae.append({'rek': i + 1, 'cols': cols, 'rata': rata})

    min_cols_mae = [min(rows_mae[i]['cols'][j] for i in range(5)) for j in range(n_cols)]
    min_rata_mae = min(r['rata'] for r in rows_mae)
    idx_terbaik_mae = min(range(5), key=lambda i: rows_mae[i]['rata'])

    rata_list_mae = [r['rata'] for r in rows_mae]
    chart_mae = buat_bar_chart(rata_list_mae, idx_terbaik_mae,
                                'Grafik Rata-Rata MAE Setiap Rekomendasi',
                                'Rata-Rata MAE')

    return render_template(
        'pso_analisis.html',
        # RMSE
        rows_rmse=rows_rmse,
        min_cols_rmse=min_cols_rmse,
        min_rata_rmse=min_rata_rmse,
        idx_terbaik_rmse=idx_terbaik_rmse,
        chart_rmse=chart_rmse,
        # MAE
        rows_mae=rows_mae,
        min_cols_mae=min_cols_mae,
        min_rata_mae=min_rata_mae,
        idx_terbaik_mae=idx_terbaik_mae,
        chart_mae=chart_mae,
        # Common
        sub_cols=SUB_COLS,
    )


print("[PSO Analisis Blueprint] Loaded")