"""
Cart views for CrushMe e-commerce application
Handles shopping cart operations: view, add, update, remove, clear
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from ..models import Cart, CartItem, Product
from ..serializers.cart_serializers import (
    CartSerializer, CartSummarySerializer, AddToCartSerializer,
    UpdateCartItemSerializer, CartCheckoutSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """
    Get user's shopping cart with all items
    Creates cart if it doesn't exist
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    serializer = CartSerializer(cart, context={'request': request})
    
    return Response({
        'cart': serializer.data,
        'is_new_cart': created
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart_summary(request):
    """
    Get lightweight cart summary (for header/navigation)
    """
    try:
        cart = Cart.objects.get(user=request.user)
        serializer = CartSummarySerializer(cart)
        
        return Response({
            'cart_summary': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Cart.DoesNotExist:
        return Response({
            'cart_summary': {
                'id': None,
                'total_items': 0,
                'total_price': '0.00',
                'items_count': 0
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Add a product to user's cart
    If item already exists, increase quantity
    """
    serializer = AddToCartSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            with transaction.atomic():
                # Get or create cart
                cart, created = Cart.objects.get_or_create(user=request.user)
                
                # Get product
                product = Product.objects.get(id=product_id)
                
                # Add product to cart
                cart_item = cart.add_product(product, quantity)
                
                # Return updated cart
                cart_serializer = CartSerializer(cart, context={'request': request})
                
                return Response({
                    'message': f'Added {quantity} x {product.name} to cart',
                    'cart': cart_serializer.data,
                    'added_item': {
                        'product_name': product.name,
                        'quantity': quantity,
                        'unit_price': str(cart_item.unit_price)
                    }
                }, status=status.HTTP_200_OK)
                
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'Failed to add item to cart',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """
    Update quantity of a specific cart item
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = cart.items.get(id=item_id)
    except Cart.DoesNotExist:
        return Response({
            'error': 'Cart not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except CartItem.DoesNotExist:
        return Response({
            'error': 'Cart item not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UpdateCartItemSerializer(
        data=request.data,
        context={'cart_item': cart_item}
    )
    
    if serializer.is_valid():
        new_quantity = serializer.validated_data['quantity']
        
        try:
            with transaction.atomic():
                # Update quantity
                cart_item.quantity = new_quantity
                cart_item.save()
                
                # Return updated cart
                cart_serializer = CartSerializer(cart, context={'request': request})
                
                return Response({
                    'message': f'Updated {cart_item.product.name} quantity to {new_quantity}',
                    'cart': cart_serializer.data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': 'Failed to update cart item',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, item_id):
    """
    Remove a specific item from cart
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = cart.items.get(id=item_id)
    except Cart.DoesNotExist:
        return Response({
            'error': 'Cart not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except CartItem.DoesNotExist:
        return Response({
            'error': 'Cart item not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    product_name = cart_item.product.name
    cart_item.delete()
    
    # Return updated cart
    cart_serializer = CartSerializer(cart, context={'request': request})
    
    return Response({
        'message': f'Removed {product_name} from cart',
        'cart': cart_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """
    Remove all items from user's cart
    """
    try:
        cart = Cart.objects.get(user=request.user)
        items_count = cart.items.count()
        cart.clear()
        
        # Return updated (empty) cart
        cart_serializer = CartSerializer(cart, context={'request': request})
        
        return Response({
            'message': f'Cleared {items_count} items from cart',
            'cart': cart_serializer.data
        }, status=status.HTTP_200_OK)
    
    except Cart.DoesNotExist:
        return Response({
            'message': 'Cart was already empty',
            'cart': {
                'id': None,
                'items': [],
                'total_items': 0,
                'total_price': '0.00',
                'is_empty': True
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_cart_for_checkout(request):
    """
    Validate cart items before checkout
    Check stock availability and product status
    """
    serializer = CartCheckoutSerializer(data={}, context={'request': request})
    
    if serializer.is_valid():
        cart = serializer.validated_data['cart']
        
        # Additional validation for checkout
        validation_errors = []
        
        for item in cart.items.all():
            if not item.product.is_active:
                validation_errors.append(f"{item.product.name} is no longer available")
            elif item.product.stock_quantity < item.quantity:
                validation_errors.append(
                    f"Only {item.product.stock_quantity} of {item.product.name} available"
                )
        
        if validation_errors:
            return Response({
                'error': 'Cart validation failed',
                'issues': validation_errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Cart is valid for checkout',
            'cart_summary': {
                'total_items': cart.total_items,
                'total_price': str(cart.total_price),
                'items_count': cart.items.count()
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Cart validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_to_cart_direct(request, product_id):
    """
    Directly add a specific product to cart (convenient endpoint)
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get quantity from request data, default to 1
    quantity = request.data.get('quantity', 1)
    
    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return Response({
            'error': 'Invalid quantity'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Use existing add_to_cart logic
    serializer = AddToCartSerializer(
        data={'product_id': product_id, 'quantity': quantity},
        context={'request': request}
    )
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item = cart.add_product(product, quantity)
                
                cart_serializer = CartSerializer(cart, context={'request': request})
                
                return Response({
                    'message': f'Added {quantity} x {product.name} to cart',
                    'cart': cart_serializer.data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': 'Failed to add item to cart',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart_item_count(request, product_id):
    """
    Get quantity of specific product in user's cart
    """
    try:
        cart = Cart.objects.get(user=request.user)
        product = Product.objects.get(id=product_id)
        quantity = cart.get_item_count_for_product(product)
        
        return Response({
            'product_id': product_id,
            'quantity_in_cart': quantity,
            'is_in_cart': quantity > 0
        }, status=status.HTTP_200_OK)
    
    except Cart.DoesNotExist:
        return Response({
            'product_id': product_id,
            'quantity_in_cart': 0,
            'is_in_cart': False
        }, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
