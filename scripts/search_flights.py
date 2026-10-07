#!/usr/bin/env python3
"""
Search flights in Argentina using Google Flights via browser automation.
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime


def search_google_flights(from_airport: str, to_airport: str, date: str, return_date: str = None, adults: int = 1) -> list:
    """Search Google Flights and return structured results."""
    
    # Build URL
    base_url = "https://www.google.com/travel/flights"
    query = f"Flights+from+{from_airport}+to+{to_airport}+on={date}"
    if return_date:
        query += f"+returning+{return_date}"
    else:
        query += "+one+way"
    query += "&hl=es&curr=ARS"
    
    url = f"{base_url}?q={query}"
    
    # Use browser to search
    try:
        # Navigate to Google Flights
        result = subprocess.run(
            ["python3", "-c", f"""
import sys
import os
sys.path.insert(0, os.environ.get('BROWSER_HELPERS_PATH', './browser-helpers'))
from browser_helpers import new_tab, wait_for_load, js

new_tab('{url}')
wait_for_load()

# Wait for results to load
import time
time.sleep(3)

# Extract results
results = js('''
(() => {{
  const text = document.body.innerText;
  const idx = text.indexOf('Resultados de búsqueda');
  if (idx >= 0) return text.substring(idx, idx + 10000);
  return text.substring(0, 10000);
}})()
''')
print(results)
"""],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return []
        
        return parse_results(result.stdout)
    except Exception as e:
        print(f"Error searching Google Flights: {e}", file=sys.stderr)
        return []


def parse_results(text: str) -> list:
    """Parse Google Flights results from text."""
    flights = []
    
    # Pattern to match flight entries
    # Example: "22:00\n –\n23:18\nJetSMARTOperado por Jetsmart Airlines S.a.\n1 h 18 min\nCOR–AEP\nDirecto\n75 kg CO2e\n-18 % de emisiones\n30.493 ARS"
    
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for time pattern (HH:MM)
        if re.match(r'^\d{2}:\d{2}$', line):
            departure = line
            if i + 2 < len(lines) and lines[i + 1].strip() == '–':
                arrival = lines[i + 2].strip()
                
                # Look for airline name
                j = i + 3
                airline = ""
                while j < len(lines) and j < i + 10:
                    if 'Operado por' in lines[j]:
                        airline = lines[j].replace('Operado por', '').strip()
                        break
                    elif any(x in lines[j] for x in ['JetSMART', 'Aerolíneas', 'Flybondi', 'LATAM', 'GOL', 'Azul']):
                        airline = lines[j].strip()
                        break
                    j += 1
                
                # Look for duration
                duration = ""
                for k in range(j, min(j + 5, len(lines))):
                    if re.match(r'^\d+ h \d+ min$', lines[k].strip()):
                        duration = lines[k].strip()
                        break
                
                # Look for route
                route = ""
                for k in range(j, min(j + 5, len(lines))):
                    if '–' in lines[k] and any(x in lines[k] for x in ['COR', 'AEP', 'EZE', 'MDZ', 'BRC', 'SLA', 'ROS', 'TUC', 'NQN', 'IGR']):
                        route = lines[k].strip()
                        break
                
                # Look for price
                price = ""
                for k in range(j, min(j + 10, len(lines))):
                    if 'ARS' in lines[k]:
                        price_match = re.search(r'([\d.]+)\s*ARS', lines[k])
                        if price_match:
                            price = price_match.group(1)
                        break
                
                if departure and arrival and airline:
                    flights.append({
                        'departure': departure,
                        'arrival': arrival,
                        'airline': airline,
                        'duration': duration,
                        'route': route,
                        'price': price,
                        'source': 'Google Flights'
                    })
                
                i = j + 1
                continue
        
        i += 1
    
    return flights


def main():
    parser = argparse.ArgumentParser(description='Search flights in Argentina')
    parser.add_argument('--from', dest='from_airport', required=True, help='Origin airport code (e.g., COR)')
    parser.add_argument('--to', dest='to_airport', required=True, help='Destination airport code (e.g., AEP)')
    parser.add_argument('--date', required=True, help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--return', dest='return_date', help='Return date (YYYY-MM-DD)')
    parser.add_argument('--adults', type=int, default=1, help='Number of adults')
    
    args = parser.parse_args()
    
    print(f"Searching flights from {args.from_airport} to {args.to_airport} on {args.date}...")
    if args.return_date:
        print(f"Return: {args.return_date}")
    print()
    
    flights = search_google_flights(
        args.from_airport,
        args.to_airport,
        args.date,
        args.return_date,
        args.adults
    )
    
    if not flights:
        print("No flights found.")
        return
    
    # Sort by price
    def get_price(f):
        try:
            return float(f['price'].replace('.', '').replace(',', '.')) if f['price'] else float('inf')
        except:
            return float('inf')
    
    flights.sort(key=get_price)
    
    # Print results
    print(f"Found {len(flights)} flights:")
    print()
    print("| Hora | Aerolínea | Ruta | Duración | Precio | Fuente |")
    print("|------|-----------|------|----------|--------|--------|")
    
    for f in flights:
        time_str = f"{f['departure']} → {f['arrival']}"
        price_str = f"{f['price']} ARS" if f['price'] else "N/A"
        print(f"| {time_str} | {f['airline']} | {f['route']} | {f['duration']} | {price_str} | {f['source']} |")


if __name__ == '__main__':
    main()
