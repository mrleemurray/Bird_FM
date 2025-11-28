# BirdFM - Xeno-Canto Bird Sound Player

A Raspberry Pi Zero W application that plays bird songs from the Xeno-Canto API.

## Features

- ✅ **API Key Support**: Updated to work with Xeno-Canto's new API authentication
- 🌐 **Web Configuration Interface**: Configure settings from any device on your network
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

3. Start the services:
```bash
sudo systemctl start birdfm
sudo systemctl start birdfm-web
```

4. Configure via web interface:
Open `http://birdbox.local:5000` in your browser to set your API key and countries.

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

## Web Configuration Interface

BirdFM includes a web-based configuration interface that allows you to manage settings without SSH access.

### Access the Web Interface

After installation, access the web interface from any device on your network:

```
http://birdbox.local:5000
```

Or use the Raspberry Pi's IP address:
```
http://192.168.1.xxx:5000
```

### Web Interface Features

- **Dashboard**: View service status, API configuration, and active countries
- **API Settings**: Configure your Xeno-Canto API key
- **Countries Management**: Add/remove countries with one-click suggestions
- **Service Control**: Restart the BirdFM service directly from the web
- **Log Viewer**: View recent application logs in real-time

### Security Note

The web interface runs on your local network only. For production use:
1. Change the default secret key in `web_server.py`
2. Consider adding authentication
3. Use a reverse proxy with HTTPS if exposing to the internet

## Service Management

The installation creates two systemd services:

### BirdFM Main Service
- ✅ Plays bird songs automatically
- ✅ Starts automatically on boot
- ✅ Restarts automatically on crash (10 second delay)
- ✅ Logs to `logs/birdfm.log` and `logs/birdfm-error.log`

### BirdFM Web Service
- ✅ Provides web configuration interface
- ✅ Starts automatically on boot
- ✅ Restarts automatically on crash
- ✅ Logs to `logs/webserver.log` and `logs/webserver-error.log`

### Service Commands

```bash
# Main BirdFM service
sudo systemctl start birdfm      # Start the service
sudo systemctl stop birdfm       # Stop the service
sudo systemctl restart birdfm    # Restart the service
sudo systemctl status birdfm     # Check status

# Web interface service
sudo systemctl start birdfm-web      # Start the web interface
sudo systemctl stop birdfm-web       # Stop the web interface
sudo systemctl restart birdfm-web    # Restart the web interface
sudo systemctl status birdfm-web     # Check status

# Both services
sudo systemctl enable birdfm birdfm-web     # Enable auto-start on boot
sudo systemctl disable birdfm birdfm-web    # Disable auto-start
```

### View Logs

```bash
# Application logs
tail -f logs/birdfm.log
tail -f logs/webserver.log

# Service logs
journalctl -u birdfm.service -f
journalctl -u birdfm-web.service -f

# Error logs
tail -f logs/birdfm-error.log
tail -f logs/webserver-error.log
```

## Configuration

### Method 1: Web Interface (Recommended)

The easiest way to configure BirdFM is through the web interface:

1. Open `http://birdbox.local:5000` in your browser
2. Navigate to **API Settings** and enter your Xeno-Canto API key
3. Navigate to **Countries** to select which countries' bird songs to play
4. Click **Save** and restart the service from the dashboard

### Method 2: Manual Configuration (Advanced)

**API Key Setup via Config File**

```bash
nano config.json
```

Add your key:
```json
{
    "api_key": "your_xeno_canto_api_key_here"
}
```

**API Key via Environment Variable**

```bash
export XENO_CANTO_API_KEY="your_api_key_here"
```

**Countries Configuration**

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

### Cannot access web interface
- Check service status: `sudo systemctl status birdfm-web`
- Verify port 5000 is not blocked by firewall
- Try using IP address instead of hostname: `http://192.168.1.xxx:5000`
- View logs: `tail -f logs/webserver.log`

### Audio playback issues
- Ensure `mpg123` is installed: `sudo apt-get install mpg123`
- Check audio output: `speaker-test -t wav -c 2`
- View logs: `tail -f logs/birdfm.log`

### API errors
- Verify your API key is correct via the web interface or `config.json`
- Check `logs/birdfm.log` for error messages
- Ensure internet connection is working
- Test API with: `python3 test_api.py`

### High memory usage
- Reduce `MAX_RECORDINGS_PER_COUNTRY` in `BirdFM.py`
- Increase `CACHE_EXPIRY_HOURS` to reduce API calls
- Restart services to clear memory

### Service not starting
- Check status: `sudo systemctl status birdfm birdfm-web`
- View errors: `journalctl -u birdfm.service -n 50`
- Ensure virtual environment is activated: `source venv/bin/activate`
- Verify all dependencies are installed: `pip list`

## About Bird Feathers

Bird feathers are remarkable structures that serve multiple functions beyond just flight. Understanding feather types can enhance your bird watching experience:

### Feather Types
- **Contour Feathers**: The outer layer that gives birds their shape and color
- **Down Feathers**: Fluffy insulation feathers that trap air for warmth
- **Flight Feathers**: Specialized wing and tail feathers for aerodynamics
- **Filoplumes**: Sensory feathers that detect air movement and feather position

### Interesting Facts
- Birds molt (shed and regrow) their feathers regularly to maintain flight capability
- Feather colors come from pigments and microscopic structures that reflect light
- Some birds can control individual feathers for precise flight adjustments
- Feathers are made of keratin, the same protein found in human hair and nails

### Identification Tips
- Look for distinctive feather patterns and colors when identifying birds
- Wing bars, eye rings, and tail patterns are key field marks
- Breeding vs. non-breeding plumage can vary dramatically in some species

For more detailed bird identification information, check out the `BIRD_SPECIES_GUIDE.md` file.

## License

See LICENSE file for details.
