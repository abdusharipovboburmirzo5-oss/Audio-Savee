"""
Health Check Server for Telegram Bot
Prevents server from sleeping on free hosting platforms
"""
import os
import time
import logging
from flask import Flask, jsonify
from threading import Thread

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Track when the server started
start_time = time.time()

@app.route('/')
def index():
    """Root endpoint - returns bot status"""
    uptime_seconds = int(time.time() - start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    return jsonify({
        'status': 'running',
        'service': 'Instagram Downloader Bot',
        'uptime': f'{hours}h {minutes}m {seconds}s',
        'uptime_seconds': uptime_seconds
    })

@app.route('/health')
def health():
    """Health check endpoint for monitoring services"""
    return jsonify({
        'status': 'ok',
        'uptime': int(time.time() - start_time)
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return jsonify({'pong': True})

def run_server(port=8080, host='0.0.0.0'):
    """Run the Flask server"""
    # Disable Flask's default logging to reduce noise
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)
    
    logger.info(f"🌐 Health check server starting on {host}:{port}")
    logger.info(f"📍 Endpoints: /, /health, /ping")
    
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Health server error: {e}")

def start_health_server(port=None):
    """Start the health check server in a background thread"""
    if port is None:
        # Try to get port from environment (for platforms like Render, Railway)
        port = int(os.environ.get('PORT', 8080))
    
    server_thread = Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    logger.info(f"✅ Health check server started on port {port}")
    return server_thread

if __name__ == '__main__':
    # For testing purposes
    run_server()
