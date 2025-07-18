#!/usr/bin/env python3
from seed import connect_to_prodev

def paginate_users(page_size, offset):
    """Fetches a page of users starting at a specific offset."""
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """Generator that lazily paginates user data, one page at a time."""
    offset = 0
    while True:  # <-- This is the single loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
