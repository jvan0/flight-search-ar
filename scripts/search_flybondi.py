#!/usr/bin/env python3
"""
Search flights on Flybondi directly via their API.
Flybondi is a low-cost airline in Argentina.

NOTE (verified 2026-10-07): api.flybondi.com does not resolve from the
public internet and www.flybondi.com blocks automated access (Cloudflare),
so this script is best-effort. If it returns no flights, search manually
at https://www.flybondi.com/
"""

import argparse
import json
import sys
import requests
from datetime import datetime


# Flybondi airport codes
FLYBONDI_AIRPORTS = {
    'COR': {'code': 'COR', 'name': 'Córdoba'},
    'AEP': {'code': 'AEP', 'name': 'Buenos Aires (Aeroparque)'},
    'EZE': {'code': 'EZE', 'name': 'Buenos Aires (Ezeiza)'},
    'MDZ': {'code': 'MDZ', 'name': 'Mendoza'},
    'BRC': {'code': 'BRC', 'name': 'Bariloche'},
    'SLA': {'code': 'SLA', 'name': 'Salta'},
    'ROS': {'code': 'ROS', 'name': 'Rosario'},
    'TUC': {'code': 'TUC', 'name': 'Tucumán'},
    'NQN': {'code': 'NQN', 'name': 'Neuquén'},
    'IGR': {'code': 'IGR', 'name': 'Iguazú'},
    'Jujuy': {'code': 'JUJ', 'name': 'Jujuy'},
    'Misiones': {'code': 'PSS', 'name': 'Posadas'},
}


def search_flybondi(from_airport: str, to_airport: str, date: str, adults: int = 1) -> list:
    """
    Search flights on Flybondi.
    
    Flybondi uses a REST API that can be queried directly.
    """
    flights = []
    
    # Flybondi API endpoint (internal API used by their website)
    # This is the API that the Flybondi website uses to search flights
    url = "https://api.flybondi.com/v1/flights/search"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'es-AR,es;q=0.9',
        'Origin': 'https://www.flybondi.com',
        'Referer': 'https://www.flybondi.com/',
    }
    
    params = {
        'origin': from_airport,
        'destination': to_airport,
        'departureDate': date,
        'adults': adults,
        'children': 0,
        'infants': 0,
        'tripType': 'ONE_WAY',
        'currency': 'ARS',
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"Flybondi API returned status {response.status_code}", file=sys.stderr)
            return []
        
        data = response.json()
        
        # Parse Flybondi response
        # The response structure may vary, but typically contains:
        # - flights: array of flight options
        #   - departureTime, arrivalTime, price, etc.
        
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
        elif 'data' in data and 'flights' in data['data']:
            for flight in data['data']['flights']:
                flights.append({
                    'departure': flight.get('departureTime', ''),
                    'arrival': flight.get('arrivalTime', ''),
                    'airline': 'Flybondi',
                    'duration': flight.get('duration', ''),
                    'route': f"{from_airport}–{to_airport}",
                    'price': flight.get('price', ''),
                    'source': 'Flybondi'
                })
        else:
            # Try to find any flight data in the response
            print(f"Unexpected Flybondi response structure: {json.dumps(data, indent=2)[:500]}", file=sys.stderr)
            
    except requests.exceptions.RequestException as e:
        print(f"Error querying Flybondi API: {e}", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"Error parsing Flybondi response: {e}", file=sys.stderr)
    
    return flights


def main():
    parser = argparse.ArgumentParser(description='Search flights on Flybondi')
    parser.add_argument('--from', dest='from_airport', required=True, help='Origin airport code')
    parser.add_argument('--to', dest='to_airport', required=True, help='Destination airport code')
    parser.add_argument('--date', required=True, help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--adults', type=int, default=1, help='Number of adults')
    
    args = parser.parse_args()
    
    print(f"Searching Flybondi flights from {args.from_airport} to {args.to_airport} on {args.date}...")
    print()
    
    flights = search_flybondi(args.from_airport, args.to_airport, args.date, args.adults)
    
    if not flights:
        print("No flights found on Flybondi.")
        return
    
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
