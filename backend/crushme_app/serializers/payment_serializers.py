"""Input contracts for public checkout endpoints."""

from rest_framework import serializers


class CheckoutItemInputSerializer(serializers.Serializer):
    woocommerce_product_id = serializers.IntegerField(min_value=1)
    woocommerce_variation_id = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )
    variation_id = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    def validate(self, attrs):
        canonical_id = attrs.get('woocommerce_variation_id')
        legacy_id = attrs.get('variation_id')
        if canonical_id and legacy_id and canonical_id != legacy_id:
            raise serializers.ValidationError('Conflicting variation IDs')
        attrs['variation_id'] = canonical_id or legacy_id
        return attrs


class CheckoutInputSerializer(serializers.Serializer):
    items = CheckoutItemInputSerializer(many=True, min_length=1, max_length=50)
    customer_email = serializers.EmailField(max_length=254)
    customer_name = serializers.CharField(max_length=200)
    shipping_address = serializers.CharField(max_length=255)
    shipping_address_line_2 = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='',
    )
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100, default='CO')
    phone_number = serializers.CharField(max_length=32, required=False, allow_blank=True, default='')
    notes = serializers.CharField(max_length=2000, required=False, allow_blank=True, default='')
    gift_message = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        default='',
    )
    is_gift = serializers.BooleanField(required=False, default=False)
    sender_username = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    receiver_username = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    is_from_wishlist = serializers.BooleanField(required=False, default=False)
    wishlist_id = serializers.CharField(
        max_length=64,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    wishlist_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    discount_code = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )

    def validate(self, attrs):
        if attrs['is_gift'] and not attrs.get('receiver_username'):
            raise serializers.ValidationError({
                'receiver_username': 'This field is required for gifts.'
            })
        return attrs
