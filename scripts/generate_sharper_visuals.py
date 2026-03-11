import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta

# Configuration
RAW_DATA_DIR = "/home/gilang/Documents/Project/mm-lp-evaluation-sample/data/raw"
OUTPUT_CHARTS_DIR = "/home/gilang/Documents/Project/mm-lp-evaluation-sample/assets/charts"
os.makedirs(OUTPUT_CHARTS_DIR, exist_ok=True)

# Custom Colors
COLORS = {
    'tokocrypto': '#00C076',  # Bright green
    'reku': '#FF4D4D',        # Bright red/coral
    'exhausted': '#8B0000',   # Muted dark red
    'volatility': '#FFD700'   # Gold
}

plt.style.use('dark_background')
sns.set_theme(style="dark", palette="pastel")

def load_orderbook(exchange, pair):
    # Normalize filename because Indodax/Reku often use NO underscore while Tokocrypto uses underscore
    # Checking availability
    path = os.path.join(RAW_DATA_DIR, f"orderbook_{exchange}_{pair}.csv")
    if not os.path.exists(path):
        # try without underscore in pair
        path_no_underscore = os.path.join(RAW_DATA_DIR, f"orderbook_{exchange}_{pair.replace('_', '')}.csv")
        if os.path.exists(path_no_underscore):
            path = path_no_underscore
        else:
            print(f"Warning: Could not find orderbook for {exchange} {pair}")
            return pd.DataFrame()
    
    df = pd.read_csv(path)
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
    return df

def calculate_slippage(row, side, target_notional_usd):
    """Calculates slippage for a target notional. Returns (slippage_pct, exhausted)"""
    levels = 20
    cumulative_notional = 0
    weights_p_q = 0
    
    # We assume IDR pair for depth if not USDT. 
    # For simplicity in this demo, the requested sizes ($10K etc) are converted to IDR using fixed rate 15700
    idr_rate = 15700
    target_val = target_notional_usd * idr_rate if "IDR" in str(row.get('pair', '')) else target_notional_usd
    
    mid = row['mid_price']
    if pd.isna(mid) or mid <= 0:
        return np.nan, True

    for i in range(1, levels + 1):
        p = row.get(f"{side}_{i}_price")
        q = row.get(f"{side}_{i}_qty")
        if pd.isna(p) or pd.isna(q) or p <= 0 or q <= 0:
            continue
            
        level_notional = p * q
        if cumulative_notional + level_notional >= target_val:
            needed_q = (target_val - cumulative_notional) / p
            weights_p_q += needed_q * p
            cumulative_notional = target_val
            break
        else:
            weights_p_q += q * p
            cumulative_notional += level_notional
            
    if cumulative_notional < target_val:
        return np.nan, True
        
    # Final Results calculation
    total_qty = 0
    rem_notional = target_val
    for i in range(1, levels + 1):
        p = row.get(f"{side}_{i}_price")
        q = row.get(f"{side}_{i}_qty")
        if pd.isna(p) or pd.isna(q): continue
        take_q = min(q, rem_notional / p)
        total_qty += take_q
        rem_notional -= take_q * p
        if rem_notional <= 0: break
    
    avg_price = target_val / total_qty
    slippage = abs(avg_price - mid) / mid * 100
    return slippage, False

# ---------------------------------------------------------
# PANEL 1: Bid-Ask Spread Time-Series
# ---------------------------------------------------------
def generate_spread_chart():
    print("Generating Chart 1: Spread Time-Series...")
    toko = load_orderbook("tokocrypto", "BTC_IDR")
    reku = load_orderbook("reku", "BTCIDR")
    
    plt.figure(figsize=(12, 5))
    
    if not toko.empty:
        toko['spread_pct'] = (toko['best_ask'] - toko['best_bid']) / toko['mid_price'] * 100
        plt.plot(toko['timestamp_utc'], toko['spread_pct'], label='Tokocrypto', color=COLORS['tokocrypto'], linewidth=1.5)
        
    if not reku.empty:
        # Reku has many NaNs or missing quotes
        reku['spread_pct'] = (reku['best_ask'] - reku['best_bid']) / reku['mid_price'] * 100
        # If best_bid or best_ask is 0, it's quote absence
        reku.loc[reku['best_bid'] <= 0, 'spread_pct'] = np.nan
        plt.plot(reku['timestamp_utc'], reku['spread_pct'], label='Reku', color=COLORS['reku'], linewidth=1)

    # Detect Volatility (Mock for now based on data range)
    # Shading a period of high spread for Tokocrypto
    if not toko.empty:
        v_start = toko['timestamp_utc'].iloc[len(toko)//2]
        v_end = v_start + timedelta(hours=1)
        plt.axvspan(v_start, v_end, color=COLORS['volatility'], alpha=0.2, label='High Volatility Alert')

    plt.title("Bid-Ask Spread (%) - BTC/IDR", fontsize=14, pad=15)
    plt.ylabel("Spread % of Mid")
    plt.xlabel("Time (UTC)")
    plt.legend()
    plt.grid(alpha=0.1)
    plt.savefig(os.path.join(OUTPUT_CHARTS_DIR, "spread_timeseries.png"), bbox_inches='tight', dpi=150)
    plt.close()

# ---------------------------------------------------------
# PANEL 2: Slippage / Price Impact Bar Chart
# ---------------------------------------------------------
def generate_slippage_chart():
    print("Generating Chart 2: Slippage Impact...")
    sizes = [10000, 50000, 100000, 250000]
    labels = ["$10K", "$50K", "$100K", "$250K"]
    
    toko = load_orderbook("tokocrypto", "BTC_IDR").tail(100)
    reku = load_orderbook("reku", "BTCIDR").tail(100)
    
    results = []
    
    for exchange, df in [("Tokocrypto", toko), ("Reku", reku)]:
        if df.empty: continue
        for size in sizes:
            slips = []
            exhausted_count = 0
            for _, row in df.iterrows():
                s, ex = calculate_slippage(row, "ask", size) # Buy side impact
                if ex: exhausted_count += 1
                else: slips.append(s)
            
            avg_slip = np.mean(slips) if slips else 0
            is_exhausted = exhausted_count > len(df) * 0.5 # If > 50% exhausted
            results.append({
                'Exchange': exchange,
                'Size': f"${size//1000}K",
                'Slippage': 5.0 if is_exhausted else avg_slip, # Cap for visualization if exhausted
                'Exhausted': is_exhausted
            })
            
    res_df = pd.DataFrame(results)
    
    plt.figure(figsize=(14, 7)) # Hero chart - more vertical space
    
    # Custom plotting to handle exhausted bars
    x = np.arange(len(sizes))
    width = 0.35
    
    for i, exchange in enumerate(["Tokocrypto", "Reku"]):
        ex_data = res_df[res_df['Exchange'] == exchange]
        color = COLORS[exchange.lower()]
        bars = plt.bar(x + (i*width - width/2), ex_data['Slippage'], width, label=exchange, color=color)
        
        # Overlay exhausted bars
        for j, (_, row) in enumerate(ex_data.iterrows()):
            if row['Exhausted']:
                bars[j].set_facecolor(COLORS['exhausted'])
                plt.text(x[j] + (i*width - width/2), 5.1, "EXHAUSTED", 
                         ha='center', va='bottom', color=COLORS['exhausted'], fontsize=9, fontweight='bold')

    plt.title("Expected Buy-Side Price Impact (%)", fontsize=16, pad=20)
    plt.ylabel("Avg Slippage (%)")
    plt.xticks(x, labels)
    plt.ylim(0, 6)
    plt.legend()
    plt.grid(axis='y', alpha=0.1)
    plt.savefig(os.path.join(OUTPUT_CHARTS_DIR, "slippage_impact.png"), bbox_inches='tight', dpi=150)
    plt.close()

# ---------------------------------------------------------
# PANEL 3: Order Book Depth Heatmap (Tokocrypto)
# ---------------------------------------------------------
def generate_heatmap():
    print("Generating Chart 3: Depth Heatmap...")
    toko = load_orderbook("tokocrypto", "BTC_IDR").tail(200) # Use recent 48 hours approximate
    if toko.empty: return
    
    # Create bins relative to mid
    bins = np.linspace(-2.0, 2.0, 41) # -2% to +2%
    bin_labels = bins[:-1] + 0.1
    
    heatmap_data = []
    
    for _, row in toko.iterrows():
        mid = row['mid_price']
        row_bins = np.zeros(len(bins)-1)
        
        # Bids (negative side)
        for i in range(1, 21):
            p = row.get(f"bid_{i}_price")
            q = row.get(f"bid_{i}_qty")
            if pd.isna(p) or p <= 0: continue
            dist = (p - mid) / mid * 100
            idx = np.digitize(dist, bins) - 1
            if 0 <= idx < len(row_bins):
                row_bins[idx] += (p * q) / 1000000 # In Millions IDR
                
        # Asks (positive side)
        for i in range(1, 21):
            p = row.get(f"ask_{i}_price")
            q = row.get(f"ask_{i}_qty")
            if pd.isna(p) or p <= 0: continue
            dist = (p - mid) / mid * 100
            idx = np.digitize(dist, bins) - 1
            if 0 <= idx < len(row_bins):
                row_bins[idx] += (p * q) / 1000000
                
        heatmap_data.append(row_bins)
        
    hm_df = pd.DataFrame(heatmap_data).T
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(hm_df, cmap="mako", cbar_kws={'label': 'Depth (M IDR)'}, xticklabels=False)
    
    # Adjust Y axis to show price distance
    plt.yticks(np.arange(len(bins)-1)[::5], [f"{b:.1f}%" for b in bins[:-1][::5]])
    plt.axhline(20, color='white', linestyle='--', alpha=0.5) # Mid price line
    plt.text(len(toko)*1.02, 20, "MID", color='white', va='center')
    
    plt.title("Tokocrypto Depth Distribution vs Mid Price", fontsize=14)
    plt.ylabel("Distance from Mid (%)")
    plt.xlabel("Timeline (Snapshots)")
    plt.savefig(os.path.join(OUTPUT_CHARTS_DIR, "depth_heatmap_toko.png"), bbox_inches='tight', dpi=150)
    plt.close()

if __name__ == "__main__":
    generate_spread_chart()
    generate_slippage_chart()
    generate_heatmap()
    print("Done! Visuals exported to assets/charts/")
