import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.connection = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        # Open database connection
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        # Execute the query with parameters
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results  # Return the result to the with-block

    def __exit__(self, exc_type, exc_value, traceback):
        # Rollback if there's an exception, otherwise commit
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        # Close the cursor and connection
        self.cursor.close()
        self.connection.close()
# Setup example database and table (run once)
with sqlite3.connect('test.db') as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    cursor.executemany("INSERT INTO users (name, age) VALUES (?, ?)", [
        ("Alice", 22),
        ("Bob", 30),
        ("Charlie", 28)
    ])
    conn.commit()

# Use the ExecuteQuery context manager
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

with ExecuteQuery('test.db', query, params) as results:
    for row in results:
        print(row)
