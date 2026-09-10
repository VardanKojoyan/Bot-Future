import sqlite3
import requests

def update_binance_data(symbol="BTCUSDT", interval="1h", limit=200, db_name="data.db"):
    prices = []
    
    # Օգտագործում ենք CoinGecko-ի բաց API-ն, որը 100% աշխատում է Render-ում
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            raw_prices = data.get('prices', [])[-limit:]
            for item in raw_prices:
                prices.append(float(item[1]))
        else:
            raise Exception(f"CoinGecko HTTP Error: {res.status_code}")
    except Exception as e:
        raise Exception(f"API Fetch Error: {str(e)}")

    if not prices:
        raise Exception("Չհաջողվեց ստանալ գնային տվյալներ:")

    # Գրանցում ենք SQLite բազայում
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
    
    insert_data = [(float(i), prices[i]) for i in range(len(prices))]
    cursor.executemany("INSERT INTO points (x, y) VALUES (?, ?)", insert_data)
    
    conn.commit()
    conn.close()
    print(f"✅ CoinGecko-ից {len(prices)} կետ հաջողությամբ գրանցվեց {db_name}-ում։")

if __name__ == "__main__":
    update_binance_data()
