"""
Currency conversion utilities for price handling
"""
import requests
from django.core.cache import cache
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """
    Handle currency conversion with caching to avoid excessive API calls.
    Uses exchangerate-api.com for real-time exchange rates.
    """
    
    # Free API endpoint (no key required for basic usage)
    # For production, consider getting a free API key at https://www.exchangerate-api.com/
    API_URL = "https://open.er-api.com/v6/latest/COP"
    
    # Cache exchange rates for 1 hour
    CACHE_TIMEOUT = 3600
    CACHE_KEY = "exchange_rate_cop_to_usd"
    
    # Fallback rate if API fails (approximate)
    FALLBACK_RATE = 0.00025  # 1 COP ≈ 0.00025 USD (1 USD ≈ 4000 COP)
    
    @classmethod
    def get_exchange_rate(cls):
        """
        Get COP to USD exchange rate.
        Uses cache to minimize API calls.
        
        Returns:
            float: Exchange rate (COP to USD)
        """
        # Try to get from cache first
        cached_rate = cache.get(cls.CACHE_KEY)
        if cached_rate:
            logger.debug(f"Using cached exchange rate: {cached_rate}")
            return cached_rate
        
        # Fetch from API
        try:
            response = requests.get(cls.API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result') == 'success':
                # Get USD rate from COP base
                usd_rate = data['rates'].get('USD')
                
                if usd_rate:
                    # Cache the rate
                    cache.set(cls.CACHE_KEY, usd_rate, cls.CACHE_TIMEOUT)
                    logger.info(f"Fetched new exchange rate: 1 COP = {usd_rate} USD")
                    return usd_rate
        
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch exchange rate: {e}")
        except (KeyError, ValueError) as e:
            logger.warning(f"Invalid exchange rate data: {e}")
        
        # Use fallback rate
        logger.warning(f"Using fallback exchange rate: {cls.FALLBACK_RATE}")
        return cls.FALLBACK_RATE
    
    @classmethod
    def convert_cop_to_usd(cls, amount_cop):
        """
        Convert COP amount to USD.
        
        Args:
            amount_cop: Amount in Colombian Pesos
            
        Returns:
            float: Amount in US Dollars (rounded to 2 decimals)
        """
        if amount_cop is None:
            return None
        
        try:
            amount_cop = float(amount_cop)
            rate = cls.get_exchange_rate()
            amount_usd = amount_cop * rate
            
            # Round to 2 decimal places
            return round(amount_usd, 2)
        
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting {amount_cop} COP to USD: {e}")
            return None
    
    @classmethod
    def convert_price(cls, price, target_currency):
        """
        Convert price to target currency.
        
        Args:
            price: Price amount (assumed to be in COP)
            target_currency: Target currency code ('COP' or 'USD')
            
        Returns:
            float/int: Converted price (int for COP, float for USD)
        """
        if price is None:
            return None
        
        target_currency = target_currency.upper()
        
        if target_currency == 'COP':
            # Return as integer (no decimals in Colombian pesos)
            return int(round(float(price)))
        
        elif target_currency == 'USD':
            # Convert to USD (keep 2 decimals)
            return cls.convert_cop_to_usd(price)
        
        else:
            # Unknown currency, return as-is
            logger.warning(f"Unknown currency: {target_currency}, returning COP price")
            return int(round(float(price)))
    
    @classmethod
    def get_current_rate_info(cls):
        """
        Get current exchange rate information for display/debugging.
        
        Returns:
            dict: Exchange rate information
        """
        rate = cls.get_exchange_rate()
        return {
            'rate': rate,
            'base': 'COP',
            'target': 'USD',
            'example': f'1000 COP = {cls.convert_cop_to_usd(1000)} USD',
            'cached': cache.get(cls.CACHE_KEY) is not None
        }


def convert_price_dict(price_dict, target_currency):
    """
    Convert all prices in a dictionary to target currency.
    
    Args:
        price_dict: Dictionary with price fields (price, regular_price, sale_price)
        target_currency: Target currency code ('COP' or 'USD')
        
    Returns:
        dict: Dictionary with converted prices
    """
    if not price_dict:
        return price_dict
    
    converted = price_dict.copy()
    
    # Convert each price field
    for field in ['price', 'regular_price', 'sale_price']:
        if field in converted and converted[field] is not None:
            converted[field] = CurrencyConverter.convert_price(
                converted[field], 
                target_currency
            )
    
    # Add currency indicator
    converted['currency'] = target_currency.upper()
    
    return converted
