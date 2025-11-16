# BirdFM - Xeno-Canto Bird Sound Player

A Raspberry Pi Zero W application that plays bird songs from the Xeno-Canto API.

## Features

- ✅ **API Key Support**: Updated to work with Xeno-Canto's new API authentication
- 🗄️ **Smart Caching**: Caches API responses for 24 hours to reduce API calls
- ⏱️ **Rate Limiting**: 2-second delay between API calls to avoid spamming
- 🔄 **Retry Logic**: Automatic retry with exponential backoff for failed requests
- 📝 **Logging**: Comprehensive logging to file and console
- 🎯 **Memory Efficient**: Limits recordings per country (default: 50) for Pi Zero W
- 🛡️ **Robust Error Handling**: Graceful degradation for network and playback issues
- 🔊 **Fallback Playback**: Uses mpg123 if playsound fails

## Quick Start (Raspberry Pi)

### Option 1: Automated Deployment (Recommended)

From your local machine, deploy directly to your Pi:

```bash
./deploy.sh
```

This will copy files and run the installation automatically.

### Option 2: Manual Installation on Pi

1. Copy files to your Raspberry Pi:
```bash
scp -r * lee@birdbox.local:/home/lee/BirdFM/
```

2. SSH into your Pi and run the installation script:
```bash
ssh lee@birdbox.local
cd ~/BirdFM
./install.sh
```

3. Edit the config file to add your API key:
```bash
nano config.json
```

4. Start the service:
```bash
sudo systemctl start birdfm
```

## Installation Scripts

### `install.sh`
Complete installation on Raspberry Pi:
- Installs system dependencies (Python, mpg123, audio libraries)
- Creates Python virtual environment
- Installs Python packages
- Sets up systemd service for auto-start and auto-recovery
- Configures audio output

### `deploy.sh`
Deploy from your local machine to Pi:
- Copies files via rsync
- Optionally runs installation
- Customizable via environment variables:
  ```bash
  PI_USER=pi PI_HOST=raspberrypi.local ./deploy.sh
  ```

### `update.sh`
Update BirdFM on Pi without full reinstall:
- Stops service
- Updates Python packages
- Restarts service

### `uninstall.sh`
Remove BirdFM service from Pi:
- Stops and disables service
- Removes systemd configuration
- Leaves application files intact

## Service Management

The installation creates a systemd service that:
- ✅ Starts automatically on boot
- ✅ Restarts automatically on crash (10 second delay)
- ✅ Recovers from errors automatically
- ✅ Logs to `logs/birdfm.log` and `logs/birdfm-error.log`

### Service Commands

```bash
sudo systemctl start birdfm      # Start the service
sudo systemctl stop birdfm       # Stop the service
sudo systemctl restart birdfm    # Restart the service
sudo systemctl status birdfm     # Check status
sudo systemctl enable birdfm     # Enable auto-start on boot
sudo systemctl disable birdfm    # Disable auto-start
```

### View Logs

```bash
# Application logs
tail -f logs/birdfm.log
tail -f birdfm.log

# Service logs
journalctl -u birdfm.service -f

# Error logs
tail -f logs/birdfm-error.log
```

## Configuration

### API Key Setup

**Option A: Config File (Recommended for Pi)**

```bash
nano config.json
```

Add your key:
```json
{
    "api_key": "your_xeno_canto_api_key_here"
}
```

**Option B: Environment Variable**

```bash
export XENO_CANTO_API_KEY="your_api_key_here"
```

### Countries Configuration

Edit `countries.json` to specify which countries' bird songs to play:

```json
{
    "countries": [
        "United Kingdom",
        "United States",
        "Australia"
    ]
}
```

## Configuration Options

Edit these constants in `BirdFM.py`:

- `CACHE_EXPIRY_HOURS`: How long to cache API responses (default: 24 hours)
- `API_DELAY_SECONDS`: Delay between API calls (default: 2 seconds)
- `MAX_RECORDINGS_PER_COUNTRY`: Limit recordings per country (default: 50)

## Cache Management

The script creates a `cache/` directory to store API responses. To clear the cache:

```bash
rm -rf cache/
```

## Logs

Logs are written to `birdfm.log` in the same directory. To monitor in real-time:

```bash
tail -f birdfm.log
```

## Getting a Xeno-Canto API Key

1. Visit [xeno-canto.org](https://xeno-canto.org)
2. Create an account or log in
3. Request an API key from your account settings
4. Add the key to your configuration as described above

## Troubleshooting

### Audio playback issues
- Ensure `mpg123` is installed: `sudo apt-get install mpg123`
- Check audio output: `speaker-test -t wav -c 2`

### API errors
- Verify your API key is correct
- Check `birdfm.log` for error messages
- Ensure internet connection is working

### High memory usage
- Reduce `MAX_RECORDINGS_PER_COUNTRY` in the script
- Increase `CACHE_EXPIRY_HOURS` to reduce API calls

## License

See LICENSE file for details.
