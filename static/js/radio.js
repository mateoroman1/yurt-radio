/**
 * Yurt Radio - JavaScript Controller
 *
 * This file handles:
 * - Fetching tracks from the API
 * - Controlling the audio player
 * - Updating the UI
 * - User interactions
 */

// ==================== CONFIGURATION ====================

// UPDATE FOR PROD const API_BASE_URL = '/api';
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// ==================== STATE ====================

let currentTrack = null;
let isPlaying = false;

// ==================== DOM ELEMENTS ====================

const audioPlayer = document.getElementById('audio-player');
const playBtn = document.getElementById('play-btn');
const nextBtn = document.getElementById('next-btn');
const playIcon = document.getElementById('play-icon');
const playText = document.getElementById('play-text');
const volumeSlider = document.getElementById('volume');
const volumeValue = document.getElementById('volume-value');
const progressBar = document.getElementById('progress-bar');
const progressContainer = document.querySelector('.progress-container');

const trackTitle = document.getElementById('track-title');
const trackArtist = document.getElementById('track-artist');
const trackDuration = document.getElementById('track-duration');
const statusMessage = document.getElementById('status-message');
const statsText = document.getElementById('stats-text');

// ==================== API FUNCTIONS ====================

/**
 * Fetch a random track from the API
 */
async function fetchRandomTrack() {
    try {
        const url = `${API_BASE_URL}/track/random`;
        const response = await fetch(url);

        if (!response.ok){
            throw new Error('Failed to fetch track');
        }
        // Parse JSON
        const track = await response.json();

        console.log('Fetched Track: ', track);

        // Return track data
        return track;
    } catch (error) {
        console.error('Error fetching track:', error);
        showStatus('Error loading track', 'error');
        return null;
    }
}

/**
 * Fetch collection stats from the API
 */
async function fetchStats() {
    try {
        const url = `${API_BASE_URL}/stats`;
        const response = await fetch(url);

        if (!response.ok){
            throw new Error('Failed to fetch track');
        }

        const stats = await response.json();
        console.log('Stats: ', stats);

        const total_tracks = stats.total_tracks;
        const total_duration = formatTime(stats.total_duration);
        const most_played = stats.most_played.title;

        // Update statsText element
        statsText.textContent = `${total_tracks} songs | total runtime - ${total_duration} | most played - ${most_played}`;  

    } catch (error) {
        console.error('Error fetching stats:', error);
        statsText.textContent = 'Stats unavailable';
    }
}

// ==================== PLAYER FUNCTIONS ====================

/**
 * Load and play a track
 */
async function loadTrack(track, autoplay = false) {
    if (!track) {
        showStatus('No track available', 'error');
        return;
    }

    // Set current track
    currentTrack = track;
    // Set audio source
    audioPlayer.src = `${API_BASE_URL}/stream/${track.id}`;
    // Update UI
    updateUI(currentTrack);
    // Optionally play
    if (autoplay) {
        audioPlayer.play();
        isPlaying = true;
    }
}

/**
 * Toggle play/pause
 */
async function togglePlay() {
    // If no track loaded yet, load one first
    if (!currentTrack) {
        const track = await fetchRandomTrack();

        if (track){
            await loadTrack(track);
        }
    }

    // Toggle play/pause
    if (isPlaying) {
        audioPlayer.pause();
    } else {
        audioPlayer.play();
    }

}

/**
 * Load and play the next random track
 */
async function playNext() {
    // YOUR CODE HERE
    showStatus('Loading next track...', 'loading');

    // Fetch random track
    const track = await fetchRandomTrack();

    if (track){
        await loadTrack(track, true);

    }
}

/**
 * Update the UI with current track information
 */
function updateUI(track) {

    if (!track) return;

    const titleElement = document.getElementById('track-title');
    const artistElement = document.getElementById('track-artist');
    const durationElement = document.getElementById('track-duration');

    // Update title
    titleElement.textContent = track.file_path;
    // Update artist
    artistElement.textContent = track.author;
    // Update duration display (use formatTime)
    const durationText = formatTime(track.duration);
    durationElement.textContent = `0:00 / ${durationText}`;

    // Clear status
    showStatus('', '');
}

