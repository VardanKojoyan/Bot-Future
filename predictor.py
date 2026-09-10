import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def load_data_from_db(db_name="data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT x, y FROM points ORDER BY x ASC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise ValueError("Բազան դատարկ է։")
        
    x = np.array([r[0] for r in rows], dtype=float)
    y = np.array([r[1] for r in rows], dtype=float)
    return x, y

def generate_prediction_plot(db_name="data.db", output_img="prediction.png", future_hours=48, top_harmonics=5):
    x_real, y_real = load_data_from_db(db_name)
    N = len(x_real)
    
    # 1. Գնային Թրենդի առանձնացում (1-ին կամ 2-րդ աստիճանի պոլինոմ)
    trend_poly = np.polyfit(x_real, y_real, deg=1)
    trend_past = np.polyval(trend_poly, x_real)
    detrended = y_real - trend_past  # Ալիքային տատանումները առանց թրենդի
    
    # 2. Fast Fourier Transform (FFT) detrended տվյալների վրա
    fft_vals = np.fft.rfft(detrended)
    fft_freqs = np.fft.rfftfreq(N)
    
    # Վերցնում ենք ամենաբարձր ամպլիտուդով top_harmonics հաճախությունները
    amps = np.abs(fft_vals)
    top_indices = np.argsort(amps)[::-1][:top_harmonics]
    
    # 3. Ապագա ժամերի տիրույթ (օրինակ՝ առաջիկա 48 ժամը)
    last_x = x_real[-1]
    x_future = np.arange(last_x + 1, last_x + 1 + future_hours)
    x_full = np.concatenate([x_real, x_future])
    
    # 4. Ֆուրյեի վերականգնում (Reconstruction & Extrapolation)
    detrended_full = np.zeros(len(x_full))
    for idx in top_indices:
        amp = np.abs(fft_vals[idx]) / (N / 2)
        phase = np.angle(fft_vals[idx])
        freq = fft_freqs[idx]
        detrended_full += amp * np.cos(2 * np.pi * freq * x_full + phase)
        
    trend_full = np.polyval(trend_poly, x_full)
    y_pred_full = trend_full + detrended_full
    
    # 5. Գտնում ենք ապագայի (Future) Էքստրեմումները
    future_mask = x_full > last_x
    x_fut = x_full[future_mask]
    y_fut = y_pred_full[future_mask]
    
    max_peaks, _ = find_peaks(y_fut, distance=3)
    min_peaks, _ = find_peaks(-y_fut, distance=3)
    
    extremas = []
    for p in max_peaks:
        hours_ahead = int(x_fut[p] - last_x)
        extremas.append({'type': 'MAX', 'x': x_fut[p], 'y': y_fut[p], 'hours_ahead': hours_ahead})
    for p in min_peaks:
        hours_ahead = int(x_fut[p] - last_x)
        extremas.append({'type': 'MIN', 'x': x_fut[p], 'y': y_fut[p], 'hours_ahead': hours_ahead})
    extremas.sort(key=lambda item: item['x'])
    
    # 6. Գրաֆիկի կառուցում
    plt.figure(figsize=(11, 5))
    plt.plot(x_real, y_real, color='black', label='BTC/USDT Իրական (Binance 1h)', linewidth=1.5)
    plt.plot(x_full[:N], y_pred_full[:N], color='blue', alpha=0.7, linestyle='--', label='Ֆուրյե+Թրենդ մոտարկում')
    plt.plot(x_full[N-1:], y_pred_full[N-1:], color='red', linewidth=2, label=f'Կանխատեսում (+{future_hours} ժամ)')
    plt.axvline(x=last_x, color='gray', linestyle=':', label='Այսօր/Ներկա պահ')
    
    for ext in extremas:
        color = 'green' if ext['type'] == 'MAX' else 'purple'
        marker = '^' if ext['type'] == 'MAX' else 'v'
        plt.plot(ext['x'], ext['y'], marker=marker, color=color, markersize=8)
        plt.annotate(f"{ext['type']}\n+{ext['hours_ahead']}h\n${ext['y']:.0f}", 
                     (ext['x'], ext['y']), 
                     textcoords="offset points", 
                     xytext=(0, 10 if ext['type']=='MAX' else -25), 
                     ha='center', fontsize=7, color=color)
        
    plt.title(f"Binance BTC/USDT Ժամային Կանխատեսում (+{future_hours} ժամ)")
    plt.xlabel("Ժամեր (Hours)")
    plt.ylabel("Գին ($ USDT)")
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.savefig(output_img, dpi=150, bbox_inches='tight')
    plt.close()
    
    return extremas, output_img
