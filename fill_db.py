import sqlite3
import cloudscraper
import requests

def update_binance_data(symbol="BTCUSDT", interval="1h", limit=200, db_name="data.db"):
    prices = []
    
    # 1. Փորձում ենք Bybit API-ն cloudscraper-ով (շրջանցում է Cloudflare 403-ը)
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={symbol}&interval=60&limit={limit}"
        res = scraper.get(url, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('retCode') == 0:
                kline_list = data['result']['list']
                kline_list.reverse()
                for item in kline_list:
                    prices.append(float(item[4])) # Close price
    except Exception as e:
        print(f"Bybit Error: {e}")

    # 2. Եթե Bybit-ը չաշխատեց, որպես fallback օգտագործում ենք CoinGecko API-ն
    if not prices:
        try:
            cg_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=8"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(cg_url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                raw_prices = data.get('prices', [])[-limit:]
                for item in raw_prices:
                    prices.append(float(item[1]))
            else:
                raise Exception(f"CoinGecko status: {res.status_code}")
        except Exception as e:
            raise Exception(f"API Error 403/Blocked: {str(e)}")

    if not prices:
        raise Exception("Չհաջողվեց ստանալ գնային տվյալներ API-ներից:")

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
    print(f"✅ {len(prices)} մոմ հաջողությամբ գրանցվեց {db_name}-ում։")

if __name__ == "__main__":
    update_binance_data()
