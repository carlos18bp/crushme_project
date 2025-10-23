"""
Discount code model for promotional campaigns
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class DiscountCode(models.Model):
    """
    Discount code model for promotional campaigns
    Stores discount codes with their percentage values
    """
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Discount Code",
        help_text="Unique discount code (e.g., SUMMER2024, WELCOME10)"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Discount Percentage",
        help_text="Discount percentage (0-100)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether this discount code is currently active"
    )
    
    # Optional: Usage tracking
    times_used = models.PositiveIntegerField(
        default=0,
        verbose_name="Times Used",
        help_text="Number of times this code has been used"
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Max Uses",
        help_text="Maximum number of times this code can be used (leave empty for unlimited)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    class Meta:
        verbose_name = "Discount Code"
        verbose_name_plural = "Discount Codes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"
    
    def is_valid(self):
        """
        Check if discount code is valid for use
        """
        if not self.is_active:
            return False
        
        # Check if max uses exceeded
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False
        
        return True
    
    def increment_usage(self):
        """
        Increment the usage counter
        """
        self.times_used += 1
        self.save(update_fields=['times_used', 'updated_at'])
