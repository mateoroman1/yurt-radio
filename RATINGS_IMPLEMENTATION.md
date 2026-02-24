# Track Ratings Implementation Guide

## Overview
Add a simple 5-star rating system to Yurt Radio.

## Database Schema

### New Table: ratings
```sql
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
);

CREATE INDEX idx_track_ratings ON ratings(track_id);
```

### Update tracks table (optional)
Add cached rating data for performance:
```sql
ALTER TABLE tracks ADD COLUMN average_rating REAL DEFAULT 0;
ALTER TABLE tracks ADD COLUMN rating_count INTEGER DEFAULT 0;
```

## Backend Implementation

### Step 1: Update models.py

Add these functions:

**submit_rating(track_id, rating)**
- Validates rating (1-5)
- Inserts into ratings table
- Updates track's average_rating and rating_count
- Returns success/failure

**get_track_rating(track_id)**
- Returns average rating and count for a track
- Example: `{"average": 4.2, "count": 15}`

**get_top_rated_tracks(limit=10)**
- Returns tracks sorted by average_rating
- Good for a "Top Rated" feature later

### Step 2: Update routes.py

Add these endpoints:

**POST /api/track/<track_id>/rate**
```json
Request: { "rating": 4 }
Response: { "success": true, "new_average": 4.2, "total_ratings": 16 }
```

**GET /api/track/<track_id>/rating**
```json
Response: { "average": 4.2, "count": 15 }
```

Update existing endpoints:
- `/api/track/random` - Include rating info in response
- `/api/track/<id>` - Include rating info

### Step 3: Migration Script

Create `scripts/add_ratings.py`:
```python
# Creates the ratings table
# Updates existing tracks with default rating values
# Safe to run multiple times
```

## Frontend Implementation

### Step 1: Add Star Display Component

**In radio.js**, add:

```javascript
/**
 * Render star rating display (read-only)
 * @param {number} rating - Average rating (0-5)
 * @param {number} count - Number of ratings
 */
function renderStars(rating, count) {
    // Returns HTML string with stars
    // ★★★★☆ (15 ratings)
}

/**
 * Render interactive star rating
 * @param {number} trackId - Track to rate
 * @param {number} currentRating - User's current rating if any
 */
function renderRatingInput(trackId, currentRating) {
    // Returns clickable stars
    // Calls submitRating() on click
}

/**
 * Submit a rating to the API
 */
async function submitRating(trackId, rating) {
    // POST to /api/track/<id>/rate
    // Update UI with new average
}
```

### Step 2: Update UI

**In index.html**, add rating display:

```html
<!-- After track duration -->
<div id="track-rating" style="font-family: monospace; margin-top: 0.5rem;">
    <!-- Stars will be inserted here by JavaScript -->
</div>
```

**In updateUI()**, add:
```javascript
// Fetch and display rating
const ratingHTML = renderStars(track.average_rating, track.rating_count);
document.getElementById('track-rating').innerHTML = ratingHTML;
```

### Step 3: Add Rating Interface

Options:
- **Simple**: Show stars, click to rate
- **Modal**: "Rate this track" button opens rating dialog
- **Inline**: Always show clickable stars below track info

Recommended: Inline clickable stars

## CSS Styling

Add to `style.css`:

```css
/* Star ratings */
.star-rating {
    font-size: 1.5rem;
    color: #ffff00;  /* TUI yellow */
    cursor: pointer;
}

.star-rating .star {
    display: inline-block;
    margin: 0 2px;
}

.star-rating .star.filled {
    color: #ffff00;
}

.star-rating .star.empty {
    color: #666;
}

.star-rating .star:hover {
    color: #fff;
}

.rating-count {
    font-size: 0.8rem;
    color: #888;
    margin-left: 0.5rem;
}
```

## Implementation Order

### Phase 1: Backend (30 min)
1. ✅ Create migration script for ratings table
2. ✅ Add submit_rating() to models.py
3. ✅ Add get_track_rating() to models.py
4. ✅ Add POST /api/track/<id>/rate endpoint
5. ✅ Update /api/track/random to include ratings

### Phase 2: Frontend Display (20 min)
1. ✅ Add renderStars() function
2. ✅ Update updateUI() to show rating
3. ✅ Add CSS for stars
4. ✅ Test display with dummy data

### Phase 3: Frontend Interaction (20 min)
1. ✅ Add renderRatingInput() function
2. ✅ Add submitRating() API call
3. ✅ Wire up click handlers
4. ✅ Update UI after rating

### Phase 4: Testing & Polish (15 min)
1. ✅ Test rating submission
2. ✅ Test on mobile
3. ✅ Add loading states
4. ✅ Add error handling

Total time: ~1.5 hours

## Future Enhancements

Once basic ratings work:
- **Top Rated page** - Show highest rated tracks
- **Rating distribution** - Show 5-star/4-star/etc breakdown
- **User rating memory** - Store ratings in localStorage
- **Prevent spam** - Rate limit per IP
- **Rating trends** - Track how ratings change over time
- **Comments** - Add text reviews alongside ratings

## Testing Checklist

- [ ] Can rate a track 1-5 stars
- [ ] Rating shows immediately after submission
- [ ] Average rating updates correctly
- [ ] Can't submit invalid ratings (0, 6, etc)
- [ ] Rating displays correctly on mobile
- [ ] Multiple ratings on same track work
- [ ] Rating persists after page refresh
- [ ] Rating shows on random track load

## Notes

**Why separate ratings table?**
- Allows tracking individual ratings
- Easy to add user attribution later
- Can analyze rating patterns
- Can add features like "Recent Ratings"

**Why cache average in tracks table?**
- Faster queries (don't calculate average every time)
- Can sort tracks by rating efficiently
- Reduces database load

**Anonymous ratings concerns:**
- No spam prevention initially (fine for small community)
- Can add IP-based rate limiting later
- Can add localStorage to prevent double-rating
