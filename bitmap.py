import psycopg2
from psycopg2 import sql

# Replace these with your actual database connection parameters
dbname = 'your_database'
user = 'your_user'
password = 'your_password'
host = 'your_host'
port = 'your_port'

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cursor = conn.cursor()

bitmap_dict = {}

unique_values_query = 'SELECT DISTINCT supplier_id FROM suppliers'
cursor.execute(unique_values_query)
unique_values = [row[0] for row in cursor.fetchall()]

for value in unique_values:
    bitmap = 0
    rows_with_value_query = f'SELECT supplier_id FROM suppliers WHERE supplier_id = {value}'
    cursor.execute(rows_with_value_query)
    rows_with_value = [row[0] for row in cursor.fetchall()]

    for row_id in rows_with_value:
        bitmap |= (1 << row_id)

    bitmap_dict[value] = int(bitmap/2)

for value, bitmap in bitmap_dict.items():
    print(f"Value: {value}, Bitmap: {bitmap}")
    Bit=str(bin(bitmap))
    print(Bit)
    print(len(Bit))

conn.close()
