Web Security Lab: Vulnerable vs Patched Flask App
Laboratorium praktis menggunakan Python Flask untuk mensimulasikan celah keamanan web dasar dan cara memperbaikinya pada sisi Web (HTML) maupun API (JSON).

Arsitektur Aplikasi
app_vulnerable.py (Port 5000): Mengandung beberapa kerentanan web dasar seperti SQL Injection (Bypass Login) dan Mass Assignment (Eksploitasi Hak Akses Admin).

app_patched.py (Port 5002): Versi yang telah mengamankan kerentanan pada app_vulnerable.py.

Cara Menjalankan
Instalasi Pustaka:
pip install flask pyjwt werkzeug flask-limiter

Jalankan Lab Rentan:
python app_vulnerable.py
Akses lewat: http://127.0.0.1:5000/register

Jalankan Lab Aman:
python app_patched.py
Akses lewat: http://127.0.0.1:5002/register
