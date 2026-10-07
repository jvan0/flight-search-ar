#!/usr/bin/env python3
"""
Search all flight sources in Argentina and compare prices.
Combines Google Flights, Flybondi API, and Anduin Promos API.
"""

import argparse
import json
import sys
import requests
from datetime import datetime


def _browser_available() -> bool:
    """Check whether the browser_helpers module is importable.

    Standalone installs usually don't have it; the Google Flights
    functions degrade to an empty result with a warning instead of
    failing silently.
    """
    import os

    helper_path = os.environ.get("BROWSER_HELPERS_PATH", "./browser-helpers")
    if helper_path not in sys.path:
        sys.path.insert(0, helper_path)
    try:
        import importlib.util

        return importlib.util.find_spec("browser_helpers") is not None
    except Exception:
        return False


def search_anduin_promos() -> list:
    """Search Anduin Promos API for flight deals."""
    url = "https://anduin.ferminrp.com/api/v1/promos"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return []
        
        data = response.json()
        if not data.get('success'):
            return []
        
        promos = data.get('data', {}).get('promos', [])
        flight_promos = [p for p in promos if p.get('category') == 'vuelos']
        
        results = []
        for p in flight_promos:
            results.append({
                'title': p.get('title', ''),
                'date': p.get('date', ''),
                'destination': p.get('destinationCountry', ''),
                'score': p.get('score', 0),
                'permalink': p.get('permalink', ''),
                'source': 'Anduin Promos'
            })
        
        return results
    except Exception as e:
        print(f"Error querying Anduin API: {e}", file=sys.stderr)
        return []


