# Geolocation API Documentation

## Overview

The Geolocation API uses MaxMind GeoLite2 Country database to detect a user's country from their IP address. This is used primarily to determine the recommended currency (COP for Colombia, USD for all other countries).

## Database

- **Database**: MaxMind GeoLite2 Country
- **Location**: `/backend/geolocalization/GeoLite2-Country_20251024/GeoLite2-Country.mmdb`
- **Library**: `geoip2` (official MaxMind library)
- **Update Frequency**: Database should be updated monthly from MaxMind

## Endpoints

### 1. Detect Country by IP (POST)

Detect country from a specific IP address or auto-detect from client.

**Endpoint**: `POST /api/geolocation/detect/`

**Authentication**: Public (no authentication required)

**Request Body**:
```json
{
  "ip": "181.49.176.10"  // Optional - if not provided, uses client IP
}
```

**Response (Success)**:
```json
{
  "ip": "181.49.176.10",
  "country_code": "CO",
  "is_colombia": true,
  "recommended_currency": "COP"
}
```

**Response (IP not found)**:
```json
{
  "ip": "192.168.1.1",
  "country_code": null,
  "is_colombia": false,
  "recommended_currency": "USD",
  "message": "IP address not found in database"
}
```

**Response (Error)**:
```json
{
  "error": "Could not determine IP address"
}
```

### 2. Detect My Country (GET)

Auto-detect country from client's IP address.

**Endpoint**: `GET /api/geolocation/me/`

**Authentication**: Public (no authentication required)

**Response (Success)**:
```json
{
  "ip": "181.49.176.10",
  "country_code": "CO",
  "is_colombia": true,
  "recommended_currency": "COP"
}
```

## Usage Examples

### Frontend (JavaScript)

```javascript
// Auto-detect client's country
const response = await fetch('/api/geolocation/me/');
const data = await response.json();

if (data.is_colombia) {
  // Use COP currency
  currencyStore.setCurrency('COP');
} else {
  // Use USD currency
  currencyStore.setCurrency('USD');
}
```

```javascript
// Check specific IP
const response = await fetch('/api/geolocation/detect/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    ip: '181.49.176.10'
  })
});
const data = await response.json();
console.log(`Country: ${data.country_code}, Currency: ${data.recommended_currency}`);
```

### cURL Examples

```bash
# Auto-detect from client IP
curl -X GET http://localhost:8000/api/geolocation/me/

# Check specific IP
curl -X POST http://localhost:8000/api/geolocation/detect/ \
  -H "Content-Type: application/json" \
  -d '{"ip": "181.49.176.10"}'

# Auto-detect (no IP in body)
curl -X POST http://localhost:8000/api/geolocation/detect/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Currency Logic

- **Colombia (CO)**: Returns `COP` as recommended currency
- **All other countries**: Returns `USD` as recommended currency

## IP Detection

The service automatically detects the client's IP address from:

1. `X-Forwarded-For` header (if behind proxy/load balancer)
2. `REMOTE_ADDR` (direct connection)

This ensures accurate detection even when the application is behind a reverse proxy (e.g., Nginx, Cloudflare).

## Service Class

The `GeoLocationService` class provides the following methods:

```python
from crushme_app.utils.geolocation import GeoLocationService

# Get country code
country_code = GeoLocationService.get_country_code('181.49.176.10')
# Returns: 'CO'

# Check if Colombia
is_colombia = GeoLocationService.is_colombia('181.49.176.10')
# Returns: True

# Get recommended currency
currency = GeoLocationService.get_currency_by_ip('181.49.176.10')
# Returns: 'COP'

# Close the reader (optional, for cleanup)
GeoLocationService.close()
```

## Performance

- **Database size**: ~9.5 MB
- **Lookup time**: < 1ms (in-memory database)
- **Memory usage**: ~10 MB (database loaded in memory)
- **Singleton pattern**: Database reader is initialized once and reused

## Error Handling

- **IP not found**: Returns `null` for country_code, `false` for is_colombia, `USD` for currency
- **Invalid IP**: Returns error message
- **Database not found**: Raises `FileNotFoundError` on first use

## Updating the Database

To update the GeoLite2 database:

1. Download latest database from MaxMind: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
2. Extract the `.tar.gz` file
3. Replace the database file in `/backend/geolocalization/`
4. Update the path in `geolocation.py` if the folder name changed
5. Restart the Django application

## Integration with Currency System

This geolocation service integrates with the existing currency system:

1. Frontend calls `/api/geolocation/me/` on app initialization
2. Backend returns recommended currency based on country
3. Frontend sets currency in `currencyStore`
4. All subsequent API calls include `X-Currency` header
5. Backend converts prices accordingly

This replaces the previous external API calls (ipapi.co, ip-api.com) with a local, faster, and more reliable solution.
