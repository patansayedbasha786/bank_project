from flask import Blueprint, request, jsonify, session
from src.database.bank_db import BankDatabase
import traceback

bank_bp = Blueprint('bank', __name__)
db = BankDatabase()

@bank_bp.route('/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        table_name = data.get('table_name', 'bank_transactions')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        if db.authenticate_user(username, password):
            # Create table if it doesn't exist
            db.create_table_if_not_exists(table_name)
            
            # Store session data
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

@bank_bp.route('/logout', methods=['POST'])
def logout():
    """Admin logout endpoint"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@bank_bp.route('/session-status', methods=['GET'])
def session_status():
    """Check session status"""
    try:
        if session.get('authenticated'):
            return jsonify({
                'authenticated': True,
                'table_name': session.get('table_name'),
                'username': session.get('username')
            }), 200
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        return jsonify({'error': f'Session check failed: {str(e)}'}), 500

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bank_bp.route('/check-user', methods=['POST'])
@require_auth
def check_user():
    """Check if user exists and get user information"""
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        table_name = session.get('table_name')
        
        if not aadhar_no:
            return jsonify({'error': 'Aadhar number is required'}), 400
        
        # Validate Aadhar number format
        if len(aadhar_no) != 12 or not aadhar_no.isdigit():
            return jsonify({'error': 'Invalid Aadhar number format'}), 400
        
        user_info = db.get_user_latest_record(table_name, aadhar_no)
        
        if user_info:
            return jsonify({
                'exists': True,
                'user_info': user_info
            }), 200
        else:
            return jsonify({
                'exists': False,
                'message': 'User not found'
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to check user: {str(e)}'}), 500

@bank_bp.route('/create-user', methods=['POST'])
@require_auth
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        table_name = session.get('table_name')
        
        # Validate required fields
        required_fields = ['aadhar_no', 'name_of_user', 'address', 'phone_no', 'nominee_aadhar_no', 'balance']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate Aadhar numbers
        if len(data['aadhar_no']) != 12 or not data['aadhar_no'].isdigit():
            return jsonify({'error': 'Invalid Aadhar number format'}), 400
        
        if len(data['nominee_aadhar_no']) != 12 or not data['nominee_aadhar_no'].isdigit():
            return jsonify({'error': 'Invalid nominee Aadhar number format'}), 400
        
        # Validate phone number
        if len(data['phone_no']) != 10 or not data['phone_no'].isdigit():
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Validate balance
        try:
            balance = float(data['balance'])
            if balance < 0:
                return jsonify({'error': 'Balance cannot be negative'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid balance amount'}), 400
        
        # Prepare user data
        user_data = {
            'aadhar_no': data['aadhar_no'],
            'name_of_user': data['name_of_user'].strip(),
            'address': data['address'].strip(),
            'phone_no': data['phone_no'],
            'nominee_aadhar_no': data['nominee_aadhar_no'],
            'balance': balance,
            'withdrawal': float(data.get('withdrawal', 0)),
            'deposit': float(data.get('deposit', 0))
        }
        
        db.create_user(table_name, user_data)
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_data': user_data
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500

@bank_bp.route('/deposit', methods=['POST'])
@require_auth
def deposit():
    """Process deposit transaction"""
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        amount = data.get('amount')
        table_name = session.get('table_name')
        
        if not aadhar_no or not amount:
            return jsonify({'error': 'Aadhar number and amount are required'}), 400
        
        # Validate Aadhar number
        if len(aadhar_no) != 12 or not aadhar_no.isdigit():
            return jsonify({'error': 'Invalid Aadhar number format'}), 400
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({'error': 'Deposit amount must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid amount format'}), 400
        
        result = db.deposit_amount(table_name, aadhar_no, amount)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Deposit failed: {str(e)}'}), 500

@bank_bp.route('/withdraw', methods=['POST'])
@require_auth
def withdraw():
    """Process withdrawal transaction"""
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        amount = data.get('amount')
        table_name = session.get('table_name')
        
        if not aadhar_no or not amount:
            return jsonify({'error': 'Aadhar number and amount are required'}), 400
        
        # Validate Aadhar number
        if len(aadhar_no) != 12 or not aadhar_no.isdigit():
            return jsonify({'error': 'Invalid Aadhar number format'}), 400
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({'error': 'Withdrawal amount must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid amount format'}), 400
        
        result = db.withdraw_amount(table_name, aadhar_no, amount)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Withdrawal failed: {str(e)}'}), 500

@bank_bp.route('/mini-statement', methods=['POST'])
@require_auth
def mini_statement():
    """Generate mini statement for a user"""
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        table_name = session.get('table_name')
        
        if not aadhar_no:
            return jsonify({'error': 'Aadhar number is required'}), 400
        
        # Validate Aadhar number
        if len(aadhar_no) != 12 or not aadhar_no.isdigit():
            return jsonify({'error': 'Invalid Aadhar number format'}), 400
        
        statement = db.get_mini_statement(table_name, aadhar_no)
        
        return jsonify(statement), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate statement: {str(e)}'}), 500

@bank_bp.route('/balance-enquiry', methods=['POST'])
@require_auth
def balance_enquiry():
    """Get balance enquiry for a user"""
    try:
        data = request.get_json()
        aadhar_no = data.get('aadhar_no')
        table_name = session.get('table_name')
        
        if not aadhar_no:
            return jsonify({'error': 'Aadhar number is required'}), 400
        
        # Validate Aadhar number
        if len(aadhar_no) != 12 or not aadhar_no.isdigit():
            return jsonify({'error': 'Invalid Aadhar number format'}), 400
        
        balance_info = db.get_balance_enquiry(table_name, aadhar_no)
        
        return jsonify(balance_info), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get balance: {str(e)}'}), 500

@bank_bp.route('/dashboard-stats', methods=['GET'])
@require_auth
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        table_name = session.get('table_name')
        stats = db.get_dashboard_stats(table_name)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({
            'totalUsers': 0,
            'totalDeposits': 0,
            'totalWithdrawals': 0,
            'totalBalance': 0
        }), 200

# Error handlers
@bank_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@bank_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@bank_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

