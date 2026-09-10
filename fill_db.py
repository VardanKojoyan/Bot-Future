import sqlite3
import requests

def update_binance_data(symbol="BTCUSDT", interval="1h", limit=200, db_name="data.db"):
    # Օգտագործում ենք api1, api2 կամ api3 (որոնք չունեն 451 geo-block սահմանափակում)
    endpoints = [
        f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}",
        f"https://api2.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}",
        f"https://api3.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}",
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    ]
    
    response = None
    for url in endpoints:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                response = res
                break
        except Exception:
            continue
            
    if response is None or response.status_code != 200:
        status = response.status_code if response else "No Connection"
        raise Exception(f"Binance API Error: {status}")
        
    data = response.json()
    
    prices = []
    times = []
    
    for idx, item in enumerate(data):
        close_price = float(item[4])
        prices.append(close_price)
        times.append(idx)
        
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
    print(f"✅ Binance {symbol} {interval}-ից {len(prices)} մոմ գրանցվեց {db_name}-ում։")

if __name__ == "__main__":
    update_binance_data()
