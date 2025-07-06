import mysql.connector

def stream_users_in_batches(batch_size):
    """Yields batches of users from the database."""
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mongolian5781',
        database='ALX_prodev'
    )
    cursor = conn.cursor(dictionary=True)  # Use dict for column names

    cursor.execute("SELECT * FROM user_data")

    batch = []
    for row in cursor:
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

    cursor.close()
    conn.close()


def batch_processing(batch_size):
    """Prints users over age 25 from each batch."""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user.get('age', 0) > 25:  # Safer access
                print(user)  # ✅ Actually print the user
