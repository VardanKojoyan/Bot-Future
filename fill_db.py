import sqlite3
import numpy as np

def create_and_fill_db(db_name="data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Աղյուսակի ստեղծում
    cursor.execute("DROP TABLE IF EXISTS points")
    cursor.execute("""
        CREATE TABLE points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            x REAL NOT NULL,
            y REAL NOT NULL
        )
    """)
    
    # Գեներացնում ենք 200 կետ x ∈ [0, 10]
    x = np.linspace(0, 10, 200)
    
    # Ֆունկցիա կոտորակային հաճախություններով՝ y = 1.5 + 2.0*sin(1.43*x + 0.3) + 1.2*sin(2.87*x - 0.5)
    y = 1.5 + 2.0 * np.sin(1.43 * x + 0.3) + 1.2 * np.sin(2.87 * x - 0.5)
    
    # Լցնում ենք տվյալները բազա
    data = [(float(x[i]), float(y[i])) for i in range(len(x))]
    cursor.executemany("INSERT INTO points (x, y) VALUES (?, ?)", data)
    
    conn.commit()
    conn.close()
    print(f"✅ {len(x)} կետ հաջողությամբ գրանցվեց {db_name} բազայում։")

if __name__ == "__main__":
    create_and_fill_db()
