import psycopg

from configure import host, user, password, db_name

def database(name, rating, comments):
    connection = None
    try:
        # Connect to the existing database
        connection = psycopg.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name  # Use dbname instead of db_name for psycopg
        )
        connection.autocommit = True

        # Create cursor 
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            print(f"Server version: {cursor.fetchone()}")

        # create a new Table 
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users_feedback(
                    id serial PRIMARY KEY, 
                    fullname varchar(64), 
                    rating INT CHECK (rating >= 1 AND rating <= 5),
                    suggestion TEXT
                    );
            """)

        print("INFO: Таблица была создана успешно!")   

        with connection.cursor() as cursor: 
            cursor.execute(""" 
            INSERT INTO users_feedback (fullname, rating, suggestion) VALUES (%s, %s, %s);
            """, (name, rating, comments))
    except Exception as _ex:
        print("INFO: Ошибка при работе с БД PostgreSQL")
        print(_ex)
    finally:
        if connection is not None:
            connection.close()
            print("INFO: PostgreSQL соединение закрыто")

def insert_input_data(user_name, x_value, y_value, x_name, y_name):
    connection = None
    try:
        # Connect to the existing database
        connection = psycopg.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name  # Use dbname instead of db_name for psycopg
        )
        connection.autocommit = True

        # Create cursor
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            print(f"Server version: {cursor.fetchone()}")

        # Create new table for input data
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS input_data(
                    id serial PRIMARY KEY,
                    user_name VARCHAR(25),
                    x_value FLOAT,
                    y_value FLOAT,
                    x_name VARCHAR(64),
                    y_name VARCHAR(64)
                );
            """)

        print("INFO: Таблица input_data была создана успешно!")

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

#if __name__ == '__main__':
#   database()
