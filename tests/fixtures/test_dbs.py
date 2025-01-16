import os

from sqlalchemy import create_engine

psql_address = os.environ.get('PSQL_ADDRESS', 'localhost')
PSQL_DATABASE_ADDRESS = f"postgresql://postgres:postgres@{psql_address}:5432/testing"

psql_engine = create_engine(PSQL_DATABASE_ADDRESS)
sqlite_engine = create_engine('sqlite:///:memory:', echo=True)
