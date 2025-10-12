#!/usr/bin/env python3
"""
Script para ver el log de productos de WooCommerce
"""
import json
import sys

LOG_FILE = '/home/cerrotico/work/crushme_project/backend/woocommerce_products_log.json'

def main():
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("="*80)
        print("LOG DE PRODUCTOS DE WOOCOMMERCE")
        print("="*80)
        print(f"Timestamp: {data['timestamp']}")
        print(f"Endpoint: {data['endpoint']}")
        print(f"Parámetros: category_id={data['params']['category_id']}, page={data['params']['page']}, per_page={data['params']['per_page']}")
        print(f"Total productos recibidos: {data['total_products_received']}")
        print(f"Productos en el log: {data['products_in_log']}")
        print("="*80)
        
        if len(sys.argv) > 1 and sys.argv[1] == '--list':
            print("\nLISTA DE PRODUCTOS:")
            for idx, product in enumerate(data['products'], 1):
                print(f"\n{idx}. ID: {product['id']} - {product['name']}")
                print(f"   Precio: ${product['price']} - Stock: {product['stock_quantity']}")
                print(f"   Categoría: {product['categories'][0]['name'] if product['categories'] else 'Sin categoría'}")
        
        elif len(sys.argv) > 1 and sys.argv[1].isdigit():
            idx = int(sys.argv[1]) - 1
            if 0 <= idx < len(data['products']):
                print(f"\nPRODUCTO #{idx+1}:")
                print(json.dumps(data['products'][idx], indent=2, ensure_ascii=False))
            else:
                print(f"\n❌ Error: Producto {sys.argv[1]} no existe (hay {len(data['products'])} productos)")
        
        else:
            print("\nUSO:")
            print("  python view_products_log.py           # Ver resumen")
            print("  python view_products_log.py --list    # Ver lista de productos")
            print("  python view_products_log.py <número>  # Ver detalle de un producto")
            print("\nEjemplo: python view_products_log.py 1  # Ver primer producto completo")
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {LOG_FILE}")
        print("Haz una petición al endpoint primero para generar el log.")
    except json.JSONDecodeError:
        print(f"❌ Error: El archivo {LOG_FILE} no es un JSON válido")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    main()