/**
 * Update play/pause button appearance
 */
function updatePlayButton() {

    if (isPlaying) {
        const playTxtElement = document.getElementById('play-text');
        playTxtElement.textContent = 'PAUSE';

        const playIconElement = document.getElementById('play-icon');
        playIconElement.textContent = '⏸';
    } else {
        const playTxtElement = document.getElementById('play-text');
        playTxtElement.textContent = 'PLAY';

        const playIconElement = document.getElementById('play-icon');
        playIconElement.textContent = '▶';
    }
}

/**
 * Update progress bar as track plays
 */
function updateProgress() {

    if (!audioPlayer.duration) return;

    const currentTime = audioPlayer.currentTime;
    const duration = audioPlayer.duration;

    // Calculate progress percentage
    const percentage = (currentTime / duration) * 100;
    // Update progress bar width
    progressBar.style.width = `${percentage}%`;
    // Update time display (current / total)
    trackDuration.textContent = `${formatTime(currentTime)} / ${formatTime(duration)}`;
}

/**
 * Show a status message to the user
 */
function showStatus(message, type = '') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;

    // Auto-clear after 3 seconds unless it's an error
    if (type !== 'error') {
        setTimeout(() => {
            statusMessage.textContent = '';
            statusMessage.className = 'status-message';
        }, 3000);
    }
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Format seconds to MM:SS
 */
function formatTime(seconds) {

    if (Number.isNaN(seconds)) return '0:00';

    // Calculate minutes and seconds
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    // Format as MM:SS
    const secsFormatted = secs.toString().padStart(2, '0');
    if (hours > 0){
        return `${hours}:${mins}:${secsFormatted}`;
    }
    return `${mins}:${secsFormatted}`;
}

// ==================== EVENT LISTENERS ====================

/**
 * Set up all event listeners
 * Most of these are already implemented for you!
 */
function setupEventListeners() {
    // Play/Pause button
    playBtn.addEventListener('click', togglePlay);

    // Next button
    nextBtn.addEventListener('click', playNext);

    // Volume control
    volumeSlider.addEventListener('input', (e) => {
        const volume = e.target.value / 100;
        audioPlayer.volume = volume;
        volumeValue.textContent = e.target.value;
    });

    // Audio player events
    audioPlayer.addEventListener('play', () => {
        isPlaying = true;
        updatePlayButton();
    });

    audioPlayer.addEventListener('pause', () => {
        isPlaying = false;
        updatePlayButton();
    });

    audioPlayer.addEventListener('ended', () => {
        // Auto-play next track when current one ends
        playNext();
    });

    audioPlayer.addEventListener('timeupdate', updateProgress);

    audioPlayer.addEventListener('error', (e) => {
        console.error('Audio error:', e);
        showStatus('Error playing track', 'error');
    });

    // Progress bar click to seek
    progressContainer.addEventListener('click', (e) => {
        if (!audioPlayer.duration) return;

        const rect = progressContainer.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const percentage = clickX / rect.width;
        audioPlayer.currentTime = percentage * audioPlayer.duration;
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Spacebar = play/pause
        if (e.code === 'Space') {
            e.preventDefault();
            togglePlay();
        }
        // N key = next track
        if (e.code === 'KeyN') {
            e.preventDefault();
            playNext();
        }
    });
}

// ==================== INITIALIZATION ====================

/**
 * Initialize the application
 */
function init() {
    console.log('Yurt Radio initializing...');

    // Set initial volume
    audioPlayer.volume = volumeSlider.value / 100;
    volumeValue.textContent = volumeSlider.value;

    // Fetch stats
    fetchStats();

    // Set up event listeners
    setupEventListeners();

    console.log('Yurt Radio ready!');
}

// Run init when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
