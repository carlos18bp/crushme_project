# Public Diary Endpoints - Status

## Overview

All diary-related endpoints are now configured as **public endpoints** (no authentication required). These endpoints allow anyone to view crush profiles, search for users, and browse the crush directory.

## Public Endpoints Summary

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/api/auth/public/@{username}/` | GET | ✅ Public | Get public profile by username |
| `/api/auth/crush/random/` | GET | ✅ Public | Get random crush profile |
| `/api/auth/crush/random-7/` | GET | ✅ Public | Get 7 random crushes |
| `/api/auth/crush/list/` | GET | ✅ Public | List all crushes with pagination |
| `/api/users/search/` | GET | ✅ Public | Search users by username |

## Endpoint Details

### 1. Get Public Profile by Username

**Endpoint**: `GET /api/auth/public/@{username}/`

**Authentication**: None (AllowAny)

**Query Parameters**:
- `lang` (optional): Language code (`es` or `en`)

**Example**:
```bash
GET /api/auth/public/@cerrotico/?lang=en
```

**Response**:
```json
{
  "success": true,
  "data": {
    "username": "cerrotico",
    "profile_picture_url": "...",
    "cover_image_url": "...",
    "about": "...",
    "links": [...],
    "current_status": "...",
    "note": "...",
    "gallery_photos": [...],
    "wishlists": [...]
  }
}
```

### 2. Get Random Crush

**Endpoint**: `GET /api/auth/crush/random/`

**Authentication**: None (AllowAny)

**Query Parameters**:
- `lang` (optional): Language code (`es` or `en`)

**Example**:
```bash
GET /api/auth/crush/random/?lang=en
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "username": "randomcrush",
    "profile_picture_url": "...",
    "current_status": "...",
    "note": "...",
    "is_crush": true
  }
}
```

### 3. Get 7 Random Crushes

**Endpoint**: `GET /api/auth/crush/random-7/`

**Authentication**: None (AllowAny)

**Query Parameters**:
- `lang` (optional): Language code (`es` or `en`)

**Example**:
```bash
GET /api/auth/crush/random-7/?lang=en
```

**Response**:
```json
{
  "success": true,
  "count": 7,
  "results": [
    {
      "id": 1,
      "username": "crush1",
      "profile_picture_url": "...",
      "current_status": "...",
      "note": "...",
      "is_crush": true
    },
    ...
  ]
}
```

### 4. List All Crushes

**Endpoint**: `GET /api/auth/crush/list/`

**Authentication**: None (AllowAny)

**Query Parameters**:
- `limit` (optional): Number of results per page (default: 20, max: 50)
- `offset` (optional): Pagination offset (default: 0)
- `lang` (optional): Language code (`es` or `en`)

**Example**:
```bash
GET /api/auth/crush/list/?limit=10&offset=0&lang=en
```

**Response**:
```json
{
  "success": true,
  "count": 10,
  "total": 45,
  "next": 10,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "crush1",
      "profile_picture_url": "...",
      "current_status": "...",
      "note": "...",
      "is_crush": true
    },
    ...
  ]
}
```

### 5. Search Users

**Endpoint**: `GET /api/users/search/`

**Authentication**: None (AllowAny)

**Query Parameters**:
- `q` (required): Search query (username)
- `limit` (optional): Max results (default: 20, max: 50)
- `lang` (optional): Language code (`es` or `en`)

**Example**:
```bash
GET /api/users/search/?q=cerro&limit=10&lang=en
```

**Response**:
```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "id": 1,
      "username": "cerrotico",
      "profile_picture_url": "...",
      "is_crush": true
    },
    ...
  ]
}
```

## Implementation Details

All endpoints use the `@permission_classes([AllowAny])` decorator to allow unauthenticated access:

```python
@api_view(['GET'])
@permission_classes([AllowAny])
def get_crush_public_profile(request, username):
    # ...
```

## Frontend Integration

These endpoints can be called directly from the frontend without authentication:

```javascript
// Get public profile
const response = await fetch(`/api/auth/public/@${username}/?lang=en`);
const data = await response.json();

// Get random crush
const response = await fetch('/api/auth/crush/random/?lang=en');
const data = await response.json();

// Search users
const response = await fetch(`/api/users/search/?q=${query}&limit=10&lang=en`);
const data = await response.json();

// List crushes
const response = await fetch('/api/auth/crush/list/?limit=20&offset=0&lang=en');
const data = await response.json();
```

## Use Cases

1. **Public Diaries/Profiles**: Anyone can view crush profiles without logging in
2. **Discovery**: Random crush feature for homepage/carousel
3. **Search**: Find crushes by username
4. **Browse**: Paginated list of all crushes
5. **Wishlist Sharing**: Public wishlist links work without authentication

## Security Notes

- These endpoints only return **public** information
- Private user data is not exposed
- Rate limiting should be considered for production
- CORS headers should be configured appropriately

## Changes Made

**File**: `crushme_app/views/auth_views.py`

**Modified Functions**:
1. `get_random_crush()` - Added `@permission_classes([AllowAny])`
2. `search_users()` - Added `@permission_classes([AllowAny])`

**Already Public** (no changes needed):
1. `get_crush_public_profile()` - Already had `@permission_classes([AllowAny])`
2. `list_crushes()` - Already had `@permission_classes([AllowAny])`
3. `get_random_crushes()` - Already had `@permission_classes([AllowAny])`

## Testing

All endpoints can be tested without authentication:

```bash
# Test public profile
curl http://localhost:8000/api/auth/public/@cerrotico/?lang=en

# Test random crush
curl http://localhost:8000/api/auth/crush/random/?lang=en

# Test search
curl "http://localhost:8000/api/users/search/?q=cerro&limit=10&lang=en"

# Test list crushes
curl "http://localhost:8000/api/auth/crush/list/?limit=20&offset=0&lang=en"

# Test 7 random crushes
curl http://localhost:8000/api/auth/crush/random-7/?lang=en
```

All requests should return data without requiring authentication headers.
