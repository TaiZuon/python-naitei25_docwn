#!/usr/bin/env python
"""
Script để test timezone configuration
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
from django.conf import settings

def test_timezone():
    """Test timezone configuration"""
    print("=== Django Timezone Configuration Test ===")
    print(f"TIME_ZONE setting: {settings.TIME_ZONE}")
    print(f"USE_TZ setting: {settings.USE_TZ}")
    
    # Current time in different formats
    now_utc = timezone.now()
    print(f"Current UTC time: {now_utc}")
    
    # Convert to local timezone
    now_local = timezone.localtime(now_utc)
    print(f"Current local time: {now_local}")
    
    # Test with specific datetime
    test_dt = timezone.make_aware(datetime(2025, 1, 1, 12, 0, 0))
    test_local = timezone.localtime(test_dt)
    print(f"Test datetime UTC: {test_dt}")
    print(f"Test datetime local: {test_local}")
    
    print("=== Test passed! ===")

if __name__ == "__main__":
    test_timezone()
