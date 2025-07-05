#!/usr/bin/env python3
import mysql.connector

def stream_users():
    """Generator that yields rows one by one from the user_data table in MySQL."""
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mongolian5781',
        database='ALX_prodev'
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_data")
    
    for row in cursor:
        yield row

    cursor.close()
    conn.close()
