"""
GeoIP2 service for IP geolocation using MaxMind GeoLite2 Country database.
"""
import geoip2.database
import os
from django.conf import settings


class GeoLocationService:
    """Service to detect country from IP address using MaxMind GeoLite2 Country database."""
    
    _reader = None
    
    @classmethod
    def get_reader(cls):
        """Get or create GeoIP2 reader instance (singleton pattern)."""
        if cls._reader is None:
            # Path to GeoLite2 Country database
            db_path = os.path.join(
                settings.BASE_DIR,
                'geolocalization',
                'GeoLite2-Country_20251024',
                'GeoLite2-Country.mmdb'
            )
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"GeoLite2 database not found at {db_path}")
            
            cls._reader = geoip2.database.Reader(db_path)
        
        return cls._reader
    
    @classmethod
    def get_country_code(cls, ip_address):
        """
        Get country code from IP address.
        
        Args:
            ip_address (str): IP address to lookup
            
        Returns:
            str: Two-letter country code (e.g., 'CO', 'US') or None if not found
        """
        try:
            reader = cls.get_reader()
            response = reader.country(ip_address)
            return response.country.iso_code
        except geoip2.errors.AddressNotFoundError:
            # IP not found in database
            return None
        except Exception as e:
            print(f"Error getting country for IP {ip_address}: {e}")
            return None
    
    @classmethod
    def is_colombia(cls, ip_address):
        """
        Check if IP address is from Colombia.
        
        Args:
            ip_address (str): IP address to check
            
        Returns:
            bool: True if IP is from Colombia, False otherwise
        """
        country_code = cls.get_country_code(ip_address)
        return country_code == 'CO'
    
    @classmethod
    def get_currency_by_ip(cls, ip_address):
        """
        Get recommended currency based on IP address.
        
        Args:
            ip_address (str): IP address to check
            
        Returns:
            str: 'COP' for Colombia, 'USD' for all other countries
        """
        return 'COP' if cls.is_colombia(ip_address) else 'USD'
    
    @classmethod
    def close(cls):
        """Close the GeoIP2 reader."""
        if cls._reader is not None:
            cls._reader.close()
            cls._reader = None
