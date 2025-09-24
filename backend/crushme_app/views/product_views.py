"""
Product views for CrushMe e-commerce application
Handles product CRUD operations, search, and category management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from ..models import Product
from ..serializers.product_serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductSearchSerializer, ProductCategorySerializer, ProductStockUpdateSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    """
    Get list of all active products
    """
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'products': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product(request, product_id):
    """
    Get detailed information about a specific product
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductDetailSerializer(product, context={'request': request})
    
    return Response({
        'product': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products_by_category(request):
    """
    Get products filtered by category
    """
    category = request.query_params.get('category')
    
    if not category:
        return Response({
            'error': 'Category parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate category exists
    valid_categories = [choice[0] for choice in Product.CATEGORY_CHOICES]
    if category not in valid_categories:
        return Response({
            'error': 'Invalid category',
            'valid_categories': valid_categories
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get products
    products = Product.objects.filter(category=category, is_active=True).order_by('-created_at')
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'products': serializer.data,
        'category': category,
        'category_display': dict(Product.CATEGORY_CHOICES).get(category)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    """
    Search products by name or description
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response({
            'error': 'Search query is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(query) < 2:
        return Response({
            'error': 'Search query must be at least 2 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Search products
    products = Product.search_products(query)
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'products': serializer.data,
        'query': query
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    """
    Get all product categories with product counts
    """
    categories = ProductCategorySerializer.get_categories_with_counts()
    
    return Response({
        'categories': categories
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_product(request):
    """
    Create a new product (Admin only)
    """
    serializer = ProductCreateUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        product = serializer.save()
        detail_serializer = ProductDetailSerializer(product, context={'request': request})
        
        return Response({
            'message': 'Product created successfully',
            'product': detail_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_product(request, product_id):
    """
    Update an existing product (Admin only)
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
    
    if serializer.is_valid():
        product = serializer.save()
        detail_serializer = ProductDetailSerializer(product, context={'request': request})
        
        return Response({
            'message': 'Product updated successfully',
            'product': detail_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_product(request, product_id):
    """
    Delete a product (Admin only)
    Soft delete by setting is_active to False
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Soft delete
    product.is_active = False
    product.save()
    
    return Response({
        'message': 'Product deleted successfully'
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_product_stock(request, product_id):
    """
    Update product stock quantity (Admin only)
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductStockUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        new_stock = serializer.validated_data['stock_quantity']
        product.stock_quantity = new_stock
        product.save()
        
        return Response({
            'message': 'Stock updated successfully',
            'product_id': product.id,
            'new_stock': new_stock,
            'is_in_stock': product.is_in_stock
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_products(request):
    """
    Get featured products (latest products or high-rated ones)
    """
    # For now, return latest products
    # In future, this could be based on ratings, sales, or admin selection
    products = Product.objects.filter(
        is_active=True,
        stock_quantity__gt=0
    ).order_by('-created_at')[:12]
    
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    
    return Response({
        'featured_products': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_recommendations(request, product_id):
    """
    Get product recommendations based on category
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get similar products from same category
    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        stock_quantity__gt=0
    ).exclude(id=product.id).order_by('?')[:8]  # Random order
    
    serializer = ProductListSerializer(similar_products, many=True, context={'request': request})
    
    return Response({
        'recommendations': serializer.data,
        'based_on': {
            'product_id': product.id,
            'product_name': product.name,
            'category': product.category
        }
    }, status=status.HTTP_200_OK)
