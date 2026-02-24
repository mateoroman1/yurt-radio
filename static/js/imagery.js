/**
 * imagery.js — Gallery build, category filter, size toggle, and lightbox.
 *
 * Images are fetched from /api/imagery and built into the DOM dynamically.
 * Clicking any image opens a full-size lightbox with prev/next navigation.
 */
(function () {
    'use strict';

    var gallery    = document.getElementById('gallery');
    var filterBtns = document.querySelectorAll('.filter-btn');
    var sizeToggle = document.getElementById('size-toggle');
    var sizeLabel  = document.getElementById('size-label');
    var currentSize = 'large';
    var activeFilter = 'all';

    // ---- Lightbox elements ----
    var lightbox = document.getElementById('lightbox');
    var lbImg    = document.getElementById('lb-img');
    var lbTitle  = document.getElementById('lb-title');
    var lbSub    = document.getElementById('lb-sub');
    var lbClose  = document.getElementById('lb-close');
    var lbPrev   = document.getElementById('lb-prev');
    var lbNext   = document.getElementById('lb-next');

    var currentIndex  = 0;
    var visibleItems  = []; // gallery-item elements currently visible

    // ---- Build a single gallery item ----
    function buildItem(img) {
        var fig = document.createElement('figure');
        fig.className = 'gallery-item';
        fig.setAttribute('data-category', img.category);
        fig.setAttribute('data-src',      img.src);
        fig.setAttribute('data-title',    img.title);
        fig.setAttribute('data-label',    img.label);

        var imgEl = document.createElement('img');
        imgEl.src     = img.src;
        imgEl.alt     = img.title;
        imgEl.loading = 'lazy';

        var caption = document.createElement('figcaption');
        caption.className = 'gallery-caption';
        caption.innerHTML =
            '<span class="caption-title">' + escapeHtml(img.title) + '</span>' +
            '<span class="caption-sub">'   + escapeHtml(img.label) + '</span>';

        fig.appendChild(imgEl);
        fig.appendChild(caption);

        fig.addEventListener('click', function () { openLightbox(fig); });

        return fig;
    }

    function escapeHtml(str) {
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // ---- Lightbox ----
    function getVisibleItems() {
        return Array.from(gallery.querySelectorAll('.gallery-item:not(.hidden)'));
    }

    function openLightbox(figEl) {
        visibleItems = getVisibleItems();
        currentIndex = visibleItems.indexOf(figEl);
        showAt(currentIndex);
        lightbox.classList.add('open');
        lightbox.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('open');
        lightbox.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    function showAt(idx) {
        var fig = visibleItems[idx];
        lbImg.src         = fig.getAttribute('data-src');
        lbImg.alt         = fig.getAttribute('data-title');
        lbTitle.textContent = fig.getAttribute('data-title');
        lbSub.textContent   = fig.getAttribute('data-label');
        lbPrev.style.visibility = idx > 0                        ? 'visible' : 'hidden';
        lbNext.style.visibility = idx < visibleItems.length - 1 ? 'visible' : 'hidden';
    }

    lbClose.addEventListener('click', closeLightbox);

    lightbox.addEventListener('click', function (e) {
        if (e.target === lightbox) closeLightbox();
    });

    lbPrev.addEventListener('click', function (e) {
        e.stopPropagation();
        if (currentIndex > 0) { currentIndex--; showAt(currentIndex); }
    });

    lbNext.addEventListener('click', function (e) {
        e.stopPropagation();
        if (currentIndex < visibleItems.length - 1) { currentIndex++; showAt(currentIndex); }
    });

    document.addEventListener('keydown', function (e) {
        if (!lightbox.classList.contains('open')) return;
        if (e.key === 'Escape')      { closeLightbox(); }
        if (e.key === 'ArrowLeft'  && currentIndex > 0)                        { currentIndex--; showAt(currentIndex); }
        if (e.key === 'ArrowRight' && currentIndex < visibleItems.length - 1)  { currentIndex++; showAt(currentIndex); }
    });

    // ---- Category filter ----
    function applyFilter(filter) {
        activeFilter = filter;
        gallery.querySelectorAll('.gallery-item').forEach(function (item) {
            var match = filter === 'all' || item.getAttribute('data-category') === filter;
            item.classList.toggle('hidden', !match);
        });
    }

    filterBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            filterBtns.forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            applyFilter(btn.getAttribute('data-filter'));
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

    // ---- Fetch images and populate gallery ----
    fetch('/api/imagery')
        .then(function (r) { return r.json(); })
        .then(function (images) {
            gallery.innerHTML = '';
            images.forEach(function (img) {
                gallery.appendChild(buildItem(img));
            });
            // Re-apply active filter if one was selected before load finished
            applyFilter(activeFilter);
        })
        .catch(function () {
            gallery.innerHTML = '<p style="color:var(--fg-dim);font-size:0.8rem;padding:1rem 0;">Failed to load imagery.</p>';
        });

})();
