import psycopg2
from psycopg2 import sql
import csv

# Replace these with your actual database connection parameters
dbname = 'miniproject'
user = 'postgres'
password = 'abcd@#A123'
host = '127.0.0.1'
port = '5432'

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cursor = conn.cursor()

bitmap_dict = {}

tableName="routes"
attribute="route_id"
primaryKey_Column="route_id"
# attribute_type can be string or number
# attribute_type="string"
attribute_type="number"

unique_values_query = f'SELECT DISTINCT {attribute} FROM {tableName}'
cursor.execute(unique_values_query)
unique_values = [row[0] for row in cursor.fetchall()]
print(unique_values)

for value in unique_values:
    bitmap = 0
    if attribute_type=="string":
        rows_with_value_query = f'SELECT {primaryKey_Column} FROM {tableName} WHERE {attribute} = \'{value}\''
    else:
        rows_with_value_query = f'SELECT {primaryKey_Column} FROM {tableName} WHERE {attribute} = {value}'
    cursor.execute(rows_with_value_query)
    rows_with_value = [row[0] for row in cursor.fetchall()]

    for row_id in rows_with_value:
        bitmap |= (1 << row_id)

    bitmap_dict[value] = int(bitmap/2)

csv_file_path = 'bitmap_index_'+tableName+'_'+attribute+'.csv'

with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)    
    csv_writer.writerow(['Value', 'Bitmap'])

    for value, bitmap in bitmap_dict.items():
        Bit=str(bin(bitmap))
        # to compress bitmap
        # need to implement compressor
        compressedBitmap=compressor(Bit[2:][::-1])
        csv_writer.writerow([value, compressedBitmap])

print(f"Bitmap created and saved in are saved in {csv_file_path}")

conn.close()
