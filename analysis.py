import csv
import collections
import statistics
import os

def analyze_history(file_path="powerball_db.csv", lookback=100):
    print(f"Analyzing last {lookback} drawings from {file_path}...\n")
    
    if not os.path.exists(file_path):
        print("Database file not found.")
        return

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    if len(rows) < lookback:
        print(f"Not enough data. Using all {len(rows)} rows.")
        lookback = len(rows)

    # Get last N rows
    data = rows[-lookback:]
    
    white_balls = []
    red_balls = []
    sums = []
    odd_counts = []
    
    for row in data:
        # Parse numbers "11 21 27 36 62 24"
        nums = [int(n) for n in row[1].split()]
        whites = nums[:5]
        red = nums[5]
        
        white_balls.extend(whites)
        red_balls.append(red)
        sums.append(sum(whites))
        odd_counts.append(sum(1 for n in whites if n % 2 != 0))

    # --- Frequency Analysis ---
    white_counts = collections.Counter(white_balls)
    red_counts = collections.Counter(red_balls)
    
    # Top Hot Numbers
    top_white = white_counts.most_common(5)
    top_red = red_counts.most_common(3)
    
    # Cold Numbers (Least common)
    # We need to consider numbers that appeared 0 times too
    all_whites = set(range(1, 70))
    seen_whites = set(white_counts.keys())
    zero_whites = list(all_whites - seen_whites)
    
    # Sort by count (asc), then by number
    sorted_whites = sorted(white_counts.items(), key=lambda x: (x[1], x[0]))
    cold_white = sorted_whites[:5]
    
    # --- Statistics ---
    avg_sum = statistics.mean(sums)
    avg_odd = statistics.mean(odd_counts)
    
    # --- Output Report ---
    print("="*40)
    print(f"STATISTICAL ANALYSIS (Last {lookback} Draws)")
    print("="*40)
    
    print(f"\n1. MOST FREQUENT (HOT) NUMBERS")
    print("-" * 30)
    print("White Balls:")
    for num, count in top_white:
        bar = "█" * count
        print(f"  #{num:02d}: {count} draws {bar}")
        
    print("\nPowerballs (Red):")
    for num, count in top_red:
        bar = "█" * count
        print(f"  #{num:02d}: {count} draws {bar}")

    print(f"\n2. LEAST FREQUENT (COLD) NUMBERS")
    print("-" * 30)
    print("White Balls (Bottom 5):")
    if zero_whites:
        print(f"  Never drawn: {sorted(zero_whites)}")
    for num, count in cold_white:
        print(f"  #{num:02d}: {count} draws")

    print(f"\n3. DRAW CHARACTERISTICS")
    print("-" * 30)
    print(f"  Average Sum of White Balls: {avg_sum:.1f} (Theoretical Avg: 175)")
    print(f"  Average Odd Numbers per Draw: {avg_odd:.1f} / 5")
    
    # --- Interpretation ---
    print("\n" + "="*40)
    print("STRATEGY SUGGESTIONS")
    print("="*40)
    
    hot_pick = [n for n, c in top_white]
    hot_pick.sort()
    hot_red = top_red[0][0]
    
    print(f"🔥 MOMENTUM PICK (Playing Hot Numbers):")
    print(f"   {hot_pick} + Powerball {hot_red}")
    
    cold_pick = [n for n, c in cold_white]
    cold_pick.sort()
    # Find coldest red
    all_reds = set(range(1, 27))
    seen_reds = set(red_counts.keys())
    zero_reds = list(all_reds - seen_reds)
    if zero_reds:
        cold_red = zero_reds[0]
    else:
        cold_red = red_counts.most_common()[-1][0]
        
    print(f"🧊 CONTRARIAN PICK (Playing Due Numbers):")
    print(f"   {cold_pick} + Powerball {cold_red}")

if __name__ == "__main__":
    analyze_history()
