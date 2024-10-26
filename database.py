import sqlite3
from contextlib import contextmanager
import json

DATABASE = "my_database.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
        conn.commit()  # Ensure changes are committed
    except Exception as e:
        print(f"An error occurred: {e}")  # Optional: Print error for debugging
        conn.rollback()  # Roll back any changes on error
    finally:
        conn.close()


def create_table():
    with get_connection() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                spreadsheet_id TEXT NOT NULL,
                spreadsheet_name TEXT NOT NULL,
                template_data TEXT NOT NULL
            )
        """
        )


def insert_user(name, email, spreadsheet_id, spreadsheet_name, template_data):
    with get_connection() as con:
        try:
            con.execute(
                "INSERT INTO Users (name, email, spreadsheet_id, spreadsheet_name ,template_data) VALUES (?, ?, ?,?,?)",
                (name, email, spreadsheet_id, spreadsheet_name, template_data),
            )
            return "User inserted successfully."
        except sqlite3.IntegrityError:
            return "Error: A user with this email already exists."


def read_users():
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Users")
        return cursor.fetchall()


def delete_user(email):
    with get_connection() as con:
        con.execute("DELETE FROM Users WHERE email = ?", (email,))
        return "User deleted successfully."


def find_user_by_email(email):
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
        return cursor.fetchone()  # This will return a single row or None if not found


def update_template_data(email, template_data):
    # Convert the list of dictionaries to a JSON string
    template_data = json.dumps(template_data)
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute(
            "UPDATE Users SET template_data = ? WHERE email = ?", (template_data, email)
        )
        if cursor.rowcount == 0:
            return "No user found with this email."
    return "Template updated successfully."


def update_spreadsheet_id(email, spreadsheet_id, spreadsheet_name):
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute(
            "UPDATE Users SET spreadsheet_id = ?, spreadsheet_name = ? WHERE email = ?",
            (spreadsheet_id, spreadsheet_name, email),
        )
        if cursor.rowcount == 0:
            return "No user found with this email."
    return "Spreadsheet ID and name updated successfully."
