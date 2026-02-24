/**
 * imagery.js — Gallery category filter and image size toggle.
 */
(function () {
    'use strict';

    var gallery    = document.getElementById('gallery');
    var filterBtns = document.querySelectorAll('.filter-btn');
    var sizeToggle = document.getElementById('size-toggle');
    var sizeLabel  = document.getElementById('size-label');
    var items      = document.querySelectorAll('.gallery-item');
    var currentSize = 'large';

    // ---- Category filter ----
    filterBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var filter = btn.getAttribute('data-filter');

            filterBtns.forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');

            items.forEach(function (item) {
                var match = filter === 'all' || item.getAttribute('data-category') === filter;
                item.classList.toggle('hidden', !match);
            });
        });
    });

    // ---- Size toggle ----
    sizeToggle.addEventListener('click', function () {
        if (currentSize === 'large') {
            currentSize = 'small';
            gallery.classList.replace('size-large', 'size-small');
            sizeLabel.textContent = 'SMALL';
        } else {
            currentSize = 'large';
            gallery.classList.replace('size-small', 'size-large');
            sizeLabel.textContent = 'LARGE';
        }
    });

})();
