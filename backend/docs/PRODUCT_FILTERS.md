# Product Filters and Sorting

## Overview
The product list endpoint now supports multiple sorting options to help users find products based on different criteria.

## Endpoint
```
GET /api/products/woocommerce/products/
```

## Query Parameters

### Basic Parameters
- `category_id` (optional): Filter by WooCommerce category ID
- `per_page` (optional): Products per page (max 100, default 20)
- `page` (optional): Page number (default 1)
- `lang` (optional): Language (es/en)

### Sorting Parameter
- `sort_by` (optional): Sort products by specific criteria

## Available Sort Options

### 1. Popular (Most Purchased)
```
GET /api/products/woocommerce/products/?sort_by=popular
```
- Orders products by number of purchases (most sold first)
- Uses `OrderItem` table to count purchases
- Products with more sales appear first

### 2. Price: Low to High
```
GET /api/products/woocommerce/products/?sort_by=price_asc
```
- Orders products by price in ascending order
- Cheapest products appear first
- Useful for budget-conscious shoppers

### 3. Price: High to Low
```
GET /api/products/woocommerce/products/?sort_by=price_desc
```
- Orders products by price in descending order
- Most expensive products appear first
- Useful for premium product discovery

### 4. Best Rated
```
GET /api/products/woocommerce/products/?sort_by=rating
```
- Orders products by average rating (highest first)
- Uses `Review` table to calculate average rating
- Only considers active reviews
- Products without reviews appear last

### 5. Newest
```
GET /api/products/woocommerce/products/?sort_by=newest
```
- Orders products by creation date (newest first)
- Uses `date_created_wc` field from WooCommerce
- Shows latest additions to catalog

### 6. Default
```
GET /api/products/woocommerce/products/
```
- No sort_by parameter or invalid value
- Orders by WooCommerce ID descending
- Default behavior

## Combined Filters

You can combine sorting with other filters:

### Example 1: Popular products in a category
```
GET /api/products/woocommerce/products/?category_id=134&sort_by=popular
```

### Example 2: Cheapest products in English
```
GET /api/products/woocommerce/products/?sort_by=price_asc&lang=en
```

### Example 3: Best rated products with pagination
```
GET /api/products/woocommerce/products/?sort_by=rating&page=1&per_page=20
```

### Example 4: Newest products in a category
```
GET /api/products/woocommerce/products/?category_id=246&sort_by=newest&per_page=10
```

## Response Format

```json
{
  "success": true,
  "message": "Productos obtenidos desde base de datos local",
  "data": [
    {
      "id": 123,
      "name": "Product Name",
      "price": 50000,
      "currency": "COP",
      ...
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_products": 150,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  },
  "filters": {
    "category_id": null,
    "language": "es",
    "sort_by": "popular"
  },
  "source": "local_db"
}
```

## Performance Notes

### Fast Queries
- `price_asc` and `price_desc` - Direct field sorting (very fast)
- `newest` - Direct field sorting (very fast)
- `default` - Direct field sorting (very fast)

### Moderate Queries
- `popular` - Requires COUNT aggregation on OrderItem table
- `rating` - Requires AVG aggregation on Review table with subquery

**Recommendation:** For best performance, use indexed fields (price, date_created) when possible.

## Frontend Implementation

### JavaScript/Vue Example
```javascript
// Get popular products
const response = await axios.get('/api/products/woocommerce/products/', {
  params: {
    sort_by: 'popular',
    per_page: 20,
    page: 1
  }
});

// Get cheapest products in category
const response = await axios.get('/api/products/woocommerce/products/', {
  params: {
    category_id: 134,
    sort_by: 'price_asc',
    per_page: 20
  }
});

// Get best rated products
const response = await axios.get('/api/products/woocommerce/products/', {
  params: {
    sort_by: 'rating',
    lang: 'en'
  }
});
```

### React Example
```javascript
const [sortBy, setSortBy] = useState('popular');

const fetchProducts = async () => {
  const response = await fetch(
    `/api/products/woocommerce/products/?sort_by=${sortBy}&per_page=20`
  );
  const data = await response.json();
  return data;
};
```

## UI Dropdown Example

```html
<select v-model="sortBy" @change="fetchProducts">
  <option value="">Default</option>
  <option value="popular">Most Popular</option>
  <option value="price_asc">Price: Low to High</option>
  <option value="price_desc">Price: High to Low</option>
  <option value="rating">Best Rated</option>
  <option value="newest">Newest</option>
</select>
```

## Database Indexes

The following indexes optimize sorting performance:

**WooCommerceProduct:**
- `price` - For price sorting
- `date_created_wc` - For newest sorting
- `wc_id` - For default sorting

**OrderItem:**
- `woocommerce_product_id` - For popular sorting

**Review:**
- `woocommerce_product_id` - For rating sorting
- `is_active` - For filtering active reviews
- `rating` - For calculating averages

## Error Handling

### Invalid sort_by value
- Falls back to default sorting (by wc_id descending)
- No error returned, just uses default

### Invalid parameters
```json
{
  "error": "Parámetros inválidos",
  "details": "invalid literal for int() with base 10: 'abc'"
}
```

## Testing

### Test all sort options
```bash
# Popular
curl "http://localhost:8000/api/products/woocommerce/products/?sort_by=popular"

# Price ascending
curl "http://localhost:8000/api/products/woocommerce/products/?sort_by=price_asc"

# Price descending
curl "http://localhost:8000/api/products/woocommerce/products/?sort_by=price_desc"

# Best rated
curl "http://localhost:8000/api/products/woocommerce/products/?sort_by=rating"

# Newest
curl "http://localhost:8000/api/products/woocommerce/products/?sort_by=newest"

# Default
curl "http://localhost:8000/api/products/woocommerce/products/"
```

### Test with category filter
```bash
curl "http://localhost:8000/api/products/woocommerce/products/?category_id=134&sort_by=popular"
```

### Test with pagination
```bash
curl "http://localhost:8000/api/products/woocommerce/products/?sort_by=rating&page=2&per_page=10"
```

## Notes

1. **Currency Conversion**: All prices are automatically converted based on the `X-Currency` header
2. **Translations**: Product names and descriptions are translated based on `Accept-Language` header or `lang` parameter
3. **Margins**: Category price margins are automatically applied to all prices
4. **Stock**: Stock information is not included by default for performance (can be queried separately)
5. **Null Ratings**: Products without reviews will have `null` average rating and appear last when sorting by rating

## Future Enhancements

Potential additions:
- `on_sale` - Filter only products on sale
- `in_stock` - Filter only products in stock
- `price_range` - Filter by price range (min/max)
- `min_rating` - Filter by minimum rating
- `brand` - Filter by brand/manufacturer
