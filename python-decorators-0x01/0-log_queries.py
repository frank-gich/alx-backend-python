import sqlite3
import functools

# Decorator to log SQL queries
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Wrap sqlite3's cursor.execute to log queries
        original_connect = sqlite3.connect

        def custom_connect(*cargs, **ckwargs):
            conn = original_connect(*cargs, **ckwargs)
            original_cursor = conn.cursor

            def custom_cursor(*cuargs, **cukwargs):
                cursor = original_cursor(*cuargs, **cukwargs)
                original_execute = cursor.execute

                def logged_execute(query, *qargs, **qkwargs):
                    print(f"[LOG] Executing SQL Query: {query}")
                    return original_execute(query, *qargs, **qkwargs)

                cursor.execute = logged_execute
                return cursor

            conn.cursor = custom_cursor
            return conn

        sqlite3.connect = custom_connect
        try:
            return func(*args, **kwargs)
        finally:
            # Restore the original connect method
            sqlite3.connect = original_connect

    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
