# SEMUA KODE UNTUK FOLDER PAGES

## 1. `pages/__init__.py`

```python
# File kosong - hanya untuk membuat pages menjadi package Python
```

---

## 2. `pages/home.py`

```python
"""
Halaman utama aplikasi DiaMeal
"""
from flask import Blueprint, render_template, redirect, url_for, request

home_bp = Blueprint('home', __name__)


@home_bp.route("/", methods=["GET", "POST"])
def index():
    """Halaman utama / landing page"""
    if request.method == "POST":
        return redirect(url_for('input.input_data'))
    return render_template('home.html')
```

---

## 3. `pages/input.py`

```python
"""
Halaman input data pengguna
"""
from flask import Blueprint, render_template, redirect, url_for, request, session

input_bp = Blueprint('input', __name__)


@input_bp.route("/input", methods=["GET", "POST"])
def input_data():
    """Halaman input data diri pengguna"""
    if request.method == "POST":
        session['user_data'] = {
            "nama": request.form["nama"],
            "jk": request.form["jk"],
            "bb": float(request.form["bb"]),
            "tb": float(request.form["tb"]),
            "usia": int(request.form["usia"]),
            "aktivitas": request.form["aktivitas"]
        }
        return redirect(url_for('metode.pilih_metode'))
    
    return render_template('input.html')
```

---

## 4. `pages/metode.py`

```python
"""
Halaman pemilihan metode rekomendasi
"""
from flask import Blueprint, render_template, redirect, url_for, session

metode_bp = Blueprint('metode', __name__)


@metode_bp.route("/metode")
def pilih_metode():
    """Halaman pemilihan metode CBF atau PSO"""
    if 'user_data' not in session:
        return redirect(url_for('input.input_data'))
    return render_template('metode.html', user_data=session['user_data'])
```

---

## 5. `pages/cbf_page.py`

```python
"""
Halaman rekomendasi menggunakan Content-Based Filtering
"""
from flask import Blueprint, render_template, redirect, url_for, session
import os
import sys

# Tambahkan path modules ke sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

from nutrisi import hitung_kebutuhan
from cbf import rekomendasi_menu

cbf_bp = Blueprint('cbf', __name__, url_prefix='/cbf')


@cbf_bp.route("/generate", methods=["GET", "POST"])
def generate_cbf():
    """Generate rekomendasi CBF"""
    print("=== GENERATE CBF DIPANGGIL ===")
    
    if 'user_data' not in session:
        print("ERROR: user_data tidak ada!")
        return redirect(url_for('input.input_data'))
    
    try:
        return redirect(url_for('cbf.rekomendasi_cbf', rec_num=1, meal='sarapan'))
        
    except Exception as e:
        print(f"ERROR EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>", 500


@cbf_bp.route("/<int:rec_num>/<meal>")
def rekomendasi_cbf(rec_num, meal):
    """Tampilkan halaman rekomendasi CBF"""
    print(f"=== REKOMENDASI CBF DIPANGGIL ===")
    print(f"rec_num: {rec_num}, meal: {meal}")
    
    if 'user_data' not in session:
        print("ERROR: user_data tidak ada!")
        return redirect(url_for('input.input_data'))
    
    try:
        user_data = session['user_data']
        
        # Generate nutrisi dan hasil setiap kali halaman dibuka
        nutrisi, per_waktu = hitung_kebutuhan(
            user_data["jk"],
            user_data["bb"],
            user_data["tb"],
            user_data["usia"],
            user_data["aktivitas"]
        )
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        EXCEL_PATH = os.path.join(BASE_DIR, "resep.xlsx")
        
        # Generate hasil CBF
        hasil = rekomendasi_menu(EXCEL_PATH, nutrisi)
        
        print(f"Hasil berhasil di-generate: {len(hasil)} kombinasi")
        
        return render_template(
            'cbf_rekomendasi.html',
            user_data=user_data,
            nutrisi=nutrisi,
            hasil=hasil,
            rec_num=rec_num,
            current_meal=meal
        )
        
    except Exception as e:
        print(f"ERROR RENDER: {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Error Rendering</h1><pre>{traceback.format_exc()}</pre>", 500
```

---

## 6. `pages/pso_page.py`

