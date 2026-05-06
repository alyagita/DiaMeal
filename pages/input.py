from flask import Blueprint, render_template, request, redirect, url_for, session

input_bp = Blueprint('input', __name__)

@input_bp.route("/input", methods=["GET", "POST"])
def input_data():
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

print("[Input Blueprint] Loaded")
