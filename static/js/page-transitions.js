/**
 * Agri-Vision - Page Transitions Engine
 * Utilizes Swup for SPA-like transitions in a server-rendered application.
 * Ensures accessibility and performance optimization.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Accessibility: Respect user's motion preferences
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Only initialize Swup if the user does NOT prefer reduced motion
    // Otherwise, standard browser navigation takes over automatically
    if (prefersReducedMotion) {
        console.log("Reduced motion requested. Page transitions disabled.");
        return;
    }

    // Initialize Swup
    const swup = new Swup({
        containers: ['#swup'],
        animationSelector: '[class*="transition-"]',
        plugins: [
            new SwupProgressPlugin({
                className: 'swup-progress-bar',
                transition: 300,
                delay: 300, // Only show progress bar if request takes longer than 300ms
                initialValue: 0.1,
                hideImmediately: true
            })
        ]
    });

    // Re-initialize custom scripts after Swup replaces the content
    swup.hooks.on('page:view', () => {
        // Re-initialize i18n
        if (typeof I18nEngine !== 'undefined' && I18nEngine.init) {
            I18nEngine.init();
        }

        // Re-initialize Intersection Observers for reveal animations
        if (typeof AnimationsEngine !== 'undefined' && AnimationsEngine.init) {
            AnimationsEngine.init();
        }

        // Scroll to top on page transition to simulate standard navigation
        window.scrollTo(0, 0);
    });
});
