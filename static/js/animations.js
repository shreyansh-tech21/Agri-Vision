/**
 * Agri-Vision - Scroll Reveal Animation System
 * A production-grade intersection observer animation system.
 * Handles performance, accessibility (reduced motion), and dynamic stagger.
 */

const AnimationsEngine = (function() {
    let revealObserver = null;

    function init() {
        // 1. Accessibility Check: Do not initialize if user prefers reduced motion
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) {
            // Immediately show all elements if animations are disabled
            document.querySelectorAll('.reveal').forEach(el => {
                el.classList.add('active');
                el.style.transition = 'none';
            });
            return;
        }

        // 2. Observer Configuration
        const observerOptions = {
            root: null, // Viewport
            rootMargin: '0px 0px -50px 0px', // Trigger slightly before element enters the bottom
            threshold: 0.15 // Trigger when 15% of element is visible
        };

        // 3. Stagger State Tracking
        let staggerNodes = new Map();
        let staggerTimeout = null;

        // 4. Observer Callback
        const observerCallback = (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    
                    // Check if element belongs to a stagger container
                    const staggerContainer = el.closest('.reveal-stagger');
                    
                    if (staggerContainer) {
                        // Group elements by their container for staggered delays
                        if (!staggerNodes.has(staggerContainer)) {
                            staggerNodes.set(staggerContainer, []);
                        }
                        staggerNodes.get(staggerContainer).push(el);
                    } else {
                        // Activate immediately if no stagger
                        el.classList.add('active');
                    }

                    // Unobserve for performance if we only want to animate once
                    const animateOnce = el.getAttribute('data-reveal-once') !== 'false';
                    if (animateOnce) {
                        observer.unobserve(el);
                    }
                } else {
                    // If data-reveal-once is false, we remove active class on exit
                    const animateOnce = entry.target.getAttribute('data-reveal-once') !== 'false';
                    if (!animateOnce) {
                        entry.target.classList.remove('active');
                    }
                }
            });

            // 5. Process Staggered Elements
            if (staggerNodes.size > 0) {
                clearTimeout(staggerTimeout);
                staggerTimeout = setTimeout(() => {
                    staggerNodes.forEach((elements, container) => {
                        // Sort elements vertically to ensure natural reading order stagger
                        elements.sort((a, b) => {
                            return a.getBoundingClientRect().top - b.getBoundingClientRect().top || 
                                   a.getBoundingClientRect().left - b.getBoundingClientRect().left;
                        });

                        elements.forEach((el, index) => {
                            // Apply dynamic delay variable
                            el.style.setProperty('--reveal-delay', `${index * 0.1}s`);
                            // Force reflow
                            void el.offsetWidth;
                            el.classList.add('active');
                        });
                    });
                    // Clear map after processing
                    staggerNodes.clear();
                }, 50);
            }
        };

        // Disconnect previous observer if re-initializing
        if (revealObserver) {
            revealObserver.disconnect();
        }

        // 6. Initialize Observer
        revealObserver = new IntersectionObserver(observerCallback, observerOptions);

        // 7. Observe Elements
        const revealElements = document.querySelectorAll('.reveal');
        revealElements.forEach(el => revealObserver.observe(el));
    }

    return {
        init
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    AnimationsEngine.init();
});
