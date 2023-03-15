import psycopg2
from pprint import pprint


def create_db(cur):
    cur.execute("""
    DROP TABLE IF EXISTS clients, phonenumbers CASCADE;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id SERIAL PRIMARY KEY,
        name VARCHAR(50),
        surname VARCHAR(50),
        email VARCHAR(250)
        );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phonenumbers(
        number VARCHAR(11) PRIMARY KEY,
        client_id INTEGER REFERENCES clients(id)
        );
    """)
    return


def insert_client(cur, name=None, surname=None, email=None, phone=None):
    cur.execute("""
        INSERT INTO clients(name, surname, email)
        VALUES (%s, %s, %s)
        """, (name, surname, email))
    cur.execute("""
        SELECT id from clients
        ORDER BY id DESC
        LIMIT 1
        """)
    id = cur.fetchone()[0]
    if phone is None:
        return id
    else:
        insert_phone(cur, id, phone)
        return id


def insert_phone(cur, client_id, phone):
    cur.execute("""
        INSERT INTO phonenumbers(number, client_id)
        VALUES (%s, %s)
        """, (phone, client_id))
    return client_id


def update_client(cur, id, name=None, surname=None, email=None):
    cur.execute("""
        SELECT * from clients
        WHERE id = %s
        """, (id, ))
    info = cur.fetchone()
    if name is None:
        name = info[1]
    if surname is None:
        surname = info[2]
    if email is None:
        email = info[3]
    cur.execute("""
        UPDATE clients
        SET name = %s, surname = %s, email =%s 
        where id = %s
        """, (name, surname, email, id))
    return id


def delete_phone(cur, number):
    cur.execute("""
        DELETE FROM phonenumbers 
        WHERE number = %s
        """, (number, ))
    return number


def delete_client(cur, id):
    cur.execute("""
        DELETE FROM phonenumbers
        WHERE client_id = %s
        """, (id, ))
    cur.execute("""
        DELETE FROM clients 
        WHERE id = %s
       """, (id,))
    return id


def find_client(cur, name=None, surname=None, email=None, phone=None):
    if name is None:
        name = '%'
    else:
        name = '%' + name + '%'
    if surname is None:
        surname = '%'
    else:
        surname = '%' + surname + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if phone is None:
        cur.execute("""
            SELECT c.id, c.name, c.surname, c.email, p.number FROM clients c
            LEFT JOIN phonenumbers p ON c.id = p.client_id
            WHERE c.name LIKE %s AND c.surname LIKE %s
            AND c.email LIKE %s
            """, (name, surname, email))
    else:
        cur.execute("""
            SELECT c.id, c.name, c.surname, c.email, p.number FROM clients c
            LEFT JOIN phonenumbers p ON c.id = p.client_id
            WHERE c.name LIKE %s AND c.surname LIKE %s
            AND c.email LIKE %s AND p.number like %s
            """, (name, surname, email, phone))
    return cur.fetchall()


if __name__ == '__main__':
    with psycopg2.connect("dbname=clients_db user=postgres password=130816") as conn:
        with conn.cursor() as curs:
            # Cоздание таблиц
            create_db(curs)
            print("База данных создана")
            print()
            # Добавляем клиентов
            print("Добавлен клиент id: ",
                  insert_client(curs, "Михаил", "Савельев", "ms1975@mail.ru"))
            print("Добавлен клиент id: ",
                  insert_client(curs, "Андрей", "Поляков", "swinx@mail.ru", 79999999991))
            print("Добавлен клиент id: ",
                  insert_client(curs, "Виктор", "Пинюдин", "vitek@mail.ru", 79999999992))
            print("Добавлен клиент id: ",
                  insert_client(curs, "Иван", "Коренной", "korennoy86@mail.ru", 79999999993))
            print("Добавлена клиент id: ",
                  insert_client(curs, "Сергей", "Зюзин", "zuzin@mail.ru"))
            print()
            print("Данные в таблицах")
            curs.execute("""
                SELECT c.id, c.name, c.surname, c.email, p.number FROM clients c
                LEFT JOIN phonenumbers p ON c.id = p.client_id
                ORDER by c.id
                """)
            pprint(curs.fetchall())
            print()
            # Добавляем клиентам номера телефонов
            print("Телефон добавлен клиенту id: ",
                  insert_phone(curs, 2, 79999999994))
            print("Телефон добавлен клиенту id: ",
                  insert_phone(curs, 1, 79999999990))
            print("Телефон добавлен клиенту id: ",
                  insert_phone(curs, 5, 79999999999))
            print()
            print("Данные в таблицах")
            curs.execute("""
                SELECT c.id, c.name, c.surname, c.email, p.number FROM clients c
                LEFT JOIN phonenumbers p ON c.id = p.client_id
                ORDER by c.id
                """)
            pprint(curs.fetchall())
            print()
            # Изменяем данные клиента
            print("Изменены данные клиента id: ",
                  update_client(curs, 4, "Иван", None, 'korennoy1986@mail.ru'))
            print()
            # Удаляем номер телефона клиента
            print("Удален номер телефона: ",
                  delete_phone(curs, '79999999991'))
            print()
            print("Данные в таблицах")
            curs.execute("""
                SELECT c.id, c.name, c.surname, c.email, p.number FROM clients c
                LEFT JOIN phonenumbers p ON c.id = p.client_id
                ORDER by c.id
                """)
            pprint(curs.fetchall())
            print()
            # Удаляем клиента №2
            print("Удален клиент с id: ",
                  delete_client(curs, 2))
            curs.execute("""
                            SELECT c.id, c.name, c.surname, c.email, p.number FROM clients c
                            LEFT JOIN phonenumbers p ON c.id = p.client_id
                            ORDER by c.id
                            """)
            pprint(curs.fetchall())
            print()
            # Поиск клиента
            print('Найдены клиенты по имени:')
            pprint(find_client(curs, 'Виктор'))
            print('Найдены клиенты по email:')
            pprint(find_client(curs, None, None, 'zuzin@mail.ru'))
            print('Найденны клиенты по имени, фамилии и email:')
            pprint(find_client(curs, 'Михаил', 'Савельев', 'ms1975@mail.ru'))
            print('Найденны клиенты по имени, фамилии, телефону:')
            pprint(find_client(curs, None, 'Зюзин', None, '79999999999'))
            print('Найденны клиенты по имени, фамилии, телефону и email:')
            pprint(find_client(curs, 'Иван', 'Коренной', 'korennoy1986@mail.ru', '79999999993'))