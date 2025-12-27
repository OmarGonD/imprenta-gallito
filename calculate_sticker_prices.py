
def calculate_prices():
    # Base data: Size -> (Units for 45 soles, Unit Cost)
    # Unit Cost = 45 / Units
    
    provider_data = {
        "4cm x 4cm": 500,
        "5cm x 5cm": 360,
        "6cm x 6cm": 280,
        "7cm x 7cm": 200,
        "8cm x 8cm": 150,
        "9cm x 9cm": 130,
        "10cm x 10cm": 100
    }
    
    quantities = [10, 20, 50, 100, 500, 1000]
    results = []

    print(f"{'Medida':<12} | {'Costo/Uni':<9} | {'Precio/Uni':<10} | {'10 u':<8} | {'20 u':<8} | {'50 u':<8} | {'100 u':<8} | {'500 u':<8} | {'1000 u':<8}")
    print("-" * 110)

    for size, batch_units in provider_data.items():
        cost_total_batch = 45.0
        unit_cost = cost_total_batch / batch_units
        
        # Ganar 50% (Margin method: Price = Cost / (1 - 0.5) = Cost * 2)
        # This usually implies 50% of the final price is profit.
        unit_price = unit_cost * 2
        
        row = [size, f"S/.{unit_cost:.3f}", f"S/.{unit_price:.3f}"]
        
        for qty in quantities:
            total_price = unit_price * qty
            # Rounding to 1 decimal or integer usually better for sales, but 2 for precision first
            row.append(f"{total_price:.2f}")
            
        print(f"{row[0]:<12} | {row[1]:<9} | {row[2]:<10} | {row[3]:<8} | {row[4]:<8} | {row[5]:<8} | {row[6]:<8} | {row[7]:<8} | {row[8]:<8}")

calculate_prices()
