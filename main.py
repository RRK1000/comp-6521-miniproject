import psycopg2
import queryprocessor


def getDBConn():
    conn = psycopg2.connect(
        database="miniproject",
        user="admin",
        password="password",
        host="127.0.0.1",
        port="5432",
    )

    conn.autocommit = True
    return conn


if __name__ == "__main__":
    conn = getDBConn()
    queryprocessor = queryprocessor.QProcessor()

    query1 = """SELECT product, product_type FROM routes, products WHERE product = products.product_id AND region_from = 1;"""
    query2 = """SELECT region_name from routes, regions, products WHERE product_type = 'ELECTRONICS' AND routes.product = products.product_id AND routes.region_from = regions.region_id;"""
    queryprocessor.processSelectQuery(conn, query1)

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    # cursor.execute(query)

    # result = cursor.fetchall()
    # for row in result:
    #     print(row)

    conn.close()
