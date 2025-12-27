import math

def calculate_smart_prices():
    # Costos Provider
    FULL_BATCH_COST = 45.0
    HALF_BATCH_COST = 25.0
    
    # Costo por tu tiempo de gestión (abrir archivo, coordinar, enviar)
    # Esto asegura que ganes algo extra aparte del costo de impresión.
    MANAGEMENT_FEE = 12.00 
    
    # Margen deseado por unidad (adicional al costo)
    # Esto define qué tanto sube el precio si llevan más cantidad
    # Lo basamos en el costo unitario base x 1.5 aprox
    
    provider_data = {
        # Medida: (Unidades Full, Unidades Media, Precio Sugerido Venta Unitaria)
        "4cm x 4cm":   (500, 250, 0.15), 
        "5cm x 5cm":   (360, 180, 0.20),
        "6cm x 6cm":   (280, 140, 0.30),
        "7cm x 7cm":   (200, 100, 0.40),
        "8cm x 8cm":   (150, 75,  0.50),
        "9cm x 9cm":   (130, 65,  0.60),
        "10cm x 10cm": (100, 50,  0.80),
    }
    
    quantities = [10, 20, 50, 100, 500, 1000]
    
    print(f"{'Medida':<12} | {'Cap. Media':<10} | {'10 u':<8} | {'20 u':<8} | {'50 u':<8} | {'100 u':<8} | {'500 u':<8} | {'1000 u':<8}")
    print("-" * 115)

    for size, (full_units, half_units, unit_markup) in provider_data.items():
        row = [size, f"{half_units} u"]
        
        for qty in quantities:
            # 1. Calcular Costo Real
            num_full_batches = qty // full_units
            remainder = qty % full_units
            
            real_cost = num_full_batches * FULL_BATCH_COST
            
            if remainder > 0:
                if remainder <= half_units:
                    real_cost += HALF_BATCH_COST
                else:
                    real_cost += FULL_BATCH_COST
            
            # 2. Calcular Precio Smart
            # Fórmula: Costo Real + Tarifa Gestión + (ValorUnidad * Cantidad)
            variable_profit = unit_markup * qty
            smart_price = real_cost + MANAGEMENT_FEE + variable_profit
            
            # Redondeo estético (ej. 39.4 -> 40.0, 39.1 -> 39.5)
            # Para simplificar: Redondear a un entero o .50
            smart_price = math.ceil(smart_price * 2) / 2
            
            row.append(f"{smart_price:.2f}")
            
        print(f"{row[0]:<12} | {row[1]:<10} | {row[2]:<8} | {row[3]:<8} | {row[4]:<8} | {row[5]:<8} | {row[6]:<8} | {row[7]:<8}")

calculate_smart_prices()
