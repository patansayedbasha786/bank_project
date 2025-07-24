# Royal Bank of India - Admin Portal

A complete banking management system with a modern web interface for managing customer accounts, transactions, and banking operations.

## Features

- **User Management**: Create and manage customer accounts
- **Transaction Processing**: Handle deposits and withdrawals
- **Account Inquiry**: Check user information and account balances
- **Mini Statements**: Generate transaction history reports
- **Dashboard**: Overview of banking operations and statistics
- **Secure Authentication**: Admin login system
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Frontend**: React.js with Tailwind CSS
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Authentication**: Session-based authentication
- **UI Components**: Font Awesome icons, custom animations

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Access the Application**
   - Open your web browser
   - Navigate to: `http://localhost:5000`

### Default Login Credentials
- **Username**: `sk`
- **Password**: `00`
- **Database Table**: `bank_transactions` (default)

## Application Structure

```
royal-bank-complete/
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── royal_bank.db          # SQLite database (created automatically)
├── static/
│   └── index.html         # Frontend React application
└── src/
    ├── __init__.py
    ├── database/
    │   ├── __init__.py
    │   └── bank_db.py     # Database operations
    └── routes/
        ├── __init__.py
        └── bank.py        # API endpoints
```

## API Endpoints

### Authentication
- `POST /api/login` - Admin login
- `POST /api/logout` - Admin logout
- `GET /api/session-status` - Check session status

### User Management
- `POST /api/check-user` - Check if user exists
- `POST /api/create-user` - Create new user account

### Transactions
- `POST /api/deposit` - Process deposit transaction
- `POST /api/withdraw` - Process withdrawal transaction

### Reports & Inquiries
- `POST /api/mini-statement` - Generate mini statement
- `POST /api/balance-enquiry` - Get account balance
- `GET /api/dashboard-stats` - Get dashboard statistics

### Health Check
- `GET /health` - Application health check
- `GET /api/health` - API health check

## Database Schema

The application uses SQLite with the following table structure:

```sql
CREATE TABLE bank_transactions (
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
);
```

## Usage Guide

### 1. Login
- Use the default credentials or configured admin credentials
- Select the database table name (default: `bank_transactions`)

### 2. Dashboard
- View system statistics and quick action buttons
- Navigate to different sections using the sidebar

### 3. Create User
- Fill in all required customer information
- Aadhar number must be 12 digits
- Phone number must be 10 digits
- Set initial account balance

### 4. Check User
- Enter customer's Aadhar number
- View complete customer information and current balance

### 5. Process Transactions
- **Deposits**: Add money to customer account
- **Withdrawals**: Remove money (with balance validation)

### 6. Generate Reports
- **Mini Statement**: Last 10 transactions for a customer
- **Balance Enquiry**: Current account balance

## Security Features

- Session-based authentication
- Input validation and sanitization
- SQL injection prevention
- CORS configuration for secure API access
- Error handling and logging

## Customization

### Changing Login Credentials
Edit the `authenticate_user` method in `src/database/bank_db.py`:

```python
def authenticate_user(self, username: str, password: str) -> bool:
    return username == "your_username" and password == "your_password"
```

### Database Configuration
The application uses SQLite by default. To use a different database:
1. Modify the database connection in `src/database/bank_db.py`
2. Update the requirements.txt with appropriate database drivers
3. Adjust the SQL queries for your database system

### UI Customization
- Modify `static/index.html` to change the frontend appearance
- Update CSS classes and styles in the `<style>` section
- Customize colors, fonts, and layout as needed

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change the port in `main.py`: `app.run(port=5001)`

2. **Database Errors**
   - Delete `royal_bank.db` to reset the database
   - Check file permissions in the application directory

3. **Module Import Errors**
   - Ensure all `__init__.py` files are present
   - Check Python path configuration

4. **Frontend Not Loading**
   - Verify `static/index.html` exists
   - Check browser console for JavaScript errors

### Development Mode
The application runs in debug mode by default. For production:
1. Set `debug=False` in `main.py`
2. Use a production WSGI server like Gunicorn
3. Configure proper SSL certificates
4. Set secure session cookies

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the application logs
3. Verify all dependencies are installed correctly

## License

This project is developed for educational and demonstration purposes.

---

**Royal Bank of India Admin Portal** - A complete banking management solution.

