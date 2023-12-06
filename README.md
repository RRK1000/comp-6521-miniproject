# COMP6521

# Pre-Requisites to set up
- PostresDB
- Python3

# Configure the Postgres Database Server (with sample data)

```shell
    $ cd sql/
    $ psql postgres 
        postgres-#  CREATE ROLE postgres WITH LOGIN PASSWORD ‘password’;
        postgres-#  ALTER ROLE postgres CREATEDB;
        postgres-#  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
        postgres-#  \q
    $ psql -h localhost -U admin -f demo.sql
```

# Running the Query Processor

Join types:
- 1 : Cross Product Join
- 2 : Sort Based Join
- 3 : Bitmap Index Based Join

```shell 
    $ pip install -r requirements.txt
    $ python3 main.py <join_type>
    
    Example Usage: 
    $ python3 main.py 2
```
