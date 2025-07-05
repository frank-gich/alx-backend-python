#!/usr/bin/env python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator that yields batches of users from the database."""
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mongolian5781',
        database='ALX_prodev'
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_data")

    batch = []
    for row in cursor:  # Loop 1
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

    cursor.close()
    conn.close()


def batch_processing(batch_size):
    """Generator that yields users over age 25 from each batch."""
    for batch in stream_users_in_batches(batch_size):  # Loop 2
        for user in batch:  # Loop 3
            if user[2] > 25:  # assuming age is the 3rd column
                yield user  # ✅ using yield, not return
