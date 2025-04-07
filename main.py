
import os
import redis
import psycopg2
from fastapi import FastAPI
from strategies import get_strategy

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL")
POSTGRES_URL = os.getenv("POSTGRES_URL")
STRATEGY_NAME = os.getenv("STRATEGY_NAME", "simple")

redis_client = redis.from_url(REDIS_URL)

def get_pg_connection():
    return psycopg2.connect(POSTGRES_URL)

@app.get("/")
def root():
    return {"status": "Running"}

@app.get("/trade")
def trade():
    strategy_class = get_strategy(STRATEGY_NAME)
    strategy = strategy_class()
    signal, price = strategy.get_signal()
    redis_client.set("last_signal", signal)

    conn = get_pg_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS trade_log (id SERIAL PRIMARY KEY, signal TEXT, price FLOAT, time TIMESTAMP DEFAULT NOW());")
    cur.execute("INSERT INTO trade_log (signal, price) VALUES (%s, %s);", (signal, price))
    conn.commit()
    cur.close()
    conn.close()

    return {"signal": signal, "price": price}
