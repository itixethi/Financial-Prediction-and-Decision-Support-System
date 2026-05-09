from database.db_storage import import_historical_prices_to_postgres

# Run historical PostgreSQL import direvctly from this file 
if __name__ == "__main__":
    
    import_historical_prices_to_postgres()