# Wishlist Security and Currency Conversion Fix

## Issues Fixed

### 1. ❌ Sensitive Data Exposure (full_name)
**Problem:** Public wishlist endpoints were exposing user's `full_name` (first_name + last_name)

**Affected Endpoints:**
- `GET /api/wishlists/user/{username}/` - Was exposing `user_full_name`
- `GET /api/wishlists/@{username}/{wishlistId}/` - Was using `user_name` with full_name

**Solution:**
- Created new `WishListPublicListSerializer` for public endpoints
- Removed `user_full_name` from response
- Changed `user_name` to `user_username` (only exposes username or email prefix)
- Updated `WishListPublicSerializer` to use `user_username` instead of `user_name`

### 2. ❌ Currency Conversion Not Applied to total_value
**Problem:** `total_value` was always returned in COP regardless of `X-Currency` header

**Affected Endpoints:**
- `GET /api/wishlists/` - User's own wishlists
- `GET /api/wishlists/{wishlistId}/` - Specific wishlist detail
- `GET /api/wishlists/user/{username}/` - Public wishlists by username
- `GET /api/wishlists/@{username}/{wishlistId}/` - Public wishlist by username and ID

**Solution:**
- Added `get_total_value()` method to all serializers that returns model's `total_value` (in COP)
- Applied `convert_price_fields()` in all views to convert `total_value` to target currency
- Added `currency` field to all responses

### 3. ❌ Missing public_url and shareable_path
**Problem:** Some endpoints were not including wishlist sharing links

**Solution:**
- Added `public_url` and `shareable_path` to all serializers:
  - `WishListListSerializer`
  - `WishListPublicListSerializer`
  - `WishListDetailSerializer`
  - `WishListPublicSerializer`

---

## Changes Made

### Serializers (`crushme_app/serializers/wishlist_serializers.py`)

#### 1. WishListListSerializer (for authenticated user's own wishlists)
```python
class WishListListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for wishlist lists (for authenticated user's own wishlists)
    """
    user = UserSerializer(read_only=True)
    total_items = serializers.ReadOnlyField()
    total_value = serializers.SerializerMethodField()  # ✅ Now converted
    is_favorited = serializers.SerializerMethodField()
    public_url = serializers.ReadOnlyField()  # ✅ Added
    shareable_path = serializers.ReadOnlyField()  # ✅ Added
    
    def get_total_value(self, obj):
        """Calculate total value from item prices (will be converted later)"""
        return obj.total_value
```

#### 2. WishListPublicListSerializer (NEW - for public endpoints)
```python
class WishListPublicListSerializer(serializers.ModelSerializer):
    """
    Public serializer for wishlist lists (NO sensitive user data like full_name)
    Used for public endpoints like GET wishlists/user/{username}/
    """
    user_username = serializers.SerializerMethodField()  # ✅ Only username, NO full_name
    total_items = serializers.ReadOnlyField()
    total_value = serializers.SerializerMethodField()  # ✅ Will be converted
    public_url = serializers.ReadOnlyField()  # ✅ Added
    shareable_path = serializers.ReadOnlyField()  # ✅ Added
    
    def get_user_username(self, obj):
        """Get username or fallback to email prefix (NO full_name for privacy)"""
        return obj.user.username or obj.user.email.split('@')[0]
    
    def get_total_value(self, obj):
        """Calculate total value from item prices (will be converted later)"""
        return obj.total_value
```

#### 3. WishListDetailSerializer
```python
class WishListDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual wishlist views (authenticated user's own wishlist)
    """
    # ... existing fields ...
    total_value = serializers.SerializerMethodField()  # ✅ Now converted
    public_url = serializers.ReadOnlyField()  # ✅ Already had
    shareable_path = serializers.ReadOnlyField()  # ✅ Already had
    
    def get_total_value(self, obj):
        """Calculate total value from item prices (will be converted later)"""
        return obj.total_value
```

#### 4. WishListPublicSerializer
```python
class WishListPublicSerializer(serializers.ModelSerializer):
    """
    Serializer for public wishlist access (via UUID link or username)
    Limited information for privacy - NO full_name exposed
    """
    user_username = serializers.SerializerMethodField()  # ✅ Changed from user_name
    total_value = serializers.SerializerMethodField()  # ✅ Now converted
    public_url = serializers.ReadOnlyField()  # ✅ Added
    shareable_path = serializers.ReadOnlyField()  # ✅ Added
    
    def get_user_username(self, obj):
        """Get username for public view (NO full_name for privacy)"""
        return obj.user.username or obj.user.email.split('@')[0]
    
    def get_total_value(self, obj):
        """Calculate total value from item prices (will be converted later)"""
        return obj.total_value
```

---

### Views

#### 1. `get_user_wishlists_by_username()` (`wishlist_woocommerce_views.py`)
```python
@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_wishlists_by_username(request, username):
    # ... existing code ...
    
    # Get currency from request (set by CurrencyMiddleware)
    currency = getattr(request, 'currency', 'COP')
    
    # ✅ Use WishListPublicListSerializer (NO full_name)
    from ..serializers.wishlist_serializers import WishListPublicListSerializer
    serializer = WishListPublicListSerializer(wishlists, many=True, context={'request': request})
    
    # ✅ Convert prices to target currency
    from ..utils.price_helpers import convert_price_fields
    wishlists_data = convert_price_fields(serializer.data, currency)
    
    return Response({
        'success': True,
        'message': f'Wishlists de @{username}',
        'username': username,
        'user_id': user.id,
        # ❌ REMOVED: 'user_full_name': user.get_full_name(),
        'total_wishlists': wishlists.count(),
        'wishlists': wishlists_data,
        'currency': currency.upper()  # ✅ Added
    }, status=status.HTTP_200_OK)
```

#### 2. `get_wishlists()` (`wishlist_views.py`)
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wishlists(request):
    wishlists = WishList.objects.filter(user=request.user).order_by('-created_at')
    serializer = WishListListSerializer(wishlists, many=True, context={'request': request})
    
    # ✅ Get currency from request
    currency = getattr(request, 'currency', 'COP')
    
    # ✅ Convert prices to target currency
    from ..utils.price_helpers import convert_price_fields
    wishlists_data = convert_price_fields(serializer.data, currency)
    
    return Response({
        'wishlists': wishlists_data,
        'currency': currency.upper()  # ✅ Added
    }, status=status.HTTP_200_OK)
```

#### 3. `get_wishlist()` (`wishlist_views.py`)
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wishlist(request, wishlist_id):
    # ... existing code ...
    
    serializer = WishListDetailSerializer(wishlist, context={'request': request})
    
    # ✅ Get currency from request
    currency = getattr(request, 'currency', 'COP')
    
    # ✅ Convert prices to target currency
    from ..utils.price_helpers import convert_price_fields
    wishlist_data = convert_price_fields(serializer.data, currency)
    
    return Response({
        'wishlist': wishlist_data,
        'currency': currency.upper()  # ✅ Added
    }, status=status.HTTP_200_OK)
```

#### 4. `get_public_wishlist()` (`wishlist_views.py`)
```python
@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_wishlist(request, unique_link):
    # ... existing code ...
    
    serializer = WishListPublicSerializer(wishlist, context={'request': request})
    
    # ✅ Get currency from request
    currency = getattr(request, 'currency', 'COP')
    
    # ✅ Convert prices to target currency
    from ..utils.price_helpers import convert_price_fields
    wishlist_data = convert_price_fields(serializer.data, currency)
    
    return Response({
        'wishlist': wishlist_data,
        'currency': currency.upper()  # ✅ Added
    }, status=status.HTTP_200_OK)
```

#### 5. `get_public_wishlist_by_username()` (`wishlist_woocommerce_views.py`)
**Already had currency conversion** ✅ (from previous memory)

---

## Response Examples

### Before (❌ Issues)

#### GET /api/wishlists/user/cerrotico/
```json
{
  "success": true,
  "username": "cerrotico",
  "user_full_name": "Carlos Cerro",  // ❌ SENSITIVE DATA EXPOSED
  "wishlists": [
    {
      "id": 1,
      "name": "My Wishlist",
      "total_value": 25000,  // ❌ Always in COP
      // ❌ Missing public_url and shareable_path
    }
  ]
  // ❌ Missing currency field
}
```

#### GET /api/wishlists/@cerrotico/1/
```json
{
  "wishlist": {
    "id": 1,
    "user_name": "Carlos Cerro",  // ❌ SENSITIVE DATA EXPOSED
    "total_value": 25000,  // ❌ Always in COP
    // ❌ Missing public_url and shareable_path
  }
  // ❌ Missing currency field
}
```

### After (✅ Fixed)

#### GET /api/wishlists/user/cerrotico/ (with X-Currency: USD)
```json
{
  "success": true,
  "username": "cerrotico",
  "user_id": 123,
  "total_wishlists": 1,
  "wishlists": [
    {
      "id": 1,
      "name": "My Wishlist",
      "user_username": "cerrotico",  // ✅ Only username
      "total_value": 6.25,  // ✅ Converted to USD
      "public_url": "http://localhost:5173/@cerrotico/1",  // ✅ Added
      "shareable_path": "/@cerrotico/1",  // ✅ Added
      "total_items": 3,
      "is_active": true,
      "is_public": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "currency": "USD"  // ✅ Added
}
```

#### GET /api/wishlists/@cerrotico/1/ (with X-Currency: USD)
```json
{
  "wishlist": {
    "id": 1,
    "name": "My Wishlist",
    "user_username": "cerrotico",  // ✅ Only username (NO full_name)
    "total_value": 6.25,  // ✅ Converted to USD
    "public_url": "http://localhost:5173/@cerrotico/1",  // ✅ Added
    "shareable_path": "/@cerrotico/1",  // ✅ Added
    "total_items": 3,
    "items": [
      {
        "product_price": 2.08,  // ✅ Already converted (from previous fix)
        "product_info": {
          "price": 2.08  // ✅ Already converted
        }
      }
    ]
  },
  "currency": "USD"  // ✅ Added
}
```

#### GET /api/wishlists/ (with X-Currency: COP)
```json
{
  "wishlists": [
    {
      "id": 1,
      "name": "My Wishlist",
      "total_value": 25000,  // ✅ Integer for COP
      "public_url": "http://localhost:5173/@cerrotico/1",  // ✅ Added
      "shareable_path": "/@cerrotico/1",  // ✅ Added
      "user": {
        "username": "cerrotico",
        "full_name": "Carlos Cerro"  // ✅ OK for own wishlists
      }
    }
  ],
  "currency": "COP"  // ✅ Added
}
```

---

## Security Improvements

### ✅ Privacy Protected
- **Public endpoints** NO longer expose `full_name` (first_name + last_name)
- Only `username` or email prefix is shown in public views
- User's own wishlists still show full user data (authenticated endpoints)

### ✅ Proper Serializer Separation
- `WishListListSerializer` - For authenticated user's own wishlists (includes full user data)
- `WishListPublicListSerializer` - For public endpoints (NO sensitive data)
- `WishListDetailSerializer` - For authenticated user's own wishlist detail
- `WishListPublicSerializer` - For public wishlist access (NO sensitive data)

---

## Currency Conversion

### ✅ All Endpoints Now Convert total_value

| Endpoint | Currency Conversion |
|----------|---------------------|
| `GET /api/wishlists/` | ✅ Applied |
| `GET /api/wishlists/{wishlistId}/` | ✅ Applied |
| `GET /api/wishlists/user/{username}/` | ✅ Applied |
| `GET /api/wishlists/@{username}/{wishlistId}/` | ✅ Already had it |

### Format Rules
- **COP:** Integer without decimals (e.g., `25000`)
- **USD:** Float with 2 decimals (e.g., `6.25`)
- **Conversion rate:** 1 USD = 4000 COP (approximate)

---

## Sharing Links

### ✅ Always Included
All wishlist responses now include:
- `public_url` - Full URL for sharing (e.g., `"http://localhost:5173/@username/1"`)
- `shareable_path` - Relative path for routing (e.g., `"/@username/1"`)

These are generated from the WishList model properties:
```python
@property
def public_url(self):
    """Get the public sharing URL"""
    from django.conf import settings
    frontend_url = settings.FRONTEND_URL
    username = self.user.username or self.user.email.split('@')[0]
    return f"{frontend_url}/@{username}/{self.id}"

@property
def shareable_path(self):
    """Get just the path portion for frontend routing"""
    username = self.user.username or self.user.email.split('@')[0]
    return f"/@{username}/{self.id}"
```

---

## Files Modified

1. **crushme_app/serializers/wishlist_serializers.py**
   - Created `WishListPublicListSerializer` (NEW)
   - Updated `WishListListSerializer` (added public_url, shareable_path, get_total_value)
   - Updated `WishListDetailSerializer` (added get_total_value)
   - Updated `WishListPublicSerializer` (changed user_name to user_username, added links, get_total_value)

2. **crushme_app/views/wishlist_woocommerce_views.py**
   - Updated `get_user_wishlists_by_username()` (use WishListPublicListSerializer, apply currency conversion, remove full_name)

3. **crushme_app/views/wishlist_views.py**
   - Updated `get_wishlists()` (apply currency conversion)
   - Updated `get_wishlist()` (apply currency conversion)
   - Updated `get_public_wishlist()` (apply currency conversion)

---

## Testing

### Test Currency Conversion
```bash
# COP (default)
curl -H "X-Currency: COP" http://localhost:8000/api/wishlists/user/cerrotico/
# Expected: total_value as integer (e.g., 25000)

# USD
curl -H "X-Currency: USD" http://localhost:8000/api/wishlists/user/cerrotico/
# Expected: total_value as float (e.g., 6.25)
```

### Test Privacy (NO full_name)
```bash
curl http://localhost:8000/api/wishlists/user/cerrotico/
# Expected: user_username: "cerrotico" (NO user_full_name)

curl http://localhost:8000/api/wishlists/@cerrotico/1/
# Expected: user_username: "cerrotico" (NO user_name with full_name)
```

### Test Sharing Links
```bash
curl http://localhost:8000/api/wishlists/user/cerrotico/
# Expected: public_url and shareable_path in each wishlist
```

---

## Summary

✅ **Security:** Removed sensitive `full_name` from public endpoints  
✅ **Currency:** Applied conversion to `total_value` in all endpoints  
✅ **Links:** Added `public_url` and `shareable_path` to all responses  
✅ **Consistency:** All wishlist endpoints now follow the same pattern  
✅ **Privacy:** Proper serializer separation for public vs authenticated endpoints
