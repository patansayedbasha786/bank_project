import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import threading

class BankDatabase:
    def __init__(self):
        # Use SQLite for simplicity - no external database required
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'royal_bank.db')
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create default table if it doesn't exist"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Create default table
                self.create_table_if_not_exists('bank_transactions')
                
                conn.close()
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
    
    def get_connection(self):
        """Establish connection to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except sqlite3.Error as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    def create_table_if_not_exists(self, table_name: str):
        """Create table if it doesn't exist"""
        try:
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Sanitize table name to prevent SQL injection
                if not table_name.replace('_', '').replace('-', '').isalnum():
                    raise Exception("Invalid table name")
                
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
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
                cursor.close()
                conn.close()
                return True
        except Exception as e:
            raise Exception(f"Table creation failed: {str(e)}")
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate admin user"""
        # Simple authentication - in production, use proper hashing
        return username == "sk" and password == "00"
    
    def get_user_latest_record(self, table_name: str, aadhar_no: str) -> Optional[Dict[str, Any]]:
        """Get the latest record for a user by Aadhar number"""
        try:
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    SELECT * FROM {table_name} 
                    WHERE aadhar_no = ?
                    ORDER BY transaction_date DESC, id DESC 
                    LIMIT 1
                """, (aadhar_no,))
                
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    return {
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
                return None
        except Exception as e:
            raise Exception(f"Failed to fetch user record: {str(e)}")
    
    def create_user(self, table_name: str, user_data: Dict[str, Any]) -> bool:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = self.get_user_latest_record(table_name, user_data['aadhar_no'])
            if existing_user:
                raise Exception("User with this Aadhar number already exists")
            
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    INSERT INTO {table_name} (
                        aadhar_no, name_of_user, address, phone_no,
                        nominee_aadhar_no, balance, withdrawal, deposit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data['aadhar_no'],
                    user_data['name_of_user'],
                    user_data['address'],
                    user_data['phone_no'],
                    user_data['nominee_aadhar_no'],
                    float(user_data['balance']),
                    float(user_data.get('withdrawal', 0)),
                    float(user_data.get('deposit', 0))
                ))
                
                conn.commit()
                cursor.close()
                conn.close()
                return True
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    def deposit_amount(self, table_name: str, aadhar_no: str, deposit_amount: float) -> Dict[str, Any]:
        """Process deposit transaction"""
        try:
            # Get current user record
            current_record = self.get_user_latest_record(table_name, aadhar_no)
            if not current_record:
                raise Exception("User not found")
            
            new_balance = current_record['balance'] + deposit_amount
            
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    INSERT INTO {table_name} (
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
                    deposit_amount
                ))
                
                conn.commit()
                cursor.close()
                conn.close()
            
            return {
                'success': True,
                'new_balance': new_balance,
                'deposit_amount': deposit_amount,
                'message': 'Deposit successful'
            }
        except Exception as e:
            raise Exception(f"Deposit failed: {str(e)}")
    
    def withdraw_amount(self, table_name: str, aadhar_no: str, withdrawal_amount: float) -> Dict[str, Any]:
        """Process withdrawal transaction"""
        try:
            # Get current user record
            current_record = self.get_user_latest_record(table_name, aadhar_no)
            if not current_record:
                raise Exception("User not found")
            
            if withdrawal_amount > current_record['balance']:
                raise Exception("Insufficient balance")
            
            new_balance = current_record['balance'] - withdrawal_amount
            
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    INSERT INTO {table_name} (
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
                    withdrawal_amount,
                    0
                ))
                
                conn.commit()
                cursor.close()
                conn.close()
            
            return {
                'success': True,
                'new_balance': new_balance,
                'withdrawal_amount': withdrawal_amount,
                'message': 'Withdrawal successful'
            }
        except Exception as e:
            raise Exception(f"Withdrawal failed: {str(e)}")
    
    def get_mini_statement(self, table_name: str, aadhar_no: str) -> Dict[str, Any]:
        """Get mini statement for a user"""
        try:
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Get user info
                current_record = self.get_user_latest_record(table_name, aadhar_no)
                if not current_record:
                    raise Exception("User not found")
                
                # Get transaction history
                cursor.execute(f"""
                    SELECT withdrawal, deposit, balance, transaction_date 
                    FROM {table_name} 
                    WHERE aadhar_no = ?
                    ORDER BY transaction_date DESC, id DESC
                    LIMIT 10
                """, (aadhar_no,))
                
                transactions = cursor.fetchall()
                cursor.close()
                conn.close()
                
                transaction_list = []
                for transaction in transactions:
                    transaction_list.append({
                        'withdrawal': float(transaction['withdrawal']) if transaction['withdrawal'] else 0,
                        'deposit': float(transaction['deposit']) if transaction['deposit'] else 0,
                        'balance': float(transaction['balance']),
                        'date': transaction['transaction_date']
                    })
                
                return {
                    'user_info': current_record,
                    'transactions': transaction_list,
                    'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            raise Exception(f"Failed to get mini statement: {str(e)}")
    
    def get_balance_enquiry(self, table_name: str, aadhar_no: str) -> Dict[str, Any]:
        """Get balance enquiry for a user"""
        try:
            current_record = self.get_user_latest_record(table_name, aadhar_no)
            if not current_record:
                raise Exception("User not found")
            
            return {
                'name': current_record['name_of_user'],
                'balance': current_record['balance'],
                'aadhar_no': current_record['aadhar_no'],
                'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            raise Exception(f"Failed to get balance: {str(e)}")
    
    def get_dashboard_stats(self, table_name: str) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            with self.lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Get unique users count
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT aadhar_no) as total_users FROM {table_name}
                """)
                total_users = cursor.fetchone()['total_users']
                
                # Get total deposits
                cursor.execute(f"""
                    SELECT COALESCE(SUM(deposit), 0) as total_deposits FROM {table_name}
                    WHERE deposit > 0
                """)
                total_deposits = cursor.fetchone()['total_deposits']
                
                # Get total withdrawals
                cursor.execute(f"""
                    SELECT COALESCE(SUM(withdrawal), 0) as total_withdrawals FROM {table_name}
                    WHERE withdrawal > 0
                """)
                total_withdrawals = cursor.fetchone()['total_withdrawals']
                
                cursor.close()
                conn.close()
                
                return {
                    'totalUsers': int(total_users),
                    'totalDeposits': float(total_deposits),
                    'totalWithdrawals': float(total_withdrawals),
                    'totalBalance': float(total_deposits) - float(total_withdrawals)
                }
        except Exception as e:
            return {
                'totalUsers': 0,
                'totalDeposits': 0,
                'totalWithdrawals': 0,
                'totalBalance': 0
            }

