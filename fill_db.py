import sqlite3
import requests

def update_binance_data(symbol="BTCUSDT", interval="1h", limit=200, db_name="data.db"):
    # Bybit API endpoint (արգելափակված չէ Render-ում)
    url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}&interval=60&limit={limit}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception(f"API Error status: {response.status_code}")
            
        data = response.json()
        if data.get('retCode') != 0:
            raise Exception(f"Bybit Error: {data.get('retMsg')}")
            
        kline_list = data['result']['list']
        # Bybit-ը տվյալները տալիս է հակառակ դասավորությամբ (նորից հին), ուստի շրջում ենք
        kline_list.reverse()
        
    except Exception as e:
        raise Exception(f"Data Fetch Error: {str(e)}")
    
    prices = []
    times = []
    
    for idx, item in enumerate(kline_list):
        close_price = float(item[4]) # 4-րդ ինդեքսը Close price-ն է
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
    print(f"✅ Bybit-ից {symbol} {len(prices)} մոմ հաջողությամբ գրանցվեց {db_name}-ում։")

if __name__ == "__main__":
    update_binance_data()
