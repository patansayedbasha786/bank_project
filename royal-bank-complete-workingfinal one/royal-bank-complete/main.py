import os
import sys
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.routes.bank import bank_bp

# Create Flask app
app = Flask(__name__, static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'royal-bank-secret-key-2024')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Enable CORS for all routes
CORS(app, supports_credentials=True, origins=['*'])

# Register blueprints
app.register_blueprint(bank_bp, url_prefix='/api')

# Serve static files and handle SPA routing
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve static files and handle single-page application routing"""
    static_folder_path = app.static_folder
    
    if static_folder_path is None:
        return jsonify({'error': 'Static folder not configured'}), 404

    # If path is empty or doesn't exist, serve index.html
    if path == "" or not os.path.exists(os.path.join(static_folder_path, path)):
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({'error': 'index.html not found'}), 404
    else:
        # Serve the requested file
        return send_from_directory(static_folder_path, path)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Royal Bank of India API is running',
        'version': '1.0.0'
    }), 200

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Royal Bank API endpoints are operational',
        'endpoints': [
            '/api/login',
            '/api/logout',
            '/api/session-status',
            '/api/check-user',
            '/api/create-user',
            '/api/deposit',
            '/api/withdraw',
            '/api/mini-statement',
            '/api/balance-enquiry',
            '/api/dashboard-stats'
        ]
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({'error': 'Access forbidden'}), 403

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': 'Bad request'}), 400

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('src/database', exist_ok=True)
    
    print("🏦 Royal Bank of India - Admin Portal")
    print("=====================================")
    print("🚀 Starting server...")
    print("📍 Access the application at: http://localhost:5000")
    print("🔐 Default login credentials:")
    print("   Username: sk")
    print("   Password: 00")
    print("📊 Database: SQLite (royal_bank.db)")
    print("=====================================")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

