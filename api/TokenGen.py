import secrets
from django.db import connection

def generate_token():
    token = secrets.token_hex(32 // 2)
    
    if not token_exists_in_database(token):
        return token

def token_exists_in_database(token):
    try:
        with connection.cursor() as cursor:
            # Use parameterized query to prevent SQL injection
            query = "SELECT * FROM users WHERE Token = %s;"
            cursor.execute(query, [token])
            result = cursor.fetchall()
        return bool(result)
            
    except Exception as e:
        return True