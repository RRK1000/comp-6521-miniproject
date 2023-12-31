import sys
import psycopg2
import queryprocessor

def getDBConn():
    conn = psycopg2.connect(
        database="miniproject",
        user="postgres",
        password="password",
        host="127.0.0.1",
        port="5432",
    )

    conn.autocommit = True
    return conn


if __name__ == "__main__":
    conn = getDBConn()
    queryprocessor = queryprocessor.QProcessor()

    # query1 = """SELECT product, product_type FROM routes, products WHERE product = products.product_id AND region_from = 1;"""
    # query2 = """SELECT region_name from routes, regions, products WHERE product_type = 'ELECTRONICS' AND routes.product = products.product_id AND routes.region_from = regions.region_id;"""

    q1 = "select supplier_name from suppliers, routes where supplier = suppliers.supplier_id AND region_to = 5;"
    q2 = "SELECT product_type, region_name FROM products, regions where origin_region = regions.region_id;"
    q3 = "SELECT product_type FROM products, routes where product = products.product_id AND region_from in (1,2);"
    q4 = "SELECT A2, A3 FROM R, S WHERE R.A2 = S.B2 AND R.A3 = S.B3;"

    selectedQuery = q4
    output = queryprocessor.processSelectQuery(conn, selectedQuery, int(sys.argv[1]))

    print()
    print(selectedQuery)
    for row in output:
        print(row)
    print("Number of rows: ", len(output))
    print(
        "Time taken by processSelectQuery() in seconds: ",
        queryprocessor.selectQueryTime,
    )

    conn.close()
