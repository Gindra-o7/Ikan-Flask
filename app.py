import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from rapidfuzz import fuzz  # Untuk fuzzy matching

# Membaca data ikan dari CSV
df = pd.read_csv('data/ikan_air_tawar.csv')

app = Flask(__name__)
CORS(app)


def fuzzy_match_percentage(text, target):
    """
    Fungsi fuzzy matching menggunakan rapidfuzz untuk menghitung persentase kecocokan
    """
    text = str(text).lower()
    target = str(target).lower()
    return fuzz.partial_ratio(text, target)  # Cocokan sebagian teks dengan skor fuzzy


def match_fish_characteristics(description):
    """
    Mencocokkan karakteristik input dengan database ikan menggunakan fuzzy matching
    """
    results = []

    for _, row in df.iterrows():
        max_percentage = 0

        # Kolom-kolom yang akan dicek
        columns_to_check = ['Habitat', 'Ukuran', 'Bentuk Tubuh', 'Warna', 'Tingkah Laku', 'Nilai Ekonomis']

        # Periksa setiap kolom dan hitung persentase kecocokan
        for column in columns_to_check:
            percentage = fuzzy_match_percentage(description, str(row[column]))
            max_percentage = max(max_percentage, percentage)

        # Tambahkan ke hasil jika ada kecocokan di atas ambang batas (misal 50%)
        if max_percentage >= 50:
            results.append({
                'ikan': row['Ikan'],
                'persentase_kecocokan': round(max_percentage, 2),
                'detail': {
                    'Habitat': row['Habitat'],
                    'Ukuran': row['Ukuran'],
                    'Bentuk Tubuh': row['Bentuk Tubuh'],
                    'Warna': row['Warna'],
                    'Tingkah Laku': row['Tingkah Laku'],
                    'Nilai Ekonomis': row['Nilai Ekonomis']
                }
            })

    # Urutkan hasil berdasarkan persentase kecocokan secara menurun
    results.sort(key=lambda x: x['persentase_kecocokan'], reverse=True)
    return results


@app.route('/identify_fish', methods=['POST'])
def identify_fish():
    """
    Endpoint untuk identifikasi ikan berdasarkan deskripsi
    """
    input_data = request.json

    try:
        description = input_data.get('description', '')

        # Validasi input deskripsi
        if not description or len(description.strip()) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Deskripsi tidak boleh kosong.',
                'results': []
            }), 400

        # Jalankan pencocokan deskripsi
        results = match_fish_characteristics(description)

        # Jika tidak ada hasil
        if not results:
            return jsonify({
                'status': 'error',
                'message': 'Deskripsi tidak cocok dengan data ikan.',
                'results': []
            }), 404

        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Terjadi kesalahan.',
            'details': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
