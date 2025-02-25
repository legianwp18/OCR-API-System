import requests

# Ganti dengan path file yang ada di sistem Anda
file_path = "/Users/sociolla/Documents/wiki/text_document.pdf"

# Headers tambahan yang mungkin diperlukan
headers = {
    'User-Agent': 'PythonClient/1.0'
}

try:
    with open(file_path, "rb") as file:
        files = {
            "file": (file_path.split("/")[-1], file, "application/pdf")
        }

        print("Mengirim file ke API...")
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