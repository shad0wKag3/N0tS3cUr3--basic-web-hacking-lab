import sqlite3
import hashlib

def init_db():
    # Membuka koneksi ke file database SQLite bernama n0ts3cur3.db
    conn = sqlite3.connect('n0ts3cur3.db')
    cursor = conn.cursor()
    
    # Membuat tabel users jika belum ada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Membuat tabel notes jika belum ada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Menghapus data lama saat inisialisasi ulang agar database bersih untuk testing
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM notes")
    
    # Membuat password bawaan menggunakan MD5 yang lemah
    admin_md5 = hashlib.md5("admin123".encode()).hexdigest()
    user_md5 = hashlib.md5("user123".encode()).hexdigest()
    
    # Memasukkan data user contoh awal ke dalam tabel users
    cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ("admin", admin_md5, 1))
    cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ("user_biasa", user_md5, 0))
    
    # Memasukkan data catatan contoh awal milik admin (user_id = 1) dan user biasa (user_id = 2)
    cursor.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (1, "Rahasia Admin", "Kunci server utama adalah xyz"))
    cursor.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (2, "Belanjaan", "Beli susu dan kopi hitam"))
    
    # Menyimpan perubahan dan menutup database
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database n0ts3cur3.db berhasil dibuat dan diisi data contoh!")