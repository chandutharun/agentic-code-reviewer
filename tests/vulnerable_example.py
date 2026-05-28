import sqlite3

def get_user(user_id):
    # VULNERABLE: SQL injection
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchone()

def execute_code(code_string):
    # VULNERABLE: dangerous eval()
    result = eval(code_string)
    return result

def read_file(filename):
    # VULNERABLE: path traversal
    with open('/home/data/' + filename, 'r') as f:
        return f.read()
