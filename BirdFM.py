### BirdFM - Enhanced version with API key support, caching, and rate limiting

import json
import time
import os
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('birdfm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CACHE_DIR = Path('cache')
AUDIO_CACHE_DIR = Path('audio_cache')  # Directory for downloaded audio files
CACHE_EXPIRY_HOURS = 24  # Cache data for 24 hours
API_DELAY_SECONDS = 2  # Delay between API calls to avoid spamming
MAX_RECORDINGS_PER_COUNTRY = 50  # Limit recordings to reduce API load
API_BASE_URL = 'https://xeno-canto.org/api/3/recordings'  # Updated to API v3

# Create cache directories if they don't exist
CACHE_DIR.mkdir(exist_ok=True)
AUDIO_CACHE_DIR.mkdir(exist_ok=True)

def get_api_key():
    """Get API key from environment variable or config file"""
    # Try environment variable first
    api_key = os.environ.get('XENO_CANTO_API_KEY')
    
    if not api_key:
        # Try reading from config file
        config_file = Path('config.json')
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    api_key = config.get('api_key')
            except Exception as e:
                logger.error(f"Error reading config file: {e}")
    
    if not api_key:
        logger.warning("No API key found. Set XENO_CANTO_API_KEY environment variable or create config.json with 'api_key' field")
    
    return api_key

def get_cache_filename(country, since):
    """Generate a cache filename based on query parameters"""
    cache_key = f"{country}_{since}"
    hash_key = hashlib.md5(cache_key.encode()).hexdigest()
    return CACHE_DIR / f"{hash_key}.json"

def is_cache_valid(cache_file):
    """Check if cache file exists and is not expired"""
    if not cache_file.exists():
        return False
    
    file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
    expiry_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
    
    return file_time > expiry_time

def download_audio_file(url, recording_id):
    """Download audio file and cache it locally"""
    # Create filename from recording ID
    file_extension = url.split('.')[-1].split('?')[0]  # Get extension from URL
    if file_extension not in ['mp3', 'wav', 'ogg']:
        file_extension = 'mp3'  # Default to mp3
    
    local_file = AUDIO_CACHE_DIR / f"{recording_id}.{file_extension}"
    
    # Check if file already exists and is recent
    if local_file.exists() and is_cache_valid(local_file):
        logger.debug(f"Using cached audio file: {local_file.name}")
        return str(local_file)
    
    # Download the file
    try:
        logger.info(f"Downloading audio file: {recording_id}")
        session = create_session_with_retry()
        response = session.get(url, timeout=60, stream=True)
        response.raise_for_status()
        
        # Save to file
        with open(local_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded: {local_file.name} ({local_file.stat().st_size / 1024:.1f} KB)")
        return str(local_file)
        
    except Exception as e:
        logger.error(f"Failed to download audio file: {e}")
        # Clean up partial download
        if local_file.exists():
            local_file.unlink()
        return None

def cleanup_old_audio_cache():
    """Remove audio files older than CACHE_EXPIRY_HOURS"""
    try:
        expiry_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
        removed_count = 0
        total_size = 0
        
        for audio_file in AUDIO_CACHE_DIR.glob('*'):
            if audio_file.is_file():
                file_time = datetime.fromtimestamp(audio_file.stat().st_mtime)
                if file_time < expiry_time:
                    size = audio_file.stat().st_size
                    audio_file.unlink()
                    removed_count += 1
                    total_size += size
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old audio files ({total_size / 1024 / 1024:.1f} MB)")
    except Exception as e:
        logger.error(f"Error cleaning up audio cache: {e}")

def load_from_cache(cache_file):
    """Load data from cache file"""
    try:
        with open(cache_file, 'r') as f:
            logger.info(f"Loading data from cache: {cache_file.name}")
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading cache: {e}")
        return None

def save_to_cache(cache_file, data):
    """Save data to cache file"""
    try:
        with open(cache_file, 'w') as f:
            json.dump(data, f)
            logger.info(f"Saved data to cache: {cache_file.name}")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")

def create_session_with_retry():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def make_api_call(country, since, api_key=None):
    """Make API call to Xeno-Canto with caching and rate limiting"""
    # Check cache first
    cache_file = get_cache_filename(country, since)
    if is_cache_valid(cache_file):
        cached_data = load_from_cache(cache_file)
        if cached_data:
            return cached_data
    
    # Make API call - Simple query format
    # Note: Xeno-Canto API doesn't use 'since' parameter in v2, just country
    query = f'cnt:"{country}"'
    url = f'{API_BASE_URL}?query={quote(query)}'
    
    logger.info(f"Making API call: {url}")
    
    try:
        session = create_session_with_retry()
        headers = {
            'User-Agent': 'BirdFM/1.0 (Raspberry Pi)'
        }
        
        # Note: Xeno-Canto API key may not be required for basic queries
        # or may be passed differently - check their documentation
        if api_key:
            # Try passing as query parameter instead of header
            url = f'{url}&key={api_key}'
        
        # Set a reasonable timeout for Pi Zero W
        response = session.get(url, headers=headers, timeout=30)
        
        # Log response details for debugging
        logger.info(f"Response status: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        
        # Limit recordings to reduce memory usage
        if 'recordings' in data and len(data['recordings']) > MAX_RECORDINGS_PER_COUNTRY:
            data['recordings'] = data['recordings'][:MAX_RECORDINGS_PER_COUNTRY]
            data['numRecordings'] = str(MAX_RECORDINGS_PER_COUNTRY)
            logger.info(f"Limited recordings to {MAX_RECORDINGS_PER_COUNTRY} for efficiency")
        
        # Save to cache
        save_to_cache(cache_file, data)
        
        # Rate limiting - be respectful to the API
        time.sleep(API_DELAY_SECONDS)
        
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None

def play_birdsong(recordings, index, location=None):
    """Play a birdsong with improved error handling"""
    try:
        recording = recordings['recordings'][index]
        
        # Check location filter if specified
        if location is not None:
            if location not in recording.get('loc', ''):
                return False
        
        # Get recording ID
        recording_id = recording.get('id', '')
        if not recording_id:
            logger.warning(f"No recording ID for index {index}")
            return False
        
        # Construct audio file URL
        # Xeno-Canto API v3 provides 'file' field with download URL (WAV format)
        # We need to construct the streaming MP3 URL from the sono path and filename
        sound_file_url = None
        
        if 'sono' in recording and 'file-name' in recording:
            # Extract the path from sonogram URL
            sono_small = recording.get('sono', {}).get('small', '')
            file_name = recording.get('file-name', '')
            
            if sono_small and file_name:
                # sono_small format: //xeno-canto.org/sounds/uploaded/XXXXX/ffts/filename-small.png
                # We need: https://xeno-canto.org/sounds/uploaded/XXXXX/filename.mp3
                if '/sounds/uploaded/' in sono_small:
                    # Extract the base path (everything before /ffts/)
                    base_path = sono_small.split('/ffts/')[0]
                    # Add https: if missing
                    if base_path.startswith('//'):
                        base_path = 'https:' + base_path
                    # Construct MP3 URL
                    sound_file_url = f"{base_path}/{quote(file_name)}"
        
        if not sound_file_url:
            logger.warning(f"No audio URL found for recording {index}")
            return False
        
        # Download audio file to local cache
        local_audio_file = download_audio_file(sound_file_url, recording_id)
        if not local_audio_file:
            logger.error(f"Failed to download audio for recording {recording_id}")
            return False
        
        # Get bird info
        bird_name = recording.get('en', 'Unknown bird')
        location_name = recording.get('loc', 'Unknown location')
        
        logger.info(f"Playing: {bird_name}, {location_name}")
        print(f"♪ {bird_name}, {location_name}")
        
        # Play audio from local file using command-line tools
        import subprocess
        
        # Try ffplay first (handles all formats), then mpg123 as fallback
        players = [
            (['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', local_audio_file], 'ffplay'),
            (['mpg123', '-q', local_audio_file], 'mpg123'),
            (['cvlc', '--play-and-exit', '--quiet', local_audio_file], 'vlc')
        ]
        
        played_successfully = False
        last_error = None
        for player_cmd, player_name in players:
            try:
                result = subprocess.run(player_cmd, capture_output=True, timeout=300)
                if result.returncode == 0:
                    played_successfully = True
                    break
                else:
                    last_error = f"{player_name} returned error code {result.returncode}: {result.stderr.decode()[:200]}"
                    logger.debug(last_error)
            except FileNotFoundError:
                logger.debug(f"{player_name} not found")
                continue
            except subprocess.TimeoutExpired:
                logger.warning(f"Playback timeout for {bird_name}")
                return False
            except Exception as e:
                last_error = str(e)
                logger.debug(f"{player_name} error: {e}")
                continue
        
        if not played_successfully:
            logger.error(f"All audio players failed. Last error: {last_error}")
            logger.error("Install audio players with: sudo apt-get install ffmpeg mpg123")
            logger.error(f"Tried to play: {local_audio_file}")
            return False
        
        # Short pause between songs
        time.sleep(2)
        return True
        
    except (KeyError, IndexError) as e:
        logger.error(f"Error accessing recording data: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error playing audio: {e}")
        return False

def load_countries():
    """Load countries from config file"""
    try:
        with open('countries.json') as f:
            data = json.load(f)
            return data.get('countries', [])
    except Exception as e:
        logger.error(f"Error loading countries: {e}")
        return []

def main():
    """Main loop with improved error handling and efficiency"""
    logger.info("Starting BirdFM...")
    
    # Get API key
    api_key = get_api_key()
    
    # Load countries once at startup
    countries = load_countries()
    if not countries:
        logger.error("No countries configured. Please check countries.json")
        return
    
    logger.info(f"Loaded {len(countries)} countries")
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            logger.info(f"Starting iteration {iteration}")
            
            # Clean up old audio files at the start of each cycle
            if iteration > 1:  # Skip on first iteration
                cleanup_old_audio_cache()
            
            for country in countries:
                logger.info(f"Processing country: {country}")
                
                # Make API call with caching
                xeno_data = make_api_call(country, 1, api_key)
                
                if not xeno_data or 'recordings' not in xeno_data:
                    logger.warning(f"No data available for {country}")
                    continue
                
                num_recordings = int(xeno_data.get('numRecordings', 0))
                logger.info(f"Found {num_recordings} recordings for {country}")
                
                # Download and play each recording
                success_count = 0
                for i in range(num_recordings):
                    if play_birdsong(xeno_data, i):
                        success_count += 1
                
                logger.info(f"Successfully played {success_count}/{num_recordings} recordings")
            
            logger.info(f"Completed iteration {iteration}. Starting next cycle...")
            
        except KeyboardInterrupt:
            logger.info("Shutting down BirdFM...")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

if __name__ == "__main__":
    main()