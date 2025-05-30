# ✨ Delta Control Panel ✨

<p align="center">
  <img src="https://media.giphy.com/media/H83vGJf3F3T84zPzGI/giphy.gif" width="300px" alt="Delta Banner"/>
</p>

<p align="center"><b>Control panel modern untuk multi-autentikasi dan pengelolaan akun berbasis web</b></p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/github/languages/top/Kztutorial99/DeltaControlPanel?style=for-the-badge"/>
  <img src="https://img.shields.io/github/last-commit/Kztutorial99/DeltaControlPanel?style=for-the-badge"/>
</p>

---

## 🎯 Fitur Utama

- 🔐 Login OTP & Facebook Auth
- 📊 Admin Dashboard User
- 📦 Support Multi-Provider
- 💡 UI Template HTML + Flask Python
- 🔄 Struktur Modular

---

## 📦 Persiapan & Instalasi

```bash
git clone https://github.com/Kztutorial99/DeltaControlPanel.git
cd DeltaControlPanel

python3 -m venv venv
source venv/bin/activate  # Linux/MacOS
# atau
venv\Scripts\activate     # Windows

pip install -r requirements.txt

python app.py

Akses di browser: http://127.0.0.1:5000


---

🧠 Struktur Folder

📂 DeltaControlPanel/
├── app.py
├── auth.py
├── facebook_auth.py
├── otp_providers.py
├── models.py
├── routes.py
├── static/
├── templates/
└── requirements.txt


---

💻 Tampilan GUI

<p align="center">
  <img src="https://user-images.githubusercontent.com/10236644/176915460-0fcf2d60-c96d-4e1b-b6cd-31dba3769cc4.gif" width="70%">
  <br>
  <i>Tampilan web panel yang elegan & mudah digunakan</i>
</p>
---

📘 Cara Menggunakan

1. Login via OTP atau Facebook


2. Kelola akun user di dashboard


3. Update atau hapus pengguna


4. Customisasi UI di folder templates/


5. Gunakan models.py untuk ubah struktur database




---

🛡️ Keamanan

Tidak menyimpan password secara plaintext

Validasi form & input

Proteksi CSRF (jika diaktifkan)



---

🙏 Terima Kasih

Dikembangkan dengan ❤️ oleh Kztutorial99

<p align="center">
  <img src="https://media.giphy.com/media/26gscSULUcfKU7dWU/giphy.gif" width="180px"/>
  <br><b>Delta Control Panel — Smart, Secure & Simple</b>
</p>EOF

> 💡 Jalankan script di atas di terminal Anda (bash/Termux) untuk membuat langsung `README.md` dengan isi VIP dan animasi. Jika Anda ingin menambahkan link custom atau badge tambahan, tinggal ganti bagian di atas.
