#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add the agent folder to the system path to import src
sys.path.insert(0, str(Path(__file__).resolve().parent / "agent"))

try:
    from src.mxf_pricing_estimator import estimate_mxf_materials_and_price
except ImportError:
    print("Error: Could not import mxf_pricing_estimator from agent/src.")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 estimate_price.py <path_to_mxf_file> [timber_rate_eur_m3] [fabrication_markup] [setup_cost]")
        print("\nDefaults:")
        print("  timber_rate_eur_m3:  4866.76 €/m3 (Slovak/Czech market)")
        print("  fabrication_markup:  0.2878 (28.78%)")
        print("  setup_cost:          156.41 € per unique shape")
        sys.exit(1)

    mxf_path = sys.argv[1]
    if not os.path.exists(mxf_path):
        print(f"Error: File not found at '{mxf_path}'")
        sys.exit(1)

    # Optional parameter overrides from CLI
    timber_rate = float(sys.argv[2]) if len(sys.argv) > 2 else 4866.76
    fab_markup = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2878
    setup_fee = float(sys.argv[4]) if len(sys.argv) > 4 else 156.41

    try:
        results = estimate_mxf_materials_and_price(
            mxf_path,
            timber_rate_eur_m3=timber_rate,
            fabrication_markup=fab_markup,
            setup_cost_per_type=setup_fee
        )
        
        print(f"\n=== Cost Estimate for {mxf_path} ===")
        print(f"Total Timber Volume: {results['timber_volume_m3']:.4f} m³")
        print(f"Total Plates Quantity: {results['plates_qty']} pcs ({results['plates_weight_kg']:.2f} kg)")
        print(f"Total Plates Cost: {results['plates_cost_eur']:.2f} €")
        print(f"Estimated Grand Total (excl. VAT): {results['total_price_eur']:.2f} €")
        
        print("\n--- Line Item Details ---")
        for item in results["line_items"]:
            print(f"  {item['name']} (qty {item['qty']}):")
            print(f"    Timber: {item['timber_cost_eur']:.2f} € ({item['timber_volume_m3']:.4f} m³)")
            print(f"    Plates: {item['plates_cost_eur']:.2f} €")
            print(f"    Final Line Price: {item['price_eur']:.2f} €")
            
    except Exception as e:
        print(f"Error: Failed to estimate price: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
