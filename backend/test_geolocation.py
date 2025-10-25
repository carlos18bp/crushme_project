#!/usr/bin/env python3
"""
Quick test script to verify geolocation implementation
Run with: python test_geolocation.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crushme_project.settings')
django.setup()

from crushme_app.utils.geolocation import GeoLocationService

def test_geolocation():
    """Test the GeoLocation service with various IPs"""
    
    print("=" * 60)
    print("GEOLOCATION SERVICE TEST")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Colombian IP (Bogotá)',
            'ip': '181.49.176.10',
            'expected_country': 'CO',
            'expected_currency': 'COP'
        },
        {
            'name': 'US IP (Google DNS)',
            'ip': '8.8.8.8',
            'expected_country': 'US',
            'expected_currency': 'USD'
        },
        {
            'name': 'Mexican IP',
            'ip': '187.188.1.1',
            'expected_country': 'MX',
            'expected_currency': 'USD'
        },
        {
            'name': 'Spanish IP',
            'ip': '88.26.224.1',
            'expected_country': 'ES',
            'expected_currency': 'USD'
        },
        {
            'name': 'Brazilian IP',
            'ip': '200.204.0.10',
            'expected_country': 'BR',
            'expected_currency': 'USD'
        },
        {
            'name': 'Colombian IP (Medellín)',
            'ip': '190.85.0.1',
            'expected_country': 'CO',
            'expected_currency': 'COP'
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n{'─' * 60}")
        print(f"Testing: {test['name']}")
        print(f"IP: {test['ip']}")
        print(f"{'─' * 60}")
        
        try:
            # Get country code
            country_code = GeoLocationService.get_country_code(test['ip'])
            is_colombia = GeoLocationService.is_colombia(test['ip'])
            currency = GeoLocationService.get_currency_by_ip(test['ip'])
            
            # Display results
            print(f"✓ Country Code: {country_code}")
            print(f"✓ Is Colombia: {is_colombia}")
            print(f"✓ Recommended Currency: {currency}")
            
            # Verify expectations
            if country_code == test['expected_country']:
                print(f"✅ Country code matches expected: {test['expected_country']}")
            else:
                print(f"❌ Country code mismatch! Expected: {test['expected_country']}, Got: {country_code}")
                failed += 1
                continue
            
            if currency == test['expected_currency']:
                print(f"✅ Currency matches expected: {test['expected_currency']}")
            else:
                print(f"❌ Currency mismatch! Expected: {test['expected_currency']}, Got: {currency}")
                failed += 1
                continue
            
            # Verify is_colombia flag
            expected_is_colombia = (test['expected_country'] == 'CO')
            if is_colombia == expected_is_colombia:
                print(f"✅ is_colombia flag correct: {is_colombia}")
            else:
                print(f"❌ is_colombia flag incorrect! Expected: {expected_is_colombia}, Got: {is_colombia}")
                failed += 1
                continue
            
            passed += 1
            print(f"✅ TEST PASSED")
            
        except Exception as e:
            print(f"❌ TEST FAILED: {str(e)}")
            failed += 1
    
    # Summary
    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Tests: {len(test_cases)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
    print(f"{'=' * 60}")
    
    # Close the reader
    GeoLocationService.close()
    print("\n✓ GeoLocation service closed")
    
    return failed == 0

if __name__ == '__main__':
    success = test_geolocation()
    exit(0 if success else 1)
