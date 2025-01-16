from sqlalchemy import create_engine
import sqlite3

PSQL_DATABASE_ADDRESS = "postgresql://postgres:postgres@localhost:5432/testing"

psql_engine = create_engine(PSQL_DATABASE_ADDRESS)
sqlite_engine = create_engine('sqlite:///:memory:', echo=True)
