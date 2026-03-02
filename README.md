# 🛒 CrushMe - E-commerce Platform

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-v5.1.4-green.svg)
![Vue.js](https://img.shields.io/badge/vue.js-v3.5.13-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A complete e-commerce platform built with **Django REST Framework** and **Vue.js**, featuring shopping cart, wishlists, JWT authentication, and comprehensive order management.

## 🌟 Features

### 🔐 Authentication & User Management
- **JWT Authentication** with automatic token refresh
- **User Registration & Login** with email verification
- **Password Reset** functionality with secure codes
- **Google OAuth2** integration ready
- **User Profile** management with update capabilities

### 🛍️ E-commerce Core Features
- **Product Catalog** with categories and search
- **Shopping Cart** with guest and authenticated user support
- **Order Management** with multiple status tracking
- **Wishlist System** with public sharing capabilities
- **Favorite Wishlists** to bookmark others' lists

### 🎨 Frontend Features
- **Vue 3** with Composition API (`<script setup>`)
- **Pinia** for state management
- **Vue Router** with authentication guards
- **Responsive Design** with clean UI
- **Real-time** cart and wishlist updates

### ⚙️ Technical Features
- **REST API** with 43+ endpoints
- **Django Admin** interface with custom configurations
- **File Upload** support with django-attachments
- **Fake Data Generator** for development
- **CORS** configured for frontend-backend communication
- **Modular Architecture** for easy maintenance

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### 🖥️ Backend Setup (Django)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crushme_project
   ```

2. **Create virtual environment**
   ```bash
   cd backend
   python -m venv crushme_venv
   source crushme_venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Generate fake data (optional)**
   ```bash
   python manage.py create_fake_data
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

   🎉 Backend will be available at: `http://localhost:8000`
   📊 Admin panel: `http://localhost:8000/admin`
   📖 API Documentation: `http://localhost:8000/api/`

### 🎨 Frontend Setup (Vue.js)

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

   🎉 Frontend will be available at: `http://localhost:5173`

## 📁 Project Structure

```
crushme_project/
├── backend/                     # Django REST API
│   ├── crushme_project/         # Main project settings
│   │   ├── settings.py          # Django configuration
│   │   ├── urls.py              # Main URL routing
│   │   └── wsgi.py              # WSGI configuration
│   ├── crushme_app/             # Main application
│   │   ├── models/              # Database models
│   │   │   ├── user.py          # User & PasswordCode models
│   │   │   ├── product.py       # Product model with gallery
│   │   │   ├── cart.py          # Cart & CartItem models
│   │   │   ├── order.py         # Order & OrderItem models
│   │   │   └── wishlist.py      # Wishlist models
│   │   ├── serializers/         # DRF serializers
│   │   ├── views/               # API views with @api_view
│   │   ├── urls/                # URL routing by module
│   │   ├── admin.py             # Django admin configuration
│   │   └── management/commands/ # Custom management commands
│   └── requirements.txt         # Python dependencies
├── frontend/                    # Vue.js application
│   ├── src/
│   │   ├── views/               # Vue components (pages)
│   │   ├── stores/              # Pinia state management
│   │   │   └── modules/         # Store modules (auth, cart, etc.)
│   │   ├── services/            # HTTP service layer
│   │   ├── composables/         # Vue composables
│   │   ├── utils/               # Utility functions
│   │   ├── router/              # Vue Router configuration
│   │   └── App.vue              # Root component
│   ├── package.json             # Node.js dependencies
│   └── vite.config.js           # Vite configuration
└── README.md                    # This file
```

## 📡 API Endpoints

### 🔐 Authentication
- `POST /api/auth/sign_on/` - User registration
- `POST /api/auth/sign_on/send_verification_code/` - Send verification code
- `POST /api/auth/sign_in/` - User login
- `POST /api/auth/update_profile/` - Update user profile
- `POST /api/auth/update_password/` - Change password
- `POST /api/auth/send_passcode/` - Send password reset code
- `POST /api/auth/verify_passcode_and_reset_password/` - Verify reset code
- `POST /api/auth/google_login/` - Google OAuth2 login

### 🛍️ Products
- `GET /api/products/` - List products
- `GET /api/products/{id}/` - Product detail
- `GET /api/products/category/` - Products by category
- `GET /api/products/search/` - Search products
- `GET /api/products/categories/` - List categories
- `GET /api/products/featured/` - Featured products

### 🛒 Shopping Cart
- `GET /api/cart/` - Get user cart
- `GET /api/cart/summary/` - Get cart summary
- `POST /api/cart/add/` - Add product to cart
- `PUT /api/cart/items/{id}/update/` - Update cart item
- `DELETE /api/cart/items/{id}/remove/` - Remove cart item
- `DELETE /api/cart/clear/` - Clear cart
- `POST /api/cart/validate/` - Validate cart for checkout

### 📦 Orders
- `GET /api/orders/` - List user orders
- `GET /api/orders/{id}/` - Order detail
- `POST /api/orders/create/` - Create new order
- `POST /api/orders/{id}/cancel/` - Cancel order
- `GET /api/orders/track/{order_number}/` - Track order
- `GET /api/orders/recent/` - Get recent orders

### 💝 Wishlists
- `GET /api/wishlists/` - List user wishlists
- `POST /api/wishlists/create/` - Create wishlist
- `GET /api/wishlists/{id}/` - Wishlist detail
- `PUT /api/wishlists/{id}/update/` - Update wishlist
- `DELETE /api/wishlists/{id}/delete/` - Delete wishlist
- `POST /api/wishlists/{id}/add-product/` - Add product to wishlist
- `DELETE /api/wishlists/{id}/remove-product/{product_id}/` - Remove product
- `GET /api/wishlists/public/{uuid}/` - Public wishlist by UUID
- `GET /api/wishlists/public/` - Search public wishlists
- `POST /api/wishlists/{id}/favorite/` - Favorite wishlist
- `DELETE /api/wishlists/{id}/unfavorite/` - Unfavorite wishlist
- `GET /api/wishlists/favorites/` - List favorite wishlists

## 🗄️ Database Models

### User Model
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)  # Used as username
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
```

### Product Model
```python
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    stock_quantity = models.IntegerField(default=0)
    gallery = GalleryField(related_name='products_with_attachment')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Order Model
```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Wishlist Model
```python
class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    unique_link = models.UUIDField(default=uuid.uuid4, unique=True)
    shipping_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 🔧 Management Commands

The project includes several custom Django management commands for development:

### Generate Fake Data
```bash
# Generate all fake data (recommended)
python manage.py create_fake_data

# Or generate individually:
python manage.py create_fake_users --count 50
python manage.py create_fake_products --count 200
python manage.py create_fake_carts --count 30
python manage.py create_fake_orders --count 100
python manage.py create_fake_wishlists --count 25
```

### Delete Fake Data
```bash
# Remove all fake data (keeps superuser accounts)
python manage.py delete_fake_data --confirm

# Remove all data including superusers
python manage.py delete_fake_data --confirm --no-keep-superusers
```

## 🏪 State Management (Pinia)

### Available Stores
- **authStore** - User authentication and profile management
- **productStore** - Product catalog and search functionality
- **cartStore** - Shopping cart with guest support
- **orderStore** - Order history and tracking
- **wishlistStore** - Wishlist management and favorites

### Usage Example
```javascript
<script setup>
import { useAuthStore, useCartStore } from '@/stores'

const authStore = useAuthStore()
const cartStore = useCartStore()

// Login user
await authStore.login({ email, password })

// Add product to cart
await cartStore.addToCart(productId, quantity)
</script>
```

## 🚦 Frontend Routing

### Public Routes
- `/` - Home page
- `/products` - Product catalog
- `/products/:id` - Product detail
- `/cart` - Shopping cart

### Protected Routes (Require Authentication)
- `/checkout` - Checkout process
- `/orders` - Order history
- `/orders/:id` - Order detail
- `/wishlists` - User wishlists
- `/wishlists/:id` - Wishlist detail
- `/profile` - User profile

### Authentication Routes (Guest Only)
- `/login` - User login
- `/register` - User registration

## 🧪 Development

### Backend Testing
```bash
cd backend
python manage.py test
```

### Frontend Testing
```bash
cd frontend
npm run test
```

## 📚 Technologies Used

### Backend
- **Django 5.1.5** - Web framework
- **Django REST Framework** - API development
- **Simple JWT** - JWT authentication
- **django-cors-headers** - CORS handling
- **django-attachments** - File upload management
- **Pillow** - Image processing
- **Faker** - Fake data generation

### Frontend
- **Vue.js 3.5.13** - Progressive JavaScript framework
- **Pinia 3.0.3** - State management
- **Vue Router 4.5.1** - Client-side routing
- **Axios 1.11.0** - HTTP client
- **Vite 6.3.5** - Build tool and dev server

---

## Environment Configuration

This project uses environment variables for configuration. Copy the example file and configure:

```bash
cp backend/.env.example backend/.env
# Edit .env with your values
```

See `backend/.env.example` for all available options.

### Settings Structure

| File | Purpose |
|------|---------|
| `backend/crushme_project/settings.py` | Base/shared settings |
| `backend/crushme_project/settings_dev.py` | Development: DEBUG=True, SQLite, console email |
| `backend/crushme_project/settings_prod.py` | Production: DEBUG=False, MySQL, SMTP, security headers |

The active environment is controlled by `DJANGO_ENV` (`development` or `production`).

---

## Task Queue

This project uses [Huey](https://huey.readthedocs.io/) with Redis for background tasks.

- **Development**: Tasks run synchronously (no Redis required).
- **Production**: Tasks run asynchronously via the Huey worker process.

### Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `scheduled_backup` | Sundays 3:00 AM | Database and media backup with compression |
| `silk_garbage_collection` | Daily 3:30 AM | Clean Silk profiling data older than 7 days |
| `weekly_slow_queries_report` | Tuesdays 7:00 AM | Slow query and N+1 detection report |
| `silk_reports_cleanup` | 1st of month 5:30 AM | Clean old Silk report logs |

All tasks are defined in `backend/crushme_project/tasks.py`.

---

## Backups

Automated backups run weekly via the `scheduled_backup` Huey task. Backups are stored in the path configured by the `BACKUP_STORAGE_PATH` environment variable (default: `/var/backups/crushme_project/`) with 90-day retention.

Manual backup commands:

```bash
cd backend
source venv/bin/activate
python manage.py dbbackup --compress
python manage.py mediabackup --compress
```

---

## Performance Monitoring

Query profiling with [django-silk](https://github.com/jazzband/django-silk) is available behind the `ENABLE_SILK` environment variable flag.

Set `ENABLE_SILK=true` in your `.env` file to enable. Access at `/silk/` (staff users only).

Garbage collection runs daily at 3:30 AM. Weekly slow-query reports are generated Tuesdays at 7:00 AM.

---

## Documentation & Standards

Project standards and architecture guides are located in the `docs/` folder:

- `docs/DJANGO_VUE_ARCHITECTURE_STANDARD.md` — Architecture and project structure reference
- `docs/GLOBAL_RULES_GUIDELINES.md` — Development rules and engineering guidelines
- `docs/TESTING_QUALITY_STANDARDS.md` — Test quality criteria, patterns, and anti-patterns
- `docs/TEST_QUALITY_GATE_REFERENCE.md` — Quality gate tool reference and configuration
- `docs/BACKEND_AND_FRONTEND_COVERAGE_REPORT_STANDARD.md` — Coverage report standards
- `docs/E2E_FLOW_COVERAGE_REPORT_STANDARD.md` — E2E flow coverage tagging and report details
- `docs/deployment-guide.md` — Production deployment guide

---

## Production

- **Domain**: `crushme.com.co` / `www.crushme.com.co`
- **Services**: `gunicorn.service`, `crushme-huey.service`
- **Deploy**: See `docs/deployment-guide.md` or run `/deploy-and-check` workflow

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.