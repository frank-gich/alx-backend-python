#!/usr/bin/env python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator that yields batches of rows from the user_data table."""
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mongolian5781',
        database='ALX_prodev'
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_data")

    batch = []
    for row in cursor:  # <-- loop 1
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch

    cursor.close()
    conn.close()


def batch_processing(batch_size):
    """Processes batches, filters users over age 25, and prints them."""
    for batch in stream_users_in_batches(batch_size):  # <-- loop 2
        filtered = [user for user in batch if user[2] > 25]  # <-- loop 3 (list comp = a loop)
        for user in filtered:
            print(user)
