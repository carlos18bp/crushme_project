"""
Product form based on candle_project implementation
"""
from django import forms
from django_attachments.models import Library
from ..models import Product

class ProductForm(forms.ModelForm):
    """
    Product form following candle_project pattern
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gallery'].required = False

    def save(self, commit=True):
        """
        Custom save method to handle gallery creation
        """
        obj = super().save(commit=False)
        if not hasattr(obj, 'gallery') or not obj.gallery:
            lib = Library()
            lib.save()
            obj.gallery = lib
        if commit:
            obj.save()
        return obj

    class Meta:
        model = Product
        fields = '__all__'
