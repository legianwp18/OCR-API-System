# OCR API System

Sistem OCR (Optical Character Recognition) dengan RESTful API untuk mengubah gambar menjadi teks yang dapat diedit. Sistem ini memungkinkan pengguna untuk mengunggah dokumen melalui API, mengubah gambar menjadi teks, dan mengembalikan hasilnya dalam format PDF.

## Persyaratan

- Python 3.11+
- Docker dan Docker Compose (untuk deployment dengan Docker)
- Tesseract OCR
- Poppler Utils

## Instalasi

### Menggunakan Docker (Direkomendasikan)

1. Clone repository ini:
   ```bash
   git clone https://github.com/legianwp18/OCR-API-System.git
   cd ocr-api
   ```

2. Bangun dan jalankan container dengan Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. API akan tersedia di `http://localhost:8080`

### Instalasi Manual

1. Instal prasyarat sistem:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-ind poppler-utils

   # MacOS
   brew install tesseract tesseract-lang poppler
   ```

2. Clone repository dan pindah ke direktori proyek:
   ```bash
   git clone https://github.com/legianwp18/OCR-API-System.git
   cd ocr-api
   ```

3. Buat dan aktifkan virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate     # Windows
   ```

4. Instal dependensi Python:
   ```bash
   pip install -r requirements.txt
   ```

5. Jalankan aplikasi:
   ```bash
   python app.py
   ```

## Penggunaan API

### Endpoint OCR

- **URL**: `/api/ocr`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

#### Parameter

| Nama | Tipe | Deskripsi |
|------|------|-----------|
| file | File | File yang akan diproses (PDF) |

#### Respons

File PDF hasil OCR yang berisi teks yang dapat diedit.

#### Kode Status

- 200 OK: Permintaan berhasil
- 400 Bad Request: Permintaan tidak valid (mis. tidak ada file atau format tidak didukung)
- 500 Internal Server Error: Terjadi kesalahan server

### Health Check

- **URL**: `/api/health`
- **Method**: `GET`

#### Respons

```json
{
  "status": "OK",
  "message": "OCR API is running"
}
```

## Contoh Penggunaan

### Dengan cURL

```bash
curl -X POST -F "file=@dokumen.pdf" http://localhost:8080/api/ocr -o hasil_ocr.pdf
```

### Dengan Python

```python
import requests

# Ganti dengan path file yang ada di sistem Anda
file_path = "/Users/sociolla/Documents/wiki/text_document.pdf"

headers = {'User-Agent': 'PythonClient/1.0'}

try:
    with open(file_path, "rb") as file:
        files = {
            "file": (file_path.split("/")[-1], file, "application/pdf")
        }

        response = requests.post(
            "http://127.0.0.1:8080/api/ocr",
            files=files,
            headers=headers
        )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        output_path = "hasil_ocr.pdf"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Hasil OCR berhasil disimpan ke {output_path}")
    else:
        print(f"Error: {response.status_code}")
        print("Response Headers:", response.headers)
        print("Response Body:", response.text)

except Exception as e:
    print(f"Terjadi kesalahan: {str(e)}")
```

### Dengan JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

async function processOCR(filePath) {
  // Validasi file
  if (!fs.existsSync(filePath)) {
    console.error(`Error: File '${filePath}' tidak ditemukan`);
    return;
  }
  
  console.log(`Memproses file: ${filePath}`);
  const fileName = path.basename(filePath);
  
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath), {
    filename: fileName,
    contentType: 'application/pdf'
  });
  
  try {
    console.log('Mengirim file ke API OCR...');
    const response = await axios.post('http://127.0.0.1:8080/api/ocr', form, {
      headers: {
        ...form.getHeaders(),
        'User-Agent': 'NodeJSClient/1.0'
      },
      responseType: 'arraybuffer'
    });
    
    console.log(`Status: ${response.status}`);
    
    if (response.status === 200) {
      const outputPath = 'hasil_ocr.pdf';
      fs.writeFileSync(outputPath, response.data);
      console.log(`Hasil OCR berhasil disimpan ke '${outputPath}'`);
    }
  } catch (error) {
    console.error('Error:', error.message);
    
    if (error.response) {
      console.error(`Status code: ${error.response.status}`);
      
      // Jika response berisi error dalam format JSON
      if (error.response.headers['content-type'] && 
          error.response.headers['content-type'].includes('application/json')) {
        try {
          const errorText = Buffer.from(error.response.data).toString('utf8');
          const errorJson = JSON.parse(errorText);
          console.error('Error detail:', errorJson.error || errorJson);
        } catch (parseError) {
          console.error('Response body:', Buffer.from(error.response.data).toString('utf8'));
        }
      } else {
        console.error('Response headers:', error.response.headers);
      }
    }
  }
}

// Ganti dengan path file PDF Anda
const filePath = "/Users/sociolla/Documents/wiki/text_document.pdf";
processOCR(filePath);
```

## Pemecahan Masalah

1. **Teks OCR tidak akurat**
   - Pastikan gambar memiliki resolusi tinggi dan teks yang jelas
   - Periksa apakah gambar tidak terlalu miring atau terdistorsi

2. **API tidak merespons**
   - Periksa apakah layanan berjalan: `docker-compose ps`
   - Periksa log container: `docker-compose logs ocr-api`

3. **Error: "No such file or directory"**
   - Pastikan direktori `uploads` dan `results` telah dibuat

## Kontribusi

Kontribusi selalu diterima! Silakan buat issue atau pull request untuk peningkatan atau perbaikan bug.

## Lisensi

[MIT License](LICENSE)
