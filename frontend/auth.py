import streamlit as st
import sqlite3
import bcrypt


# Функция для инициализации БД (создаёт таблицу users, если её нет)
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash BLOB NOT NULL
            )
        ''')
        conn.commit()

# Функция регистрации пользователя
@st.cache_data
def register_user(username, password):
    if not username or not password:
        return False, "Логин и пароль не могут быть пустыми."
    
    try:
        with sqlite3.connect('users.db') as conn:
            if conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
                return False, "Пользователь с таким логином уже существует."
            
            # Хэширование пароля
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Сохранение в БД
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            return True, "Регистрация успешна! Теперь вы можете войти."
    except Exception as e:
        return False, f"Ошибка при регистрации: {str(e)}"
    
# Функция проверки входа
def check_credentials(username, password):
    try:
        with sqlite3.connect('users.db') as conn:
            result = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        
        if result:
            return bcrypt.checkpw(password.encode('utf-8'), result[0])
    except Exception as e:
        st.error(f"Ошибка при проверке: {str(e)}")
    return False