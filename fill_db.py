import sqlite3
import requests
import numpy as np

def update_binance_data(symbol="BTCUSDT", interval="1h", limit=200, db_name="data.db"):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Binance API Error: {response.status_code}")
        
    data = response.json()
    
    # Binance kline response format:
    # [ [open_time, open, high, low, close, volume, close_time, ...], ... ]
    prices = []
    times = []
    
    for idx, item in enumerate(data):
        close_price = float(item[4])
        prices.append(close_price)
        times.append(idx)  # ժամերը որպես 0, 1, 2, ..., limit-1
        
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS points")
    cursor.execute("""
        CREATE TABLE points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            x REAL NOT NULL,
            y REAL NOT NULL
        )
    """)
    
    insert_data = [(float(times[i]), float(prices[i])) for i in range(len(prices))]
    cursor.executemany("INSERT INTO points (x, y) VALUES (?, ?)", insert_data)
    
    conn.commit()
    conn.close()
    print(f"✅ Binance {symbol} {interval}-ից {len(prices)} մոմ հաջողությամբ գրանցվեց {db_name}-ում։")

if __name__ == "__main__":
    update_binance_data()
