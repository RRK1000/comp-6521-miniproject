# COMP6521

# Pre-Requisites to set up
- PostresDB
- Python3

# Configure the Postgres Database Server (with sample data)

```shell
    $ psql postgres 
        postgres-#  CREATE ROLE postgres WITH LOGIN PASSWORD ‘password’;
        postgres-#  ALTER ROLE postgres CREATEDB;
        postgres-#  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
        postgres-#  \q
    $ psql -h localhost -U admin -f demo.sql
```

# Running the Query Processor
```shell 
    $ pip3 install psycopg2
    $ python3 main.py
```