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
                CREATE TABLE IF NOT EXISTS users(
                    id serial PRIMARY KEY, 
                    fullname varchar(64), 
                    rating INT CHECK (rating >= 1 AND rating <= 5),
                    suggestion TEXT
                    );
            """)

        print("INFO: Таблица была создана успешно!")   

        with connection.cursor() as cursor: 
            cursor.execute(""" 
            INSERT INTO users (fullname, rating, suggestion) VALUES (%s, %s, %s);
            """, (name, rating, comments))
    except Exception as _ex:
        print("INFO: Ошибка при работе с БД PostgreSQL")
        print(_ex)
    finally:
        if connection is not None:
            connection.close()
            print("INFO: PostgreSQL соединение закрыто")


if __name__ == '__main__':
    database()
