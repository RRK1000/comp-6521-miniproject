import psycopg2
from psycopg2 import sql
import csv
import os

# Replace these with your actual database connection parameters
dbname = 'miniproject'
user = 'postgres'
password = 'password'
host = '127.0.0.1'
port = '5432'

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

def generateBitmap(tableName, attribute, primaryKey_Column):

    bitmapAlreadyExists=os.path.isfile('bitmap_index_'+tableName+'.'+attribute+'.csv')

    if(bitmapAlreadyExists):
        # print("Bitmap already made!")
        return
    
    cursor = conn.cursor()

    bitmap_dict = {}

    unique_values_query = f'SELECT DISTINCT {attribute} FROM {tableName}'
    cursor.execute(unique_values_query)
    unique_values = [row[0] for row in cursor.fetchall()]

    for value in unique_values:
        bitmap = 0
        
        rows_with_value_query = f'SELECT {primaryKey_Column} FROM {tableName} WHERE {attribute} = \'{value}\''
        
        cursor.execute(rows_with_value_query)
        rows_with_value = [row[0] for row in cursor.fetchall()]

        for row_id in rows_with_value:
            bitmap |= (1 << row_id)

        bitmap_dict[value] = int(bitmap)

    csv_file_path = 'bitmap_index_'+tableName+'.'+attribute+'.csv'

    bitmap_dict=dict(sorted(bitmap_dict.items()))

    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Value', 'Bitmap'])

        for value, bitmap in bitmap_dict.items():
            Bit=str(bin(bitmap))
            # to compress bitmap
            compressedBitmap=compressBitmap(Bit[2:][::-1])
            csv_writer.writerow([value, compressedBitmap])

    # print(f"Bitmap created and saved in {csv_file_path}")


def compressBitmap(bit):

    compressedBitmap=""
    index=0

    for c in bit:
        if c=='1':

            runLengthInBinary=bin(index)[2:]
            runLength=len(runLengthInBinary)

            while runLength!=1:
                compressedBitmap+='1'
                runLength-=1

            compressedBitmap+='0'+runLengthInBinary

            index=0
        
        else:
            index+=1

    return compressedBitmap

def extractBitmap(fileName):

    bitmap_dict={}

    csv_file_path = fileName

    # Read the CSV file and populate the bitmap_dict
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        # Skip the header row
        next(csv_reader)
        
        # Read data and populate bitmap_dict
        for row in csv_reader:
            value, bitmap = row
            decompressedBitmap=decompressBitmap(bitmap)
            bitmap_dict[int(value)] = decompressedBitmap

    return bitmap_dict

def decompressBitmap(bitmap):

    decompressedBitmap=""

    index=0
    runLengthUnary=0

    while index<len(bitmap):

        runLengthUnary+=1

        if bitmap[index]=='0':
            runLengthBinary=bitmap[index+1: index+runLengthUnary+1]
            runLengthInteger=int(runLengthBinary, 2)

            while runLengthInteger!=0:
                decompressedBitmap+='0'
                runLengthInteger-=1

            decompressedBitmap+='1'

            index+=runLengthUnary+1
            runLengthUnary=0
        
        else:
            index+=1
    
    return decompressedBitmap