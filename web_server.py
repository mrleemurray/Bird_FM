#!/usr/bin/env python3
"""
BirdFM Web Configuration Interface
A Flask web server for configuring BirdFM settings without SSH access
"""

import os
import json
import logging
import subprocess
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webserver.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'birdfm-secret-key-change-in-production')

# File paths
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.json'
COUNTRIES_FILE = BASE_DIR / 'countries.json'
CONFIG_EXAMPLE = BASE_DIR / 'config.json.example'

def load_json_file(filepath, default=None):
    """Load JSON file with error handling"""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default or {}
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default or {}

def save_json_file(filepath, data):
    """Save JSON file with error handling"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False

def get_service_status():
    """Get BirdFM service status"""
    try:
        result = subprocess.run(
            ['/usr/bin/systemctl', 'is-active', 'birdfm.service'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Error checking service status: {e}")
        return "unknown"

def restart_service():
    """Restart BirdFM service"""
    try:
        subprocess.run(
            ['/usr/bin/sudo', '/usr/bin/systemctl', 'restart', 'birdfm.service'],
            check=True,
            timeout=10
        )
        logger.info("BirdFM service restarted")
        return True
    except Exception as e:
        logger.error(f"Error restarting service: {e}")
        return False

@app.route('/')
def index():
    """Main dashboard"""
    config = load_json_file(CONFIG_FILE, {'api_key': ''})
    countries = load_json_file(COUNTRIES_FILE, {'countries': []})
    status = get_service_status()
    
    # Mask API key for display
    api_key_masked = None
    if config.get('api_key'):
        key = config['api_key']
        if len(key) > 8:
            api_key_masked = key[:4] + '*' * (len(key) - 8) + key[-4:]
        else:
            api_key_masked = '*' * len(key)
    
    return render_template('index.html',
                         api_key_configured=bool(config.get('api_key')),
                         api_key_masked=api_key_masked,
                         countries=countries.get('countries', []),
                         service_status=status)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Configure API settings"""
    if request.method == 'POST':
        api_key = request.form.get('api_key', '').strip()
        
        if not api_key:
            flash('API key cannot be empty', 'error')
            return redirect(url_for('settings'))
        
        config = load_json_file(CONFIG_FILE, {})
        config['api_key'] = api_key
        
        if save_json_file(CONFIG_FILE, config):
            flash('API key saved successfully', 'success')
            logger.info("API key updated via web interface")
        else:
            flash('Error saving API key', 'error')
        
        return redirect(url_for('index'))
    
    config = load_json_file(CONFIG_FILE, {'api_key': ''})
    return render_template('settings.html', config=config)

@app.route('/countries', methods=['GET', 'POST'])
def countries():
    """Configure countries list"""
    if request.method == 'POST':
        countries_text = request.form.get('countries', '').strip()
        
        # Parse countries (one per line)
        countries_list = [c.strip() for c in countries_text.split('\n') if c.strip()]
        
        if not countries_list:
            flash('Please enter at least one country', 'error')
            return redirect(url_for('countries'))
        
        countries_data = {'countries': countries_list}
        
        if save_json_file(COUNTRIES_FILE, countries_data):
            flash(f'Saved {len(countries_list)} countries successfully', 'success')
            logger.info(f"Countries updated via web interface: {countries_list}")
        else:
            flash('Error saving countries', 'error')
        
        return redirect(url_for('index'))
    
    countries_data = load_json_file(COUNTRIES_FILE, {'countries': []})
    countries_text = '\n'.join(countries_data.get('countries', []))
    return render_template('countries.html', countries_text=countries_text)

@app.route('/service/restart', methods=['POST'])
def service_restart():
    """Restart BirdFM service"""
    if restart_service():
        flash('BirdFM service restarted successfully', 'success')
    else:
        flash('Error restarting service. Check logs for details.', 'error')
    return redirect(url_for('index'))

@app.route('/system/reboot', methods=['POST'])
def system_reboot():
    """Reboot the Raspberry Pi"""
    try:
        subprocess.Popen(['/usr/bin/sudo', '/usr/sbin/reboot'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("System reboot initiated via web interface")
        return jsonify({'status': 'success', 'message': 'System is rebooting...'}), 200
    except Exception as e:
        logger.error(f"Error initiating reboot: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to reboot system'}), 500

@app.route('/api/status')
def api_status():
    """API endpoint for service status"""
    status = get_service_status()
    return jsonify({
        'status': status,
        'active': status == 'active'
    })

@app.route('/logs')
def logs():
    """View recent logs"""
    log_file = BASE_DIR / 'logs' / 'birdfm.log'
    logs_content = []
    
    try:
        if log_file.exists():
            with open(log_file, 'r') as f:
                # Get last 100 lines
                lines = f.readlines()
                logs_content = lines[-100:] if len(lines) > 100 else lines
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        logs_content = [f"Error reading logs: {e}"]
    
    return render_template('logs.html', logs=logs_content)

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs(BASE_DIR / 'logs', exist_ok=True)
    
    # Run server
    # Use 0.0.0.0 to allow access from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=False)
