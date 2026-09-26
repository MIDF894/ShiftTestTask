import asyncio
import sys
from shifttestex.database.orm import *

async def init_with_retry(max_retries=10, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            await StartDb()
            print("Database initialized successfully!")
            return
        except Exception as e:
            if attempt == max_retries:
                print(f"Failed to initialize database after {max_retries} attempts: {e}")
                sys.exit(1)
            print(f"Database connection attempt {attempt}/{max_retries} failed: {e}")
            print(f"Retrying in {delay}s...")
            await asyncio.sleep(delay)
            delay = min(delay * 2, 30)  # Exponential backoff, max 30s

asyncio.run(init_with_retry())