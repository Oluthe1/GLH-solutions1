import sqlite3


def get_db_connection():
    conn=sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
"""
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            phonenumber TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            firstname TEXT,
            lastname TEXT,
            phonenumber TEXT,
            birthday DATETIME,
            county TEXT,
            password TEXT
    )''')
    conn.commit()
    conn.close()
"""

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_item(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            descr TEXT,
            price REAL NOT NULL,
            img TEXT UNIQUE
            )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_item(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          product_id INTEGER,
          FOREIGN KEY (product_id) REFERENCES product_item (id)
            )
    """)



    
    conn.commit()
    conn.close()


    print("success!")


