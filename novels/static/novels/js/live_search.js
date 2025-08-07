// Live Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="q"]');
    const searchForm = searchInput?.closest('form');
    let searchTimeout;
    let searchResults = null;

    // Create search results dropdown
    function createSearchDropdown() {
        if (searchResults) return searchResults;
        
        searchResults = document.createElement('div');
        searchResults.className = 'search-dropdown';
        searchResults.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 8px 8px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        // Make parent position relative
        const parent = searchInput.parentElement;
        parent.style.position = 'relative';
        parent.appendChild(searchResults);
        
        return searchResults;
    }

    // Show search results
    function showSearchResults(results) {
        const dropdown = createSearchDropdown();
        dropdown.innerHTML = '';
        
        if (results.length === 0) {
            dropdown.innerHTML = `
                <div style="padding: 15px; text-align: center; color: #666;">
                    Không tìm thấy kết quả
                </div>
            `;
        } else {
            results.forEach(result => {
                const item = document.createElement('div');
                item.className = 'search-result-item';
                item.style.cssText = `
                    padding: 12px 15px;
                    border-bottom: 1px solid #f0f0f0;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    transition: background 0.2s;
                `;
                
                item.innerHTML = `
                    <div style="width: 40px; height: 40px; margin-right: 12px; border-radius: 4px; overflow: hidden; background: #f8f9fa; display: flex; align-items: center; justify-content: center;">
                        ${result.image_url ? 
                            `<img src="${result.image_url}" style="width: 100%; height: 100%; object-fit: cover;" alt="${result.name}">` :
                            `<i class="bx bx-book" style="font-size: 20px; color: #666;"></i>`
                        }
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 500; color: #333; margin-bottom: 2px;">${result.name}</div>
                        <div style="font-size: 0.9em; color: #666;">Tác giả: ${result.author}</div>
                    </div>
                `;
                
                item.addEventListener('mouseenter', function() {
                    this.style.background = '#f8f9fa';
                });
                
                item.addEventListener('mouseleave', function() {
                    this.style.background = 'white';
                });
                
                item.addEventListener('click', function() {
                    window.location.href = result.url;
                });
                
                dropdown.appendChild(item);
            });
        }
        
        dropdown.style.display = 'block';
    }

    // Hide search results
    function hideSearchResults() {
        if (searchResults) {
            searchResults.style.display = 'none';
        }
    }

    // Perform search
    function performSearch(query) {
        if (query.length < 2) {
            hideSearchResults();
            return;
        }
        
        fetch(`/novels/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                showSearchResults(data.results);
            })
            .catch(error => {
                console.error('Search error:', error);
                hideSearchResults();
            });
    }

    // Set up event listeners
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300); // Debounce search by 300ms
        });

        searchInput.addEventListener('focus', function() {
            const query = this.value.trim();
            if (query.length >= 2) {
                performSearch(query);
            }
        });

        // Hide dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchForm?.contains(e.target)) {
                hideSearchResults();
            }
        });

        // Handle keyboard navigation
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                hideSearchResults();
            }
        });
    }
});
