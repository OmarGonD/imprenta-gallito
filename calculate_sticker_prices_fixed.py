
import math

def calculate_prices_fixed():
    # Costos Provider
    FULL_BATCH_COST = 45.0
    HALF_BATCH_COST = 25.0
    
    # Datos del proveedor: Medida -> Unidades en PLANCHA COMPLETA (Full)
    # Asumimos que Media Plancha trae la mitad (approx floor)
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
    
    print(f"{'Medida':<12} | {'Full/Media':<12} | {'10 u':<8} | {'20 u':<8} | {'50 u':<8} | {'100 u':<8} | {'500 u':<8} | {'1000 u':<8}")
    print("-" * 115)

    for size, full_units in provider_data.items():
        half_units = math.floor(full_units / 2)
        
        row = [size, f"{full_units}/{half_units}"]
        
        for qty in quantities:
            # Calcular costo óptimo
            # 1. Cuántas planchas enteras llenamos?
            num_full_batches = qty // full_units
            remainder = qty % full_units
            
            cost = num_full_batches * FULL_BATCH_COST
            
            if remainder > 0:
                if remainder <= half_units:
                    cost += HALF_BATCH_COST # Sale más a cuenta pedir media plancha extra
                else:
                    cost += FULL_BATCH_COST # Necesitamos otra plancha completa
            
            # Caso especial: Si qty cabe en media plancha, el loop arriba ya lo cubre 
            # (num_full=0, remainder <= half -> cost = 25)
            
            # Precio Venta (Ganancia 50% -> Costo * 2)
            price = cost * 2
            
            row.append(f"{price:.2f}")
            
        print(f"{row[0]:<12} | {row[1]:<12} | {row[2]:<8} | {row[3]:<8} | {row[4]:<8} | {row[5]:<8} | {row[6]:<8} | {row[7]:<8}")

calculate_prices_fixed()
