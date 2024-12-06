// Performance optimizations
document.addEventListener('DOMContentLoaded', function() {
    // Defer non-critical CSS
    function loadDeferredStyles() {
        const addStylesNode = document.getElementById('deferred-styles');
        const replacement = document.createElement('div');
        replacement.innerHTML = addStylesNode.textContent;
        document.body.appendChild(replacement);
        addStylesNode.parentElement.removeChild(addStylesNode);
    }

    // Handle fonts loading
    if ('fonts' in document) {
        Promise.all([
            document.fonts.load('1em Roboto'),
            document.fonts.load('1em Open Sans'),
            document.fonts.load('1em Poppins')
        ]).then(function () {
            document.documentElement.classList.add('fonts-loaded');
        });
    }

    // Prefetch links on hover
    const prefetcher = {
        init() {
            this.linksToPrefetch = new Set();
            this.observer = new IntersectionObserver(this.handleIntersection.bind(this));
            this.observeLinks();
        },
        
        observeLinks() {
            document.querySelectorAll('a').forEach(link => {
                this.observer.observe(link);
            });
        },

        handleIntersection(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const link = entry.target;
                    if (!this.linksToPrefetch.has(link.href)) {
                        this.linksToPrefetch.add(link.href);
                        const prefetchLink = document.createElement('link');
                        prefetchLink.rel = 'prefetch';
                        prefetchLink.href = link.href;
                        document.head.appendChild(prefetchLink);
                    }
                }
            });
        }
    };

    prefetcher.init();
});
