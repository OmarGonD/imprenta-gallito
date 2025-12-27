from decimal import Decimal

SMART_PRICING_RULES = {
    'ropa-bolsos': {
        'logic_type': 'tiered_margin',
        'base_cost': Decimal('40.00'),  # From apply_smart_pricing_ropa.py
        'min_margin': 0.15,  # Implied from logic
        'tiers': [
            {'min': 1, 'price': Decimal('67.00')},
            {'min': 12, 'price': Decimal('62.00')},
            {'min': 50, 'price': Decimal('56.00')},
            {'min': 100, 'price': Decimal('50.00')},
            {'min': 500, 'price': Decimal('48.00')},
        ],
        'surcharges': {
            'color': {
                'match': lambda val: 'blanco' not in val.lower() and 'white' not in val.lower(),
                'price': Decimal('9.00')
            },
            'print_size': {
                '14x21': Decimal('0.00'),
                '21x30': Decimal('9.00'),
                '32x38': Decimal('17.00'),
            }
        }
    },
    'stickers-etiquetas': {
        'logic_type': 'cost_plus_fixed',
        'params': {
            'full_batch_cost': Decimal('45.00'),
            'half_batch_cost': Decimal('25.00'),
            'management_fee': Decimal('12.00'),
        },
        # Defined per size variant (slug substring matching)
        'variants': {
            '4x4': {'full_units': 500, 'half_units': 250, 'unit_markup': Decimal('0.15')},
            '5x5': {'full_units': 360, 'half_units': 180, 'unit_markup': Decimal('0.20')},
            '6x6': {'full_units': 280, 'half_units': 140, 'unit_markup': Decimal('0.30')},
            '7x7': {'full_units': 200, 'half_units': 100, 'unit_markup': Decimal('0.40')},
            '8x8': {'full_units': 150, 'half_units': 75,  'unit_markup': Decimal('0.50')},
            '9x9': {'full_units': 130, 'half_units': 65,  'unit_markup': Decimal('0.60')},
            '10x10': {'full_units': 100, 'half_units': 50,  'unit_markup': Decimal('0.80')},
        },
        'quantities': [10, 20, 50, 100, 500, 1000]
    }
}