def search_google_flights_browser(from_airport: str, to_airport: str, date: str) -> list:
    """Search Google Flights using browser automation."""
    import subprocess

    if not _browser_available():
        print(
            "Google Flights search skipped: browser automation module "
            "'browser_helpers' not found. Set BROWSER_HELPERS_PATH to the "
            "directory that provides it, or rely on --include-promos "
            "(Anduin API) and the Flybondi script for standalone sources.",
            file=sys.stderr,
        )
        return []
    
    url = f"https://www.google.com/travel/flights?q=Flights+from+{from_airport}+to+{to_airport}+on={date}+one+way&hl=es&curr=ARS"
    
    try:
        result = subprocess.run(
            ["python3", "-c", f"""
import sys
import os
sys.path.insert(0, os.environ.get('BROWSER_HELPERS_PATH', './browser-helpers'))
from browser_helpers import new_tab, wait_for_load, js
import time

new_tab('{url}')
wait_for_load()
time.sleep(3)

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
            return []
        
        return parse_google_flights(result.stdout, from_airport, to_airport)
    except Exception as e:
        print(f"Error searching Google Flights: {e}", file=sys.stderr)
        return []


def parse_google_flights(text: str, from_airport: str, to_airport: str) -> list:
    """Parse Google Flights results from text."""
    import re
    
    flights = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if re.match(r'^\d{2}:\d{2}$', line):
            departure = line
            if i + 2 < len(lines) and lines[i + 1].strip() == '–':
                arrival = lines[i + 2].strip()
                
                # Find airline
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
                
                # Find duration
                duration = ""
                for k in range(j, min(j + 5, len(lines))):
                    if re.match(r'^\d+ h \d+ min$', lines[k].strip()):
                        duration = lines[k].strip()
                        break
                
                # Find price
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
                        'route': f"{from_airport}–{to_airport}",
                        'price': price,
                        'source': 'Google Flights'
                    })
                
                i = j + 1
                continue
        
        i += 1
    
    return flights


def search_flybondi_api(from_airport: str, to_airport: str, date: str) -> list:
    """Search Flybondi API."""
    url = "https://api.flybondi.com/v1/flights/search"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Origin': 'https://www.flybondi.com',
        'Referer': 'https://www.flybondi.com/',
    }
    
    params = {
        'origin': from_airport,
        'destination': to_airport,
        'departureDate': date,
        'adults': 1,
        'children': 0,
        'infants': 0,
        'tripType': 'ONE_WAY',
        'currency': 'ARS',
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            return []
        
        data = response.json()
        flights = []
        
        if 'flights' in data:
            for flight in data['flights']:
                flights.append({
                    'departure': flight.get('departureTime', ''),
                    'arrival': flight.get('arrivalTime', ''),
                    'airline': 'Flybondi',
                    'duration': flight.get('duration', ''),
                    'route': f"{from_airport}–{to_airport}",
                    'price': flight.get('price', ''),
                    'source': 'Flybondi'
                })
        
        return flights
    except Exception as e:
        print(f"Error querying Flybondi: {e}", file=sys.stderr)
        print(
            "Hint: api.flybondi.com does not resolve from the public "
            "internet (verified 2026-10-07) and www.flybondi.com blocks "
            "bots (Cloudflare). Search manually at "
            "https://www.flybondi.com/",
            file=sys.stderr,
        )
        return []


def main():
    parser = argparse.ArgumentParser(description='Search all flight sources in Argentina')
    parser.add_argument('--from', dest='from_airport', required=True, help='Origin airport code')
    parser.add_argument('--to', dest='to_airport', required=True, help='Destination airport code')
    parser.add_argument('--date', required=True, help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--return', dest='return_date', help='Return date (YYYY-MM-DD)')
    parser.add_argument('--adults', type=int, default=1, help='Number of adults')
    parser.add_argument('--include-promos', action='store_true', help='Include Anduin promos')
    
    args = parser.parse_args()
    
    print(f"Searching flights from {args.from_airport} to {args.to_airport} on {args.date}...")
    if args.return_date:
        print(f"Return: {args.return_date}")
    print()
    
    all_flights = []
    
    # Search Google Flights
    print("Searching Google Flights...")
    google_flights = search_google_flights_browser(args.from_airport, args.to_airport, args.date)
    all_flights.extend(google_flights)
    print(f"  Found {len(google_flights)} flights")
    
    # Search Flybondi
    print("Searching Flybondi...")
    flybondi_flights = search_flybondi_api(args.from_airport, args.to_airport, args.date)
    all_flights.extend(flybondi_flights)
    print(f"  Found {len(flybondi_flights)} flights")
    
    # Search return flights if specified
    if args.return_date:
        print(f"Searching return flights ({args.return_date})...")
        google_return = search_google_flights_browser(args.to_airport, args.from_airport, args.return_date)
        all_flights.extend(google_return)
        print(f"  Found {len(google_return)} return flights")
    
    # Search Anduin promos
    if args.include_promos:
        print("Searching Anduin promos...")
        promos = search_anduin_promos()
        print(f"  Found {len(promos)} flight promos")
    
    if not all_flights and not (args.include_promos and promos):
        print("\nNo flights found.")
        return
    
    # Sort by price
    def get_price(f):
        try:
            return float(f['price'].replace('.', '').replace(',', '.')) if f['price'] else float('inf')
        except:
            return float('inf')
    
    all_flights.sort(key=get_price)
    
    # Print results
    print(f"\nFound {len(all_flights)} flights:")
    print()
    print("| Hora | Aerolínea | Ruta | Duración | Precio | Fuente |")
    print("|------|-----------|------|----------|--------|--------|")
    
    for f in all_flights:
        time_str = f"{f['departure']} → {f['arrival']}"
        price_str = f"{f['price']} ARS" if f['price'] else "N/A"
        print(f"| {time_str} | {f['airline']} | {f['route']} | {f['duration']} | {price_str} | {f['source']} |")
    
    # Print promos if available
    if args.include_promos and promos:
        print("\n\nPromociones de vuelos (Anduin):")
        print()
        for p in promos[:10]:
            print(f"- {p['title']}")
            print(f"  Destino: {p['destination']} | Score: {p['score']}")
            print(f"  Link: {p['permalink']}")
            print()


if __name__ == '__main__':
    main()