```python
"""
Halaman rekomendasi menggunakan Particle Swarm Optimization
"""
from flask import Blueprint, render_template, redirect, url_for, session
import os
import sys

# Tambahkan path modules ke sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

from nutrisi import hitung_kebutuhan
from pso import rekomendasi_menu_pso

pso_bp = Blueprint('pso', __name__, url_prefix='/pso')


@pso_bp.route("/generate", methods=["GET", "POST"])
def generate_pso():
    """Generate rekomendasi PSO"""
    print("=== GENERATE PSO DIPANGGIL ===")
    
    if 'user_data' not in session:
        print("ERROR: user_data tidak ada!")
        return redirect(url_for('input.input_data'))
    
    try:
        return redirect(url_for('pso.rekomendasi_pso', rec_num=1, meal='sarapan'))
        
    except Exception as e:
        print(f"ERROR EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>", 500


@pso_bp.route("/<int:rec_num>/<meal>")
def rekomendasi_pso(rec_num, meal):
    """Tampilkan halaman rekomendasi PSO"""
    print(f"=== REKOMENDASI PSO DIPANGGIL ===")
    print(f"rec_num: {rec_num}, meal: {meal}")
    
    if 'user_data' not in session:
        print("ERROR: user_data tidak ada!")
        return redirect(url_for('input.input_data'))
    
    try:
        user_data = session['user_data']
        
        # Generate nutrisi dan hasil setiap kali halaman dibuka
        nutrisi, per_waktu = hitung_kebutuhan(
            user_data["jk"],
            user_data["bb"],
            user_data["tb"],
            user_data["usia"],
            user_data["aktivitas"]
        )
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        EXCEL_PATH = os.path.join(BASE_DIR, "resep.xlsx")
        
        # Generate hasil PSO
        print("Memulai optimasi PSO...")
        hasil = rekomendasi_menu_pso(EXCEL_PATH, nutrisi, n_particles=30, n_iterations=100)
        
        print(f"Hasil berhasil di-generate: {len(hasil)} kombinasi")
        
        return render_template(
            'pso_rekomendasi.html',
            user_data=user_data,
            nutrisi=nutrisi,
            hasil=hasil,
            rec_num=rec_num,
            current_meal=meal
        )
        
    except Exception as e:
        print(f"ERROR RENDER: {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Error Rendering</h1><pre>{traceback.format_exc()}</pre>", 500
```

---

## RINGKASAN PAGES

Total 6 files di folder `pages/`:

1. `__init__.py` - File kosong untuk package
2. `home.py` - 13 lines - Route `/`
3. `input.py` - 21 lines - Route `/input`
4. `metode.py` - 13 lines - Route `/metode`
5. `cbf_page.py` - 64 lines - Routes `/cbf/generate` dan `/cbf/<rec_num>/<meal>`
6. `pso_page.py` - 68 lines - Routes `/pso/generate` dan `/pso/<rec_num>/<meal>`

**Total: 179 lines of code**

## CATATAN PENTING

### Import Modules
Semua file pages yang menggunakan modules (cbf_page.py dan pso_page.py) menggunakan:

```python
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))
```

Ini memastikan bahwa modules bisa di-import dengan benar.

### Blueprint Naming
- `home_bp` → registered as 'home'
- `input_bp` → registered as 'input'
- `metode_bp` → registered as 'metode'
- `cbf_bp` → registered as 'cbf' with prefix '/cbf'
- `pso_bp` → registered as 'pso' with prefix '/pso'

### URL Redirects
- `url_for('input.input_data')` → `/input`
- `url_for('metode.pilih_metode')` → `/metode`
- `url_for('cbf.rekomendasi_cbf', rec_num=1, meal='sarapan')` → `/cbf/1/sarapan`
- `url_for('pso.rekomendasi_pso', rec_num=1, meal='sarapan')` → `/pso/1/sarapan`

### Session Management
Session `user_data` digunakan di:
- `input.py` - Menyimpan data form
- `metode.py` - Menampilkan nama user
- `cbf_page.py` - Generate rekomendasi CBF
- `pso_page.py` - Generate rekomendasi PSO

Session harus ada sebelum mengakses halaman metode/rekomendasi.

### Error Handling
Semua pages memiliki:
- Check session existence
- Try-catch untuk error handling
- Print statements untuk debugging
- Traceback display untuk development