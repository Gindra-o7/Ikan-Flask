import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

# Membaca data ikan dari CSV
df = pd.read_csv('data/ikan_air_tawar.csv')

app = Flask(__name__)
CORS(app)


def text_match_percentage(text, target):
    """
    Fungsi pencocokan teks dengan persentase kecocokan
    """
    text = str(text).lower()
    target = str(target).lower()

    # Tokenisasi kata (memecah kalimat menjadi kata)
    text_words = set(re.findall(r'\w+', text))
    target_words = set(re.findall(r'\w+', target))

    # Hitung jumlah kata yang cocok
    match_words = text_words.intersection(target_words)

    if not text_words:  # Hindari pembagian dengan nol
        return 0

    # Hitung persentase kecocokan
    return len(match_words) / len(text_words) * 100


def match_fish_characteristics(description):
    """
    Mencocokkan karakteristik input dengan database ikan
    """
    results = []

    for _, row in df.iterrows():
        max_percentage = 0

        # Kolom-kolom yang akan dicek
        columns_to_check = ['Habitat', 'Ukuran', 'Bentuk Tubuh', 'Warna', 'Tingkah Laku', 'Nilai Ekonomis']

        # Periksa setiap kolom dan hitung persentase kecocokan
        for column in columns_to_check:
            percentage = text_match_percentage(description, str(row[column]))
            max_percentage = max(max_percentage, percentage)

        # Tambahkan ke hasil jika ada kecocokan
        if max_percentage > 0:
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

        # Jalankan pencocokan deskripsi
        results = match_fish_characteristics(description)

        # Jika tidak ada hasil
        if not results:
            return jsonify({
                'status': 'error',
                'message': 'Deskripsi tidak cocok dengan data ikan.',
                'results': []
            }), 400

        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Terjadi kesalahan.',
            'details': str(e)
        }), 400


if __name__ == '__main__':
    app.run(debug=True)
