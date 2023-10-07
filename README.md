# COMP6521

# Pre-Requisites to set up
- PostresDB
- Python3

# Configure the Postgres Database Server (with sample data)

```shell
    $ psql postgres 
        postgres-#  CREATE ROLE admin WITH LOGIN PASSWORD ‘password’;
        postgres-#  ALTER ROLE admin CREATEDB;
        postgres-#  \q
    $ psql -h localhost -U admin -f sample_data.sql
```

# Running the Query Processor
```shell 
    $ pip3 install psycopg2
    $ python3 main.py
```