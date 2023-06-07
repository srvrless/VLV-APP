# Install dependencies
```
pip install -r requirements
```
# Database up

```
cd docker
docker-compose up -d
```

# Make migrations

```
psql -h HOST -d PASSWORD -U USER -p PORT -a -q -f pgsql/create_tables.pgsql
psql -h HOST -d PASSWORD -U USER -p PORT -a -q -f pgsql/functions.pgsql
psql -h HOST -d PASSWORD -U USER -p PORT -a -q -f pgsql/search_tables.pgsql
```

## Running app

```
python server.py
```
