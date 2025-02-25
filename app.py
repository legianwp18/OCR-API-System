from flask import Flask, request, jsonify, send_file
import time
import uuid
import fitz
from PIL import Image
import io
import os
import pytesseract
from fpdf import FPDF
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route('/api/ocr', methods=['POST'])
def ocr_process():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang dikirim'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Tidak ada file yang dipilih'}), 400

        allowed_extensions = {'pdf'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Format file tidak didukung. Gunakan PDF'}), 400

        process_id = str(uuid.uuid4())
        timestamp = int(time.time())
        filename = f"{timestamp}_{process_id}"

        file_path = os.path.join(UPLOAD_FOLDER, f"{filename}.{file_ext}")
        file.save(file_path)
        logger.info(f"File disimpan di {file_path}")

        result_pdf_path = os.path.join(RESULT_FOLDER, f"{filename}_result.pdf")

        process_pdf(file_path, result_pdf_path)

        return send_file(result_pdf_path, as_attachment=True, download_name='ocr_result.pdf')

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500


def process_pdf(pdf_path, output_path):
    logger.info(f"Memproses PDF: {pdf_path}")

    pdf_document = fitz.open(pdf_path)

    output_pdf = FPDF()

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text_from_pdf = page.get_text()
        text_length = len(text_from_pdf.strip())

        if text_length > 50:  # Ambang batas karakter yang dapat disesuaikan
            logger.info(f"Halaman {page_num + 1} sudah berisi teks ({text_length} karakter), tidak perlu OCR")
            processed_text = text_from_pdf
        else:
            logger.info(f"Halaman {page_num + 1} mungkin berisi gambar (hanya {text_length} karakter), melakukan OCR")

            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))

            processed_text = pytesseract.image_to_string(img, lang='eng+ind')
            logger.info(f"OCR selesai untuk halaman {page_num + 1}")

        processed_text = clean_text(processed_text)

        add_text_to_pdf(output_pdf, processed_text)

    pdf_document.close()

    output_pdf.output(output_path)
    logger.info(f"PDF hasil OCR disimpan di {output_path}")


def clean_text(text):
    """Bersihkan teks dari karakter yang tidak didukung oleh FPDF"""
    # Ganti karakter Unicode dengan alternatif ASCII sederhana
    text = text.replace('\u2019', "'")  # Apostrof kurva
    text = text.replace('\u201c', '"')  # Tanda kutip kurva kiri
    text = text.replace('\u201d', '"')  # Tanda kutip kurva kanan
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '--')  # Em dash
    text = text.replace('\u2022', '*')  # Bullet
    text = text.replace('\u2026', '...')  # Ellipsis
    text = text.replace('\u00a0', ' ')  # Non-breaking space
    return text


def add_text_to_pdf(pdf, text):
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    lines = text.split('\n')
    for line in lines:
        if line.strip():
            try:
                pdf.multi_cell(0, 10, line)
            except UnicodeEncodeError:
                safe_line = ''.join(c if ord(c) < 128 else ' ' for c in line)
                pdf.multi_cell(0, 10, safe_line)


@app.route('/api/health', methods=['GET'])
def health_check():
    logger.info(f"OCR API is running")
    return jsonify({'status': 'OK', 'message': 'OCR API is running'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)