#!/usr/bin/env python
"""
Script to update retailer coordinates in the fixture file using Google Maps Geocoding API.
This uses the same geocoding logic as the RetailerSerializer.
"""
import json
import os
import sys
import requests
import urllib.parse
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLEMAPS_KEY = os.getenv('GOOGLEMAPS_KEY')
if not GOOGLEMAPS_KEY or GOOGLEMAPS_KEY == 'your-google-maps-api-key-here':
    print("ERROR: GOOGLEMAPS_KEY not set in .env file")
    print("Get a free key at https://developers.google.com/maps/documentation/geocoding/get-api-key")
    sys.exit(1)

FIXTURE_FILE = 'inventory/fixtures/initdata.json'

def geocode_address(street_address, city, postcode, country='USA'):
    """
    Geocode an address using Google Maps Geocoding API.
    Uses the same logic as RetailerSerializer.create()
    """
    # Build address string (currently hard-coded to CA like in serializer)
    address_string = f"{street_address}, {city}, CA {postcode if postcode else ''}"

    # Remove empty space at end of address_string
    query_params = {'address': address_string.strip(), 'key': GOOGLEMAPS_KEY}

    query_string = urllib.parse.urlencode(query_params)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?{query_string}"

    print(f"  Geocoding: {address_string.strip()}")

    try:
        response = requests.get(url)
        json_response = response.json()

        if json_response['status'] != 'OK':
            print(f"  WARNING: Geocoding failed with status: {json_response['status']}")
            return None, None

        results = json_response["results"]
        if len(results) > 0:
            location = results[0]["geometry"]["location"]
            lat = location["lat"]
            lon = location["lng"]
            print(f"  Found coordinates: {lat}, {lon}")
            return str(Decimal(lat)), str(Decimal(lon))
        else:
            print(f"  WARNING: No results found")
            return None, None

    except Exception as e:
        print(f"  ERROR: {e}")
        return None, None

def update_all_retailers():
    """
    Update the latitude and longitude for all retailers in the fixture file.
    """
    # Load the fixture file
    with open(FIXTURE_FILE, 'r') as f:
        data = json.load(f)

    # Find all retailer entries
    retailers = [item for item in data if item['model'] == 'inventory.retailer']

    print(f"Updating coordinates for {len(retailers)} retailers...\n")

    updated_count = 0
    for retailer in retailers:
        pk = retailer['pk']
        fields = retailer['fields']
        name = fields['name']

        print(f"Retailer #{pk}: {name}")
        print(f"  Current: {fields['latitude']}, {fields['longitude']}")

        # Geocode the address
        new_lat, new_lon = geocode_address(
            fields['street_address'],
            fields['city'],
            fields.get('postcode'),
            fields['country']
        )

        if new_lat and new_lon:
            # Update the coordinates in the data structure
            for item in data:
                if item['model'] == 'inventory.retailer' and item['pk'] == pk:
                    item['fields']['latitude'] = new_lat
                    item['fields']['longitude'] = new_lon
                    updated_count += 1
                    print(f"  Updated to: {new_lat}, {new_lon}")
                    break

        print()

    # Write the updated data back to the file
    if updated_count > 0:
        with open(FIXTURE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\nSuccessfully updated {updated_count} retailer(s) in {FIXTURE_FILE}")
    else:
        print(f"\nNo retailers were updated")

if __name__ == '__main__':
    update_all_retailers()
