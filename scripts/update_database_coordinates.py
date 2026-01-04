#!/usr/bin/env python
"""
Script to update retailer coordinates in the database using Django ORM.
This uses CRUD methods to update latitude/longitude for existing retailer records.
"""
import os
import sys
import django
import requests
import urllib.parse
from decimal import Decimal
from dotenv import load_dotenv

# Setup Django environment
# Add the parent directory to the path so we can import from the Django project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables before Django setup
load_dotenv()

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import Django models
from inventory.models import Retailer

GOOGLEMAPS_KEY = os.getenv('GOOGLEMAPS_KEY')
if not GOOGLEMAPS_KEY or GOOGLEMAPS_KEY == 'your-google-maps-api-key-here':
    print("ERROR: GOOGLEMAPS_KEY not set in .env file")
    print("Get a free key at https://developers.google.com/maps/documentation/geocoding/get-api-key")
    sys.exit(1)


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
            return Decimal(str(lat)), Decimal(str(lon))
        else:
            print(f"  WARNING: No results found")
            return None, None

    except Exception as e:
        print(f"  ERROR: {e}")
        return None, None


def update_all_retailers_in_database():
    """
    Update the latitude and longitude for all retailers in the database.
    Uses Django ORM CRUD operations (Read and Update).
    """
    # READ: Query all retailers from the database
    retailers = Retailer.objects.all().order_by('id')
    total_count = retailers.count()

    print(f"Updating coordinates for {total_count} retailers in database...\n")

    updated_count = 0
    skipped_count = 0

    for retailer in retailers:
        print(f"Retailer #{retailer.id}: {retailer.name}")
        print(f"  Current: {retailer.latitude}, {retailer.longitude}")

        # Geocode the address
        new_lat, new_lon = geocode_address(
            retailer.street_address,
            retailer.city,
            retailer.postcode,
            retailer.country
        )

        if new_lat and new_lon:
            # Check if coordinates changed
            if retailer.latitude != new_lat or retailer.longitude != new_lon:
                # UPDATE: Update the retailer record in the database
                retailer.latitude = new_lat
                retailer.longitude = new_lon
                retailer.save(update_fields=['latitude', 'longitude'])
                updated_count += 1
                print(f"  ✓ Updated to: {new_lat}, {new_lon}")
            else:
                skipped_count += 1
                print(f"  → Coordinates unchanged, skipping update")
        else:
            skipped_count += 1
            print(f"  ✗ Could not geocode, skipping update")

        print()

    print(f"\nSummary:")
    print(f"  Total retailers: {total_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped (unchanged or failed): {skipped_count}")


if __name__ == '__main__':
    # Check if database exists and has data
    try:
        count = Retailer.objects.count()
        if count == 0:
            print("WARNING: No retailers found in database.")
            print("Have you loaded the seed data? Run: ./manage.py loaddata initdata.json")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        print("Make sure PostgreSQL is running and the database exists.")
        sys.exit(1)

    update_all_retailers_in_database()
