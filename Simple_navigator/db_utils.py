from hash_func import *
import pyodbc

# Функция для подключения к базе данных
def connect_to_database(db_path):
    connection_string = (
        f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
        f"DBQ={db_path};"
    )
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

def history_save_db(conn, UserID, RouteDetails):
    cursor = conn.cursor()
    try:
        query_insert = "INSERT INTO TripsHistory (UserID, RouteDetails) VALUES (?, ?)"
        cursor.execute(query_insert, UserID, RouteDetails)
        conn.commit()
        print("В истории успешно записано")
    except pyodbc.Error as e:
        conn.rollback()
        return None

def register_user(conn, username, password):
    cursor = conn.cursor()
    hashed_password = hash_password(password) # вызываем функцию хэширования из файла hash_func.py

    # Проверяем, существует ли пользователь с таким именем
    try:
        query_check = "SELECT UserID FROM Users WHERE Username = ?"
        cursor.execute(query_check, (username,))
        user = cursor.fetchone()
        if user:
            print("Пользователь с таким именем уже существует.")
            return None
    except pyodbc.Error as e:
      print(f"Ошибка при проверке пользователя: {e}")
      return None


    # Добавляем нового пользователя в базу данных
    try:
        query_insert = "INSERT INTO Users (Username, Password) VALUES (?, ?)"
        cursor.execute(query_insert, (username, hashed_password))
        conn.commit()
        print("Регистрация успешна!")
    except pyodbc.Error as e:
        print(f"Ошибка при регистрации пользователя: {e}")
        conn.rollback()
        return None

    # Получаем ID нового пользователя
    try:
      query_get_id = "SELECT UserID FROM Users WHERE Username = ?"
      cursor.execute(query_get_id, (username,))
      user_id = cursor.fetchone()[0]
      return user_id
    except (pyodbc.Error, TypeError) as e:
      print(f"Ошибка при получении ID пользователя: {e}")
      return None

def login_user(conn, username, password):
    cursor = conn.cursor()
    # Получаем хэш пароля из базы данных
    query = "SELECT UserID, Password FROM Users WHERE Username = ?"
    cursor.execute(query, (username,))
    user_data = cursor.fetchone()

    if user_data:
        user_id, stored_hashed_password = user_data

        # Проверяем пароль с помощью verify_password
        if verify_password(password, stored_hashed_password): # вызываем функцию из hash_func.py
            print("Авторизация успешна!")
            return user_id
        else:
            print("Неверный пароль.")
            return None
    else:
        print("Неверное имя пользователя.")
        return None

# Функция для проверки существования города
def check_city_exists(conn, city_name):
    cursor = conn.cursor()
    query = "SELECT CityID FROM Cities WHERE CityName = ?"
    cursor.execute(query, (city_name,))
    return cursor.fetchone()

# Функция для получения имени города по ID
def get_city_name(conn, city_id):
    cursor = conn.cursor()
    query = "SELECT CityName FROM Cities WHERE CityID = ?"
    cursor.execute(query, (city_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# Функция для получения названия типа объекта по ID
def get_object_type_name(conn, object_type_id):
    cursor = conn.cursor()
    query = "SELECT ObjectTypeName FROM ObjectTypes WHERE ObjectTypeID = ?"
    cursor.execute(query, (object_type_id,))
    result = cursor.fetchone()
    return result[0] if result else None