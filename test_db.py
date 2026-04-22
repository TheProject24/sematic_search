import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Try the original
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing original URL: {DATABASE_URL}")

def test_conn(url):
    try:
        engine = create_engine(url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print(f"SUCCESS: {result.fetchone()[0]}")
            return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

print("\n--- Testing Port 5432 (Direct) ---")
test_conn(DATABASE_URL)

# Try Port 6543 (Pooler)
if ":5432/" in DATABASE_URL:
    POOLER_URL = DATABASE_URL.replace(":5432/", ":6543/")
    print(f"\n--- Testing Port 6543 (Pooler) ---")
    print(f"URL: {POOLER_URL}")
    test_conn(POOLER_URL)
