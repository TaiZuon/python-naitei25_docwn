#!/usr/bin/env python3
"""
Test script to verify admin pagination functionality
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/home/duong/project/python-naitei25_docwn')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docwn.settings')
django.setup()

from django.core.paginator import Paginator
from novels.models import Novel, Chapter, Tag
from constants import PAGINATOR_COMMON_LIST, PAGINATION_PAGE_RANGE, DEFAULT_PAGE_NUMBER

def test_pagination():
    print("🔍 Testing Admin Pagination Settings")
    print(f"   📄 Page Size: {PAGINATOR_COMMON_LIST}")
    print(f"   📐 Page Range: {PAGINATION_PAGE_RANGE}")
    print(f"   🏁 Default Page: {DEFAULT_PAGE_NUMBER}")
    print()
    
    # Test novels pagination
    novels = Novel.objects.all()[:50]  # Limit for testing
    paginator = Paginator(novels, PAGINATOR_COMMON_LIST)
    
    print(f"📚 Novel Pagination Test:")
    print(f"   Total novels (test sample): {len(novels)}")
    print(f"   Total pages: {paginator.num_pages}")
    print(f"   Items per page: {paginator.per_page}")
    
    # Test first page
    first_page = paginator.get_page(1)
    print(f"   Page 1: {first_page.start_index()} - {first_page.end_index()}")
    print(f"   Has previous: {first_page.has_previous()}")
    print(f"   Has next: {first_page.has_next()}")
    
    # Test page range for different current pages
    for current_page in [1, 5, 10]:
        if current_page <= paginator.num_pages:
            page = paginator.get_page(current_page)
            print(f"   Page {current_page} range: {list(paginator.page_range)}")
    
    print("\n✅ Pagination test completed!")

if __name__ == "__main__":
    test_pagination()
