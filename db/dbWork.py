import psycopg
from configure import host, user, password, db_name

def create_tables():
    connection = None
    try:
        connection = psycopg.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            print(f"Server version: {cursor.fetchone()}")

        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users_feedback(
                    id SERIAL PRIMARY KEY, 
                    fullname VARCHAR(64), 
                    rating INT CHECK (rating >= 1 AND rating <= 5),
                    suggestion TEXT
                );
            """)
            print("INFO: Таблица users_feedback была создана успешно!")   

        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS input_data(
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(64),
                    x_value FLOAT,
                    y_value FLOAT,
                    x_name VARCHAR(64),
                    y_name VARCHAR(64)
                );
            """)
            print("INFO: Таблица input_data была создана успешно!")

    except Exception as _ex:
        print("INFO: Ошибка при работе с БД PostgreSQL")
        print(_ex)
    finally:
        if connection is not None:
            connection.close()
            print("INFO: PostgreSQL соединение закрыто")

def insert_user_feedback(name, rating, comments):
    connection = None
    user_id = None
    try:
        connection = psycopg.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users_feedback (fullname, rating, suggestion) VALUES (%s, %s, %s) RETURNING id;
            """, (name, rating, comments))
            user_id = cursor.fetchone()[0]
            print(f"INFO: Данные были успешно добавлены в таблицу users_feedback! User ID: {user_id}")
        
    except Exception as _ex:
        print("INFO: Ошибка при работе с БД PostgreSQL")
        print(_ex)
    finally:
        if connection is not None:
            connection.close()
            print("INFO: PostgreSQL соединение закрыто")
    return user_id

def insert_input_data(user_name, x_value, y_value, x_name, y_name):
    connection = None
    try:
        connection = psycopg.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO input_data (user_name, x_value, y_value, x_name, y_name) VALUES (%s, %s, %s, %s, %s);
            """, (user_name, x_value, y_value, x_name, y_name))
            print("INFO: Данные были успешно добавлены в таблицу input_data!")

    except Exception as _ex:
        print("INFO: Ошибка при работе с БД PostgreSQL")
        print(_ex)
    finally:
        if connection is not None:
            connection.close()
            print("INFO: PostgreSQL соединение закрыто")

# Создаем таблицы
create_tables()

# Вставляем данные и связываем таблицы
# user_id = insert_user_feedback('John Doe', 5, 'Great service!')
# if user_id:
#     insert_input_data(user_id, 12.34, 56.78, 'Time', 'Value')
