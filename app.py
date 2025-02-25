from flask import Flask, request, jsonify, send_file
import time
import uuid
import fitz
from PIL import Image
import os
import pytesseract
import logging
import base64

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

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

        with open(result_pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        return jsonify({
            'success': True,
            'filename': f"{filename}_result.pdf",
            'data': pdf_base64,
            'content_type': 'application/pdf'
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500


def create_pdf_with_reportlab(text_pages, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)

    for page_text in text_pages:
        y = 750
        lines = page_text.split('\n')

        for line in lines:
            if line.strip():
                try:
                    c.drawString(50, y, line)
                except:
                    safe_line = ''.join(ch if ord(ch) < 128 else ' ' for ch in line)
                    c.drawString(50, y, safe_line)

                y -= 15

                if y < 50:
                    c.showPage()
                    y = 750

        c.showPage()

    c.save()

def process_pdf(pdf_path, output_path):
    logger.info(f"Memproses PDF: {pdf_path}")

    pdf_document = fitz.open(pdf_path)

    all_text = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)

        text_from_pdf = page.get_text()

        text_length = len(text_from_pdf.strip())

        # Jika halaman memiliki cukup teks (bukan gambar), gunakan teks tersebut
        if text_length > 50:  # Ambang batas karakter yang dapat disesuaikan
            logger.info(f"Halaman {page_num + 1} sudah berisi teks ({text_length} karakter), tidak perlu OCR")
            processed_text = text_from_pdf
        else:
            # Halaman berisi sedikit atau tanpa teks, lakukan OCR
            logger.info(f"Halaman {page_num + 1} mungkin berisi gambar (hanya {text_length} karakter), melakukan OCR")

            # Konversi halaman ke gambar
            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))

            # Lakukan OCR
            processed_text = pytesseract.image_to_string(img, lang='eng+ind')
            logger.info(f"OCR selesai untuk halaman {page_num + 1}")

        # Simpan teks dari halaman ini
        all_text.append(processed_text)

    pdf_document.close()

    create_pdf_with_reportlab(all_text, output_path)
    logger.info(f"PDF hasil OCR disimpan di {output_path}")

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