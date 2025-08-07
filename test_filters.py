#!/usr/bin/env python
"""
Script để test datetime template filters
"""

import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, '/home/duong/project/python-naitei25_docwn')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docwn.settings')
django.setup()

from django.utils import timezone
from novels.templatetags.datetime_filters import localtime_format, to_localtime

def test_template_filters():
    """Test template filters"""
    print("=== Testing Template Filters ===")
    
    # Create a test datetime
    test_dt = timezone.make_aware(datetime(2025, 1, 1, 12, 0, 0))
    print(f"Test datetime (UTC): {test_dt}")
    
    # Test localtime_format filter
    formatted = localtime_format(test_dt, "d/m/Y H:i")
    print(f"Formatted with localtime_format: {formatted}")
    
    # Test to_localtime filter  
    local_dt = to_localtime(test_dt)
    print(f"Converted to local time: {local_dt}")
    
    # Test with None values
    print(f"localtime_format with None: '{localtime_format(None)}'")
    print(f"to_localtime with None: {to_localtime(None)}")
    
    print("=== Template filters test passed! ===")

if __name__ == "__main__":
    test_template_filters()
