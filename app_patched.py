from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
import sqlite3, jwt, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
SECRET_KEY = "kunci_rahasia_yang_sangat_panjang_dan_aman_sekali"
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

def query_db(query, args=(), one=False, commit=False):
    with sqlite3.connect('n0ts3cur3.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        if commit: conn.commit()
        return (cur.fetchone() if one else cur.fetchall())

def get_session_user():
    token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    try: return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except: return None

@app.route('/api/register', methods=['POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    is_api = request.path.startswith('/api/')
    if request.method == 'POST':
        data = request.get_json() if is_api else request.form
        p_hash = generate_password_hash(data['password'])
        try:
            query_db("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)", (data['username'], p_hash), commit=True)
            if is_api:
                return jsonify({"message": "Sukses"}), 201
            else:
                return redirect(url_for('login'))
        except:
            if is_api:
                return jsonify({"error": "Gagal"}), 400
            else:
                return "Registrasi Gagal"
            
    return render_template('register.html')

@app.route('/api/login', methods=['POST'])
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Aman dari brute force
def login():
    is_api = request.path.startswith('/api/')
    if request.method == 'POST':
        data = request.get_json() if is_api else request.form
        
        # Aman dari SQL Injection karena menggunakan Parameterized Query (?)
        user = query_db("SELECT * FROM users WHERE username = ?", (data.get('username',''),), one=True)
        
        if user and check_password_hash(user['password'], data.get('password','')):
            token = jwt.encode({"user_id": user['id'], "username": user['username'], "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")
            
            if is_api:
                return jsonify({"message": "Sukses", "token": token}), 200
            else:
                res = make_response(redirect(url_for('dashboard')))
                res.set_cookie('token', token, httponly=True, secure=False, samesite='Lax')
                return res
                
        return jsonify({"error": "Kredensial Salah"}), 401 if is_api else "Login Gagal"
        
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = get_session_user()
    if not user: return redirect(url_for('login'))
    
    if request.method == 'POST':
        query_db("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (user['user_id'], request.form['title'], request.form['content']), commit=True)
    
    # Aman dari XSS karena data dikirim biasa ke dashboard.html (Aman karena setingan secure_mode=True di HTML)
    return render_template('dashboard.html', notes=query_db("SELECT * FROM notes WHERE user_id = ?", (user['user_id'],)), username=user['username'], secure_mode=True)

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def api_get_note(note_id):
    user = get_session_user()
    if not user: return jsonify({"error": "Akses ditolak"}), 401
    
    # Aman dari IDOR karena database mencocokkan ID note dengan ID user yang sedang aktif
    note = query_db("SELECT * FROM notes WHERE id = ? AND user_id = ?", (note_id, user['user_id']), one=True)
    return jsonify({"id": note['id'], "title": note['title'], "content": note['content']}) if note else (jsonify({"error": "Tidak ditemukan"}), 404)

@app.route('/logout')
def logout():
    res = make_response(redirect(url_for('login')))
    res.delete_cookie('token')
    return res

if __name__ == '__main__':
    app.run(debug=True, port=5002)