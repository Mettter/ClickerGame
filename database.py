import os
import sqlite3

class PasswordDatabase:
    def __init__(self, dbname: str = "passwords.db") -> None:#None = returns nothing
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname)
        self.cursor = self.conn.cursor()
        print("PasswordDatabase opened DB:", os.path.abspath(self.dbname))
        self.init_table()

    def init_table(self) -> None:
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def get_users(self) -> list:
        self.cursor.execute("SELECT id, username, password FROM users")
        return self.cursor.fetchall()

    def insert_user(self, user: dict) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (user['username'], user['password'])
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_user(self, username: str) -> None:
        self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        self.conn.commit()

    def get_user_by_credentials(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

class UserDatabase:
    def __init__(self, dbname: str = "userdata.db") -> None:
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname)
        self.cursor = self.conn.cursor()
        print("UserDatabase opened DB:", os.path.abspath(self.dbname))
        self.init_table()

    def init_table(self) -> None:
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                moneyamount INTEGER NOT NULL DEFAULT 0
            )
        ''')
        self.conn.commit()

    def get_all_users(self) -> list:
        self.cursor.execute("SELECT username, moneyamount FROM users")
        rows = self.cursor.fetchall()
        print(f"Queried all users: {rows}")
        return rows

    def insert_user(self, username: str, coin_amount: int = 1) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO users (username, moneyamount) VALUES (?, ?)",
                (username, coin_amount)
            )
            self.conn.commit()
            print(f"Inserted user: {username} with {coin_amount} coins")
            # Immediately fetch all rows to verify
            self.cursor.execute("SELECT username, moneyamount FROM users")
            rows = self.cursor.fetchall()
            print(f"Users in DB after insert: {rows}")
            return True
        except sqlite3.IntegrityError:
            print(f"User already exists: {username}")
            return False

    def update_money(self, username: str, new_amount: int) -> None:
        self.cursor.execute(
            "UPDATE users SET moneyamount = ? WHERE username = ?",
            (new_amount, username)
        )
        self.conn.commit()

    def get_money_for_user(self, username: str) -> int:
        self.cursor.execute("SELECT moneyamount FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def add_moneyamount_column(self):
        try:
            self.cursor.execute("ALTER TABLE users ADD COLUMN moneyamount INTEGER DEFAULT 0")
            self.conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

    def add_user_and_money_column(self, username: str):
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (username, moneyamount) VALUES (?, ?)
        ''', (username, 1))  # Start with 1 coin
        self.conn.commit()

    def count_rows(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.cursor.fetchone()[0]
        print(f"Users table row count: {count}")
        return count