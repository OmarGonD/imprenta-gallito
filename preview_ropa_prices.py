from decimal import Decimal
import math

def preview_prices():
    COST_POLO = 30.00
    PRINT_COSTS = {
        (False, '14x21'): 10.00,
        (False, '21x30'): 15.00,
        (False, '32x38'): 20.00,
        (True, '14x21'): 15.00,
        (True, '21x30'): 20.00,
        (True, '32x38'): 25.00,
    }
    
    BASE_COST = 40.00
    
    # Calculate Base Prices (Ceiling to Integer)
    # 40% -> 66.67 -> 67
    # 35% -> 61.54 -> 62
    # 28% -> 55.56 -> 56
    # 20% -> 50.00 -> 50
    # 15% -> 47.06 -> 48
    
    p1 = math.ceil(BASE_COST / 0.60)
    p12 = math.ceil(BASE_COST / 0.65)
    p50 = math.ceil(BASE_COST / 0.72)
    p100 = math.ceil(BASE_COST / 0.80)
    p500 = math.ceil(BASE_COST / 0.85)

    # But wait, user said "decena superior". 
    # Let's try to interpret "Decena" as nearest 0 or 5? Or strictly 10?
    # Strict 10: 70, 70, 60, 50, 50. (Loss of tiers)
    # Let's try "Commercial Rounding" (ends in 0, 2, 5, 8?) or just Ceiling.
    # I will present Ceiling.
    
    BASE_TIERS = [
        (1, 11, p1), 
        (12, 49, p12),
        (50, 99, p50), 
        (100, 499, p100), 
        (500, 9999, p500) 
    ]
    
    # Surcharges (Ceiling)
    # 8.5 -> 9
    ADDER_COLOR = 9.00
    ADDER_SIZE_21 = 9.00
    ADDER_SIZE_32 = 17.00
    
    print(f"{'Qty':<5} | {'Garment':<8} | {'Size':<8} | {'Unit Cost':<10} | {'Base Price':<10} | {'Surcharges':<10} | {'Final Unit':<10} | {'Total':<10} | {'Margin %':<8}")
    print("-" * 105)
    
    scenarios = [
        (1, False, '14x21'), (12, False, '14x21'), (50, False, '14x21'), (100, False, '14x21'), (500, False, '14x21'),
        (1, True, '14x21'),  (500, True, '14x21'),
        (1, True, '32x38'), (500, True, '32x38'),
    ]
    
    for qty, is_color, size in scenarios:
        print_cost = PRINT_COSTS[(is_color, size)]
        total_cost = COST_POLO + print_cost
        
        base_price = 0
        for min_q, max_q, price in BASE_TIERS:
            if min_q <= qty <= max_q:
                base_price = price
                break
        
        surcharge = 0
        if is_color:
            surcharge += ADDER_COLOR
        
        if size == '21x30':
            surcharge += ADDER_SIZE_21
        elif size == '32x38':
            surcharge += ADDER_SIZE_32
            
        final_unit_price = base_price + surcharge
        
        total_price = final_unit_price * qty
        margin = 0
        if final_unit_price > 0:
            margin = (final_unit_price - total_cost) / final_unit_price * 100
        
        garment_str = "Color" if is_color else "White"
        
        print(f"{qty:<5} | {garment_str:<8} | {size:<8} | {total_cost:<10.2f} | {base_price:<10.2f} | {surcharge:<10.2f} | {final_unit_price:<10.2f} | {total_price:<10.2f} | {margin:.1f}%")

if __name__ == "__main__":
    preview_prices()
