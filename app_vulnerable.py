from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3, hashlib, jwt, datetime

app = Flask(__name__)
SECRET_KEY = "super_secret_key"

def query_db(query, args=(), one=False):
    with sqlite3.connect('n0ts3cur3.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

@app.route('/api/register', methods=['POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Menyatukan registrasi Web & API. Deteksi berdasarkan jenis request (JSON atau Form)
    is_api = request.path.startswith('/api/')
    data = request.get_json() if is_api else request.form
    
    if request.method == 'POST':
        p_hash = hashlib.md5(data['password'].encode()).hexdigest()
        # Rentan Mass assignment karena mengambil is_admin langsung dari input
        is_admin = data.get('is_admin', 0)
        try:
            query_db("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (data['username'], p_hash, is_admin))
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
def login():
    is_api = request.path.startswith('/api/')
    if request.method == 'POST':
        data = request.get_json() if is_api else request.form
        p_hash = hashlib.md5(data.get('password', '').encode()).hexdigest()
        
        # Rentan SQL Injection karena string input user langsung digabungkan ke query
        query = f"SELECT * FROM users WHERE username = '{data.get('username','')}' AND password = '{p_hash}'"
        user = query_db(query, one=True)
        
        if user:
            token = jwt.encode({"user_id": user['id'], "username": user['username'], "is_admin": user['is_admin'], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
            
            if is_api:
                return jsonify({"token": token}), 200
            else:
                return redirect(url_for('dashboard', token=token))
                
        return jsonify({"error": "Salah"}), 401 if is_api else "Login Gagal"
    
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    token = request.args.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return render_template('dashboard.html', notes=[], username="Guest", token="")

    if request.method == 'POST':
        query_db("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (decoded['user_id'], request.form['title'], request.form['content']))
    
    # Rentan XSS karena data diberikan apa adanya ke template dashboard
    return render_template('dashboard.html', notes=query_db("SELECT * FROM notes WHERE user_id = ?", (decoded['user_id'],)), username=decoded['username'], token=token)

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def api_get_note(note_id):
    # Rentan IDOR karena hanya mengecek ID catatan tanpa memvalidasi siapa pemiliknya
    note = query_db("SELECT * FROM notes WHERE id = ?", (note_id,), one=True)
    return jsonify({"id": note['id'], "title": note['title'], "content": note['content']}) if note else (jsonify({"error": "Tidak ditemukan"}), 404)

@app.route('/logout')
def logout(): return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)