import psycopg2
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class BankDatabase:
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'royal_bank_of_india'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
    
    def get_connection(self):
        """Establish connection to PostgreSQL database"""
        try:
            return psycopg2.connect(**self.db_config)
        except psycopg2.Error as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    def create_table_if_not_exists(self, table_name: str):
        """Create table if it doesn't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    aadhar_no BIGINT NOT NULL,
                    name_of_user VARCHAR(100) NOT NULL,
                    address VARCHAR(200),
                    phone_no BIGINT,
                    nominee_aadhar_no BIGINT,
                    balance BIGINT DEFAULT 0,
                    withdrawal BIGINT DEFAULT 0,
                    deposit BIGINT DEFAULT 0,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except psycopg2.Error as e:
            raise Exception(f"Table creation failed: {str(e)}")
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate admin user"""
        # Simple authentication - in production, use proper hashing
        return username == "sk" and password == "00"
    
    def get_user_latest_record(self, table_name: str, aadhar_no: int) -> Optional[Dict[str, Any]]:
        """Get the latest record for a user by Aadhar number"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT * FROM {table_name} 
                WHERE aadhar_no = %s
                ORDER BY transaction_date DESC, id DESC 
                LIMIT 1
            """, (aadhar_no,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'aadhar_no': result[1],
                    'name_of_user': result[2],
                    'address': result[3],
                    'phone_no': result[4],
                    'nominee_aadhar_no': result[5],
                    'balance': result[6],
                    'withdrawal': result[7],
                    'deposit': result[8],
                    'transaction_date': result[9]
                }
            return None
        except psycopg2.Error as e:
            raise Exception(f"Failed to fetch user record: {str(e)}")
    
    def create_user(self, table_name: str, user_data: Dict[str, Any]) -> bool:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                INSERT INTO {table_name} (
                    aadhar_no, name_of_user, address, phone_no,
                    nominee_aadhar_no, balance, withdrawal, deposit
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_data['aadhar_no'],
                user_data['name_of_user'],
                user_data['address'],
                user_data['phone_no'],
                user_data['nominee_aadhar_no'],
                user_data['balance'],
                user_data.get('withdrawal', 0),
                user_data.get('deposit', 0)
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except psycopg2.Error as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    def deposit_amount(self, table_name: str, aadhar_no: int, deposit_amount: int) -> Dict[str, Any]:
        """Process deposit transaction"""
        try:
            # Get current user record
            current_record = self.get_user_latest_record(table_name, aadhar_no)
            if not current_record:
                raise Exception("User not found")
            
            new_balance = current_record['balance'] + deposit_amount
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                INSERT INTO {table_name} (
                    aadhar_no, name_of_user, address, phone_no,
                    nominee_aadhar_no, balance, withdrawal, deposit
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
    
    def withdraw_amount(self, table_name: str, aadhar_no: int, withdrawal_amount: int) -> Dict[str, Any]:
        """Process withdrawal transaction"""
        try:
            # Get current user record
            current_record = self.get_user_latest_record(table_name, aadhar_no)
            if not current_record:
                raise Exception("User not found")
            
            if withdrawal_amount > current_record['balance']:
                raise Exception("Insufficient balance")
            
            new_balance = current_record['balance'] - withdrawal_amount
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                INSERT INTO {table_name} (
                    aadhar_no, name_of_user, address, phone_no,
                    nominee_aadhar_no, balance, withdrawal, deposit
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
    
    def get_mini_statement(self, table_name: str, aadhar_no: int) -> Dict[str, Any]:
        """Get mini statement for a user"""
        try:
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
                WHERE aadhar_no = %s
                ORDER BY transaction_date DESC, id DESC
                LIMIT 10
            """, (aadhar_no,))
            
            transactions = cursor.fetchall()
            cursor.close()
            conn.close()
            
            transaction_list = []
            for transaction in transactions:
                transaction_list.append({
                    'withdrawal': transaction[0] if transaction[0] else 0,
                    'deposit': transaction[1] if transaction[1] else 0,
                    'balance': transaction[2],
                    'date': transaction[3].strftime('%Y-%m-%d %H:%M:%S') if transaction[3] else None
                })
            
            return {
                'user_info': current_record,
                'transactions': transaction_list,
                'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            raise Exception(f"Failed to get mini statement: {str(e)}")
    
    def get_balance_enquiry(self, table_name: str, aadhar_no: int) -> Dict[str, Any]:
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

