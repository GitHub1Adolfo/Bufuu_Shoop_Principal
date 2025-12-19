document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');

    if (!searchInput) return;

    // ================================
    // 1. SMOOTH SCROLL TO RESULTS
    // ================================
    const resultItems = document.querySelectorAll('.result-item');
    
    resultItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            if (targetId.startsWith('#producto-')) {
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    // Smooth scroll to product
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    
                    // Highlight effect
                    targetElement.style.animation = 'highlight 2s ease';
                    setTimeout(() => {
                        targetElement.style.animation = '';
                    }, 2000);
                }
            }
        });
    });

    // ================================
    // 2. SEARCH INPUT ENHANCEMENTS
    // ================================
    
    // Clear button
    if (searchInput.value) {
        addClearButton();
    }

    searchInput.addEventListener('input', function() {
        if (this.value) {
            addClearButton();
        } else {
            removeClearButton();
        }
    });

    function addClearButton() {
        if (document.querySelector('.search-clear-btn')) return;
        
        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.className = 'search-clear-btn';
        clearBtn.innerHTML = '✕';
        clearBtn.style.cssText = `
            position: absolute;
            right: 64px;
            top: 50%;
            transform: translateY(-50%);
            width: 32px;
            height: 32px;
            background: transparent;
            border: none;
            cursor: pointer;
            color: var(--text-light);
            font-size: 1.25rem;
            border-radius: 50%;
            transition: all 0.2s ease;
        `;
        
        clearBtn.addEventListener('mouseenter', function() {
            this.style.background = 'var(--bg-secondary)';
            this.style.color = 'var(--text-primary)';
        });
        
        clearBtn.addEventListener('mouseleave', function() {
            this.style.background = 'transparent';
            this.style.color = 'var(--text-light)';
        });
        
        clearBtn.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.focus();
            removeClearButton();
            
            // If on search results page, redirect to menu
            if (window.location.search.includes('q=')) {
                window.location.href = window.location.pathname;
            }
        });
        
        searchForm.style.position = 'relative';
        searchForm.appendChild(clearBtn);
    }

    function removeClearButton() {
        const clearBtn = document.querySelector('.search-clear-btn');
        if (clearBtn) {
            clearBtn.remove();
        }
    }

    // ================================
    // 3. KEYBOARD SHORTCUTS
    // ================================
    
    // Focus search with "/" key
    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
            e.preventDefault();
            searchInput.focus();
        }
        
        // Escape to clear search
        if (e.key === 'Escape' && document.activeElement === searchInput) {
            searchInput.value = '';
            searchInput.blur();
            removeClearButton();
        }
    });

    // ================================
    // 4. SEARCH LOADING STATE
    // ================================
    
    searchForm.addEventListener('submit', function() {
        if (searchInput.value.trim()) {
            searchBtn.innerHTML = '<div class="search-spinner" style="width: 20px; height: 20px; border: 2px solid white; border-top-color: transparent; border-radius: 50%; animation: spin 0.6s linear infinite;"></div>';
            searchBtn.disabled = true;
        }
    });

    // ================================
    // 5. HIGHLIGHT SEARCH TERMS
    // ================================
    
    const query = searchInput.value.trim();
    if (query) {
        highlightSearchTerms(query);
    }

    function highlightSearchTerms(term) {
        const resultNames = document.querySelectorAll('.result-name');
        
        resultNames.forEach(nameElement => {
            const text = nameElement.textContent;
            const regex = new RegExp(`(${escapeRegex(term)})`, 'gi');
            const highlightedText = text.replace(regex, '<span class="search-highlight">$1</span>');
            nameElement.innerHTML = highlightedText;
        });
    }

    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // ================================
    // 6. SEARCH HISTORY (LocalStorage)
    // ================================
    
    function saveSearchHistory(query) {
        if (!query) return;
        
        let history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        
        // Remove duplicates and add to beginning
        history = history.filter(item => item !== query);
        history.unshift(query);
        
        // Keep only last 10 searches
        history = history.slice(0, 10);
        
        localStorage.setItem('searchHistory', JSON.stringify(history));
    }

    function getSearchHistory() {
        return JSON.parse(localStorage.getItem('searchHistory') || '[]');
    }

    // Save on form submit
    searchForm.addEventListener('submit', function() {
        const query = searchInput.value.trim();
        if (query) {
            saveSearchHistory(query);
        }
    });

    // Show history on focus (optional)
    searchInput.addEventListener('focus', function() {
        const history = getSearchHistory();
        if (history.length > 0 && !this.value) {
            // You can implement a dropdown here if desired
            console.log('Search history:', history);
        }
    });

    // ================================
    // 7. SEARCH ANALYTICS (Optional)
    // ================================
    
    function trackSearch(query, resultsCount) {
        // Send to analytics
        console.log('Search tracked:', {
            query: query,
            results: resultsCount,
            timestamp: new Date().toISOString()
        });
        
        // You can send this to Google Analytics or your backend
        // gtag('event', 'search', { search_term: query });
    }

    // Track current search
    const resultsCount = document.querySelectorAll('.result-item').length;
    if (query && resultsCount >= 0) {
        trackSearch(query, resultsCount);
    }

    // ================================
    // 8. ANIMATION HELPERS
    // ================================
    
    // Add stagger animation to results
    const results = document.querySelectorAll('.result-item');
    results.forEach((result, index) => {
        result.style.animationDelay = `${index * 0.05}s`;
    });

    // ================================
    // 9. MOBILE OPTIMIZATIONS
    // ================================
    
    // Prevent zoom on input focus (iOS)
    if (/iPhone|iPad|iPod/i.test(navigator.userAgent)) {
        searchInput.style.fontSize = '16px';
    }

    // ================================
    // 10. ACCESSIBILITY
    // ================================
    
    // Announce results to screen readers
    if (resultsCount > 0) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.style.position = 'absolute';
        announcement.style.left = '-9999px';
        announcement.textContent = `Se encontraron ${resultsCount} resultados para "${query}"`;
        document.body.appendChild(announcement);
    }
});

// ================================
// UTILITY: Debounce function
// ================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ================================
// CSS ANIMATIONS (add to your CSS if needed)
// ================================

const style = document.createElement('style');
style.textContent = `
    @keyframes highlight {
        0%, 100% {
            background-color: transparent;
        }
        50% {
            background-color: rgba(16, 185, 129, 0.2);
            transform: scale(1.02);
        }
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .result-item {
        animation: slideInLeft 0.5s ease forwards;
        opacity: 0;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);