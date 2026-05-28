import sqlite3
from typing import Tuple

def get_user(user_id: int) -> Tuple:
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()

def execute_code(code_string: str) -> any:
    try:
        result = eval(code_string)
        return result
    except Exception as e:
        raise ValueError(f"Invalid code: {e}")

def read_file(filename: str) -> str:
    import os
    filename = os.path.join('/home/data/', filename)
    with open(filename, 'r') as f:
        return f.read()

if __name__ == "__main__":
    user_id = 1
    print(get_user(user_id))

    code_string = "print('Hello World')"
    try:
        result = execute_code(code_string)
        print(result)
    except ValueError as e:
        print(e)

    filename = 'example.txt'
    content = read_file(filename)
    print(content)