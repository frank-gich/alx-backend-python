#!/usr/bin/env python3
from seed import connect_to_prodev

def stream_user_ages():
    """Generator that yields user ages one by one from the database."""
    conn = connect_to_prodev()
    cursor = conn.cursor()
    cursor.execute("SELECT age FROM user_data")

    for (age,) in cursor:  # <-- Loop 1
        yield age

    cursor.close()
    conn.close()


def compute_average_age():
    """Computes and prints the average age using a generator (memory-efficient)."""
    total_age = 0
    count = 0

    for age in stream_user_ages():  # <-- Loop 2
        total_age += age
        count += 1

    if count == 0:
        print("No users found.")
    else:
        average = total_age / count
        print(f"Average age of users: {average:.2f}")
