#!/bin/bash

# Manual Test Script for FindCokeZero
# Tests LANDING PAGE (HTML) and API ENDPOINTS (JSON)
#
# Landing Page Tests:
#   - GET / (HTML response)
#
# API Tests:
#   - Sodas endpoints (CRUD operations)
#   - Retailers endpoints (CRUD operations)
#   - Filtering endpoints (query parameters)
#   - Relationship endpoints (nested resources)
#
# Creates test data, performs operations, and cleans up afterward

# Configuration
LANDING_PAGE_URL="http://localhost:8000"
API_BASE_URL="http://localhost:8000/api"
CREATED_SODA_IDS=()
CREATED_RETAILER_IDS=()

# Check if jq is available for JSON formatting
if command -v jq &> /dev/null; then
    JQ_AVAILABLE=true
else
    JQ_AVAILABLE=false
fi

# ============================================
# UTILITY FUNCTIONS
# ============================================

print_separator() {
    echo "----------------------------------------"
}

print_test() {
    echo ""
    print_separator
    echo "Testing: $1"
    print_separator
}

print_section_header() {
    echo ""
    echo "========================================"
    echo "  $1"
    echo "========================================"
    echo ""
}

extract_id() {
    # Extract ID from JSON response
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$1" | jq -r '.id'
    else
        echo "$1" | grep -o '"id":[0-9]*' | grep -o '[0-9]*'
    fi
}

extract_url() {
    # Extract URL from JSON response
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$1" | jq -r '.url'
    else
        echo "$1" | grep -o '"url":"[^"]*"' | sed 's/"url":"\(.*\)"/\1/'
    fi
}

format_json() {
    # Format JSON if jq is available, otherwise return as-is
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$1" | jq '.'
    else
        echo "$1"
    fi
}

check_server() {
    print_test "Checking server connectivity"
    if curl -s "$LANDING_PAGE_URL/" > /dev/null 2>&1; then
        echo "Server is running at $LANDING_PAGE_URL"
        return 0
    else
        echo "Error: Server not running at $LANDING_PAGE_URL"
        echo "Start server with: ./manage.py runserver"
        return 1
    fi
}

# ============================================
# CLEANUP FUNCTION
# ============================================

cleanup() {
    print_test "Cleaning up test data"

    echo "Deleting created retailers..."
    for id in "${CREATED_RETAILER_IDS[@]}"; do
        echo "Deleting retailer ID: $id"
        curl -s -X DELETE "$API_BASE_URL/retailers/$id/"
        echo ""
    done

    echo "Deleting created sodas..."
    for id in "${CREATED_SODA_IDS[@]}"; do
        echo "Deleting soda ID: $id"
        curl -s -X DELETE "$API_BASE_URL/sodas/$id/"
        echo ""
    done

    echo "Cleanup complete!"
}

# ============================================
# API TESTS (JSON)
# ============================================

test_api_sodas_endpoints() {
    print_test "GET all sodas"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/sodas/")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    print_test "GET specific soda (ID: 1 from seed data)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/sodas/1/")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    print_test "POST create new soda"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_BASE_URL/sodas/" \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Soda", "abbreviation": "TS", "low_calorie": true}')
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    # Extract and store ID for cleanup
    new_soda_id=$(extract_id "$body")
    new_soda_url=$(extract_url "$body")
    CREATED_SODA_IDS+=("$new_soda_id")
    echo "Created soda ID: $new_soda_id"

    print_test "PATCH update soda (ID: $new_soda_id)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X PATCH "$API_BASE_URL/sodas/$new_soda_id/" \
        -H "Content-Type: application/json" \
        -d '{"name": "Updated Test Soda"}')
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"
}

test_api_retailers_endpoints() {
    print_test "GET all retailers"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/retailers/")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    print_test "GET specific retailer (ID: 1 from seed data)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/retailers/1/")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    print_test "POST create retailer without sodas"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_BASE_URL/retailers/" \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Store 001", "street_address": "123 Test Street", "city": "San Francisco"}')
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    # Extract and store ID for cleanup
    retailer_id_1=$(extract_id "$body")
    CREATED_RETAILER_IDS+=("$retailer_id_1")
    echo "Created retailer ID: $retailer_id_1"

    print_test "POST create retailer with sodas"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_BASE_URL/retailers/" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Test Store 002\", \"street_address\": \"456 Test Avenue\", \"city\": \"San Francisco\", \"sodas\": [\"$new_soda_url\"]}")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    # Extract and store ID for cleanup
    retailer_id_2=$(extract_id "$body")
    CREATED_RETAILER_IDS+=("$retailer_id_2")
    echo "Created retailer ID: $retailer_id_2"

    print_test "PATCH update retailer (ID: $retailer_id_1)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X PATCH "$API_BASE_URL/retailers/$retailer_id_1/" \
        -H "Content-Type: application/json" \
        -d '{"name": "Updated Test Store"}')
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"
}

test_api_filtering_endpoints() {
    print_test "GET retailers filtered by postcode (94109 from seed data)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/retailers/?postcode=94109")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    print_test "GET retailers filtered by postcode and single soda (94109, CZ from seed data)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/retailers/?postcode=94109&sodas=CZ")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    print_test "GET retailers filtered by postcode and multiple sodas (94108, CH,CZ from seed data)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/retailers/?postcode=94108&sodas=CH,CZ")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"
}

test_api_relationship_endpoints() {
    print_test "GET sodas at specific retailer (Retailer ID: 1 from seed data)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/retailers/1/sodas/")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"

    print_test "GET retailers carrying specific soda (Soda ID: 2 from seed data)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE_URL/sodas/2/retailers/")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"
    echo "Response:"
    format_json "$body"
}

# ============================================
# LANDING PAGE TESTS (HTML)
# ============================================

test_landing_page_html() {
    print_test "GET / (Landing Page - HTML)"
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$LANDING_PAGE_URL/")
    http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_STATUS/d')
    echo "Status: $http_code"

    # Check if response contains HTML
    if echo "$body" | grep -q "<html"; then
        echo "Response: HTML page received (showing first 500 characters)"
        echo "$body" | head -c 500
        echo "..."
    else
        echo "Response:"
        echo "$body"
    fi
}

# ============================================
# MAIN EXECUTION
# ============================================

main() {
    echo "========================================="
    echo "FindCokeZero Manual Test Script"
    echo "========================================="

    # Check server connectivity
    if ! check_server; then
        exit 1
    fi

    # LANDING PAGE TESTS (HTML)
    print_section_header "LANDING PAGE TESTS (HTML)"
    test_landing_page_html

    # API TESTS (JSON)
    print_section_header "API TESTS (JSON)"
    test_api_sodas_endpoints
    test_api_retailers_endpoints
    test_api_filtering_endpoints
    test_api_relationship_endpoints

    # Cleanup
    cleanup

    echo ""
    print_separator
    echo "All tests completed!"
    print_separator

    if [ "$JQ_AVAILABLE" = false ]; then
        echo ""
        echo "Tip: Install jq for prettier JSON formatting:"
        echo "  brew install jq"
    fi
}

# Run main function
main
