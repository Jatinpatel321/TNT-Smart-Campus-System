from database import engine, Base
from sqlalchemy import text

# Drop all tables and recreate with new schema
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables with new schema...")
Base.metadata.create_all(bind=engine)

print("Migration completed successfully.")
