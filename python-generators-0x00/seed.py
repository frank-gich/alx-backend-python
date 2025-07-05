# seed.py
import mysql.connector
import csv

def connect_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mongolian5781',
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Connection error: {err}")
        return None

def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Create DB error: {err}")

def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mongolian5781',
            database='ALX_prodev'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Connection to ALX_prodev failed: {err}")
        return None

def create_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL,
                INDEX(user_id)
            );
        """)
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Create table error: {err}")

import csv
import uuid

def insert_data(connection, data):
    try:
        cursor = connection.cursor()
        with open(data, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = str(uuid.uuid4())  # Generate a random UUID
                cursor.execute("""
                    INSERT IGNORE INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s);
                """, (user_id, row['name'], row['email'], row['age']))
        connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Insertion error: {e}")
