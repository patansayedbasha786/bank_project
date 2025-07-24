import os
import sys
from flask import Flask, send_from_directory, jsonify, session, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import threading

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask app
app = Flask(__name__, static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'royal-bank-secret-key-2024')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Enable CORS for all routes
CORS(app, supports_credentials=True, origins=['*'])

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'royal_bank.db')
DB_LOCK = threading.Lock()

def init_database():
    """Initialize the database"""
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bank_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aadhar_no TEXT NOT NULL,
                    name_of_user TEXT NOT NULL,
                    address TEXT,
                    phone_no TEXT,
                    nominee_aadhar_no TEXT,
                    balance REAL DEFAULT 0,
                    withdrawal REAL DEFAULT 0,
                    deposit REAL DEFAULT 0,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def authenticate_user(username, password):
    """Simple authentication"""
    return username == "sk" and password == "00"

# API Routes
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        table_name = data.get('table_name', 'bank_transactions')
        
        if authenticate_user(username, password):
            session['authenticated'] = True
            session['table_name'] = table_name
            session['username'] = username
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'table_name': table_name
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

@app.route('/api/session-status', methods=['GET'])
def session_status():
    if session.get('authenticated'):
        return jsonify({
            'authenticated': True,
            'table_name': session.get('table_name'),
            'username': session.get('username')
        }), 200
    else:
        return jsonify({'authenticated': False}), 200

@app.route('/api/check-user', methods=['POST'])
def check_user():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        
        with DB_LOCK:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM bank_transactions 
                WHERE aadhar_no = ?
                ORDER BY transaction_date DESC, id DESC 
                LIMIT 1
            """, (aadhar_no,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_info = {
                    'id': result['id'],
                    'aadhar_no': result['aadhar_no'],
                    'name_of_user': result['name_of_user'],
                    'address': result['address'],
                    'phone_no': result['phone_no'],
                    'nominee_aadhar_no': result['nominee_aadhar_no'],
                    'balance': float(result['balance']),
                    'withdrawal': float(result['withdrawal']),
                    'deposit': float(result['deposit']),
                    'transaction_date': result['transaction_date']
                }
                return jsonify({'exists': True, 'user_info': user_info}), 200
            else:
                return jsonify({'exists': False, 'message': 'User not found'}), 200
                
    except Exception as e:
        return jsonify({'error': f'Failed to check user: {str(e)}'}), 500

@app.route('/api/create-user', methods=['POST'])
def create_user():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        # Check if user already exists
        with DB_LOCK:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM bank_transactions WHERE aadhar_no = ? LIMIT 1", (data['aadhar_no'],))
            if cursor.fetchone():
                conn.close()
                return jsonify({'error': 'User with this Aadhar number already exists'}), 400
            
            cursor.execute("""
                INSERT INTO bank_transactions (
                    aadhar_no, name_of_user, address, phone_no,
                    nominee_aadhar_no, balance, withdrawal, deposit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['aadhar_no'],
                data['name_of_user'],
                data['address'],
                data['phone_no'],
                data['nominee_aadhar_no'],
                float(data['balance']),
                0,
                0
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'User created successfully'}), 201
            
    except Exception as e:
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500

@app.route('/api/deposit', methods=['POST'])
def deposit():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        amount = float(data.get('amount'))
        
        with DB_LOCK:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get current balance
            cursor.execute("""
                SELECT * FROM bank_transactions 
                WHERE aadhar_no = ?
                ORDER BY transaction_date DESC, id DESC 
                LIMIT 1
            """, (aadhar_no,))
            
            current_record = cursor.fetchone()
            if not current_record:
                conn.close()
                return jsonify({'error': 'User not found'}), 404
            
            new_balance = float(current_record['balance']) + amount
            
            # Insert new transaction
            cursor.execute("""
                INSERT INTO bank_transactions (
                    aadhar_no, name_of_user, address, phone_no,
                    nominee_aadhar_no, balance, withdrawal, deposit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                current_record['aadhar_no'],
                current_record['name_of_user'],
                current_record['address'],
                current_record['phone_no'],
                current_record['nominee_aadhar_no'],
                new_balance,
                0,
                amount
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'new_balance': new_balance,
                'deposit_amount': amount
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Deposit failed: {str(e)}'}), 500

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        amount = float(data.get('amount'))
        
        with DB_LOCK:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get current balance
            cursor.execute("""
                SELECT * FROM bank_transactions 
                WHERE aadhar_no = ?
                ORDER BY transaction_date DESC, id DESC 
                LIMIT 1
            """, (aadhar_no,))
            
            current_record = cursor.fetchone()
            if not current_record:
                conn.close()
                return jsonify({'error': 'User not found'}), 404
            
            current_balance = float(current_record['balance'])
            if amount > current_balance:
                conn.close()
                return jsonify({'error': 'Insufficient balance'}), 400
            
            new_balance = current_balance - amount
            
            # Insert new transaction
            cursor.execute("""
                INSERT INTO bank_transactions (
                    aadhar_no, name_of_user, address, phone_no,
                    nominee_aadhar_no, balance, withdrawal, deposit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                current_record['aadhar_no'],
                current_record['name_of_user'],
                current_record['address'],
                current_record['phone_no'],
                current_record['nominee_aadhar_no'],
                new_balance,
                amount,
                0
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'new_balance': new_balance,
                'withdrawal_amount': amount
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Withdrawal failed: {str(e)}'}), 500

@app.route('/api/balance-enquiry', methods=['POST'])
def balance_enquiry():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        
        with DB_LOCK:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM bank_transactions 
                WHERE aadhar_no = ?
                ORDER BY transaction_date DESC, id DESC 
                LIMIT 1
            """, (aadhar_no,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return jsonify({
                    'name': result['name_of_user'],
                    'balance': float(result['balance']),
                    'aadhar_no': result['aadhar_no'],
                    'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }), 200
            else:
                return jsonify({'error': 'User not found'}), 404
                
    except Exception as e:
        return jsonify({'error': f'Failed to get balance: {str(e)}'}), 500

@app.route('/api/mini-statement', methods=['POST'])
def mini_statement():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        
        with DB_LOCK:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user info
            cursor.execute("""
                SELECT * FROM bank_transactions 
                WHERE aadhar_no = ?
                ORDER BY transaction_date DESC, id DESC 
                LIMIT 1
            """, (aadhar_no,))
            
            current_record = cursor.fetchone()
            if not current_record:
                conn.close()
                return jsonify({'error': 'User not found'}), 404
            
            # Get transaction history
            cursor.execute("""
                SELECT withdrawal, deposit, balance, transaction_date 
                FROM bank_transactions 
                WHERE aadhar_no = ?
                ORDER BY transaction_date DESC, id DESC
                LIMIT 10
            """, (aadhar_no,))
            
            transactions = cursor.fetchall()
            conn.close()
            
            user_info = {
                'aadhar_no': current_record['aadhar_no'],
                'name_of_user': current_record['name_of_user'],
                'address': current_record['address'],
                'phone_no': current_record['phone_no'],
                'balance': float(current_record['balance'])
            }
            
            transaction_list = []
            for transaction in transactions:
                transaction_list.append({
                    'withdrawal': float(transaction['withdrawal']) if transaction['withdrawal'] else 0,
                    'deposit': float(transaction['deposit']) if transaction['deposit'] else 0,
                    'balance': float(transaction['balance']),
                    'date': transaction['transaction_date']
                })
            
            return jsonify({
                'user_info': user_info,
                'transactions': transaction_list,
                'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to generate statement: {str(e)}'}), 500

@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        with DB_LOCK:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get unique users count
            cursor.execute("SELECT COUNT(DISTINCT aadhar_no) as total_users FROM bank_transactions")
            total_users = cursor.fetchone()['total_users']
            
            # Get total deposits
            cursor.execute("SELECT COALESCE(SUM(deposit), 0) as total_deposits FROM bank_transactions WHERE deposit > 0")
            total_deposits = cursor.fetchone()['total_deposits']
            
            # Get total withdrawals
            cursor.execute("SELECT COALESCE(SUM(withdrawal), 0) as total_withdrawals FROM bank_transactions WHERE withdrawal > 0")
            total_withdrawals = cursor.fetchone()['total_withdrawals']
            
            conn.close()
            
            return jsonify({
                'totalUsers': int(total_users),
                'totalDeposits': float(total_deposits),
                'totalWithdrawals': float(total_withdrawals),
                'totalBalance': float(total_deposits) - float(total_withdrawals)
            }), 200
            
    except Exception as e:
        return jsonify({
            'totalUsers': 0,
            'totalDeposits': 0,
            'totalWithdrawals': 0,
            'totalBalance': 0
        }), 200

# Serve static files and handle SPA routing
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    
    if static_folder_path is None:
        return jsonify({'error': 'Static folder not configured'}), 404

    if path == "" or not os.path.exists(os.path.join(static_folder_path, path)):
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({'error': 'index.html not found'}), 404
    else:
        return send_from_directory(static_folder_path, path)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Royal Bank of India API is running',
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    # Initialize database
    init_database()
    
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

