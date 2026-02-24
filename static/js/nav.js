/**
 * nav.js — Active link detection for site-wide navbar.
 * Marks the .site-nav <a> whose href matches the current pathname.
 */
(function () {
    'use strict';

    function activateNav() {
        var path = window.location.pathname;
        var links = document.querySelectorAll('.site-nav a');

        links.forEach(function (link) {
            var href = link.getAttribute('href');
            if (!href) return;

            if (href === '/' && path === '/') {
                link.classList.add('active');
            } else if (href !== '/' && path.startsWith(href)) {
                link.classList.add('active');
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', activateNav);
    } else {
        activateNav();
    }
})();
