# Halaman pemilihan metode rekomendasi

from flask import Blueprint, render_template, redirect, url_for, session

metode_bp = Blueprint('metode', __name__)


@metode_bp.route("/metode")
def pilih_metode():
    # Halaman pemilihan metode CBF atau PSO
    if 'user_data' not in session:
        return redirect(url_for('input.input_data'))
    return render_template('metode.html', user_data=session['user_data'])