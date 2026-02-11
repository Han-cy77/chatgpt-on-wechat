import sqlite3
import os
import hashlib
import uuid
import json
import time

DB_FILE = os.path.join(os.path.dirname(__file__), 'web_chat.db')

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at REAL
    )''')
    # Sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    # Conversations table
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title TEXT,
        messages TEXT DEFAULT '[]',
        updated_at REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    conn.commit()
    conn.close()

# User functions
def register_user(username, password):
    conn = get_db()
    c = conn.cursor()
    try:
        salt = os.urandom(16).hex()
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        created_at = time.time()
        c.execute('INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)', 
                  (username, password_hash, salt, created_at))
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        salt = user['salt']
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        if password_hash == user['password_hash']:
            # Create session
            token = str(uuid.uuid4())
            expires_at = time.time() + 86400 * 7 # 7 days
            conn = get_db()
            # Clean old sessions for this user
            conn.execute('DELETE FROM sessions WHERE user_id = ?', (user['id'],))
            conn.execute('INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)', 
                         (token, user['id'], expires_at))
            conn.commit()
            conn.close()
            return token, user['username']
    return None, None

def get_user_by_token(token):
    if not token:
        return None
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT u.id, u.username FROM users u JOIN sessions s ON u.id = s.user_id WHERE s.token = ? AND s.expires_at > ?', 
              (token, time.time()))
    user = c.fetchone()
    conn.close()
    return user

def logout_user(token):
    conn = get_db()
    conn.execute('DELETE FROM sessions WHERE token = ?', (token,))
    conn.commit()
    conn.close()

# Conversation functions
def get_conversations(user_id, limit=20, offset=0, keyword=None, start_date=None, end_date=None):
    conn = get_db()
    c = conn.cursor()
    
    query = 'SELECT id, title, updated_at FROM conversations WHERE user_id = ?'
    params = [user_id]
    
    if keyword:
        query += ' AND title LIKE ?'
        params.append(f'%{keyword}%')
    
    if start_date:
        query += ' AND updated_at >= ?'
        params.append(start_date)
        
    if end_date:
        query += ' AND updated_at <= ?'
        params.append(end_date)
        
    query += ' ORDER BY updated_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_conversation_count(user_id, keyword=None, start_date=None, end_date=None):
    conn = get_db()
    c = conn.cursor()
    
    query = 'SELECT COUNT(*) FROM conversations WHERE user_id = ?'
    params = [user_id]
    
    if keyword:
        query += ' AND title LIKE ?'
        params.append(f'%{keyword}%')
    
    if start_date:
        query += ' AND updated_at >= ?'
        params.append(start_date)
        
    if end_date:
        query += ' AND updated_at <= ?'
        params.append(end_date)
        
    c.execute(query, params)
    count = c.fetchone()[0]
    conn.close()
    return count

def get_conversation(conversation_id, user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM conversations WHERE id = ? AND user_id = ?', (conversation_id, user_id))
    row = c.fetchone()
    conn.close()
    if row:
        res = dict(row)
        try:
            res['messages'] = json.loads(res['messages'])
        except:
            res['messages'] = []
        return res
    return None

def save_conversation(conversation_id, user_id, messages, title=None):
    conn = get_db()
    c = conn.cursor()
    
    # Check if exists
    c.execute('SELECT id FROM conversations WHERE id = ?', (conversation_id,))
    exists = c.fetchone()
    
    # Check ownership if exists
    if exists:
        c.execute('SELECT user_id FROM conversations WHERE id = ?', (conversation_id,))
        row = c.fetchone()
        if row and row['user_id'] != user_id:
            conn.close()
            return False # Not authorized
    
    messages_json = json.dumps(messages, ensure_ascii=False)
    now = time.time()
    
    if exists:
        if title:
            c.execute('UPDATE conversations SET messages = ?, title = ?, updated_at = ? WHERE id = ?',
                      (messages_json, title, now, conversation_id))
        else:
            c.execute('UPDATE conversations SET messages = ?, updated_at = ? WHERE id = ?',
                      (messages_json, now, conversation_id))
    else:
        if not title:
            title = "New Conversation"
        c.execute('INSERT INTO conversations (id, user_id, title, messages, updated_at) VALUES (?, ?, ?, ?, ?)',
                  (conversation_id, user_id, title, messages_json, now))
    conn.commit()
    conn.close()
    return True

def delete_conversation(conversation_id, user_id):
    conn = get_db()
    conn.execute('DELETE FROM conversations WHERE id = ? AND user_id = ?', (conversation_id, user_id))
    conn.commit()
    conn.close()
    
def clear_history(user_id):
    conn = get_db()
    conn.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()