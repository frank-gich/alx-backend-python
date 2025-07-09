import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        # Open the database connection
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        return self.cursor  # This is what you'll use inside the with-block

    def __exit__(self, exc_type, exc_value, traceback):
        # Commit if no exception, rollback if any exception
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        # Close the connection
        self.cursor.close()
        self.connection.close()


# === Example Usage ===
# For demonstration, we'll also create the 'users' table and insert data

# Setup test data (run once)
with DatabaseConnection('test.db') as cursor:
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))

# Query the data using the custom context manager
with DatabaseConnection('test.db') as cursor:
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    for row in results:
        print(row)
