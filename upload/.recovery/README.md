# Royal Bank of India - Full Stack Banking Application

A modern, full-stack banking application built with Flask (Python) backend and React frontend, featuring PostgreSQL database integration.

## 🏗️ Architecture

```
/
├── server/                 # Flask Backend
│   ├── src/
│   │   ├── models/        # Database models
│   │   │   └── bank.py    # Banking operations
│   │   ├── routes/        # API endpoints
│   │   │   └── bank.py    # Banking routes
│   │   ├── static/        # Frontend files (served by Flask)
│   │   └── main.py        # Flask application entry point
│   ├── venv/              # Python virtual environment
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── client/                # React Frontend (development)
│   ├── public/
│   │   └── index.html    # Single-page React application
│   └── package.json      # Frontend configuration
├── package.json          # Root project configuration
├── Procfile              # Deployment configuration
├── render.yaml           # Render.com deployment config
└── README.md             # This file
```

## 🚀 Features

### Admin Portal
- **Secure Login**: Username/password authentication with session management
- **User Management**: Create new users, check existing users
- **Banking Operations**:
  - Deposit money
  - Withdraw money (with balance validation)
  - Mini statement generation
  - Balance enquiry

### Modern UI/UX
- **Responsive Design**: Works on desktop and mobile devices
- **Modern Aesthetics**: Gradient backgrounds, rounded corners, shadows
- **Interactive Elements**: Hover effects, loading states, animations
- **Toast Notifications**: Success/error feedback
- **Clean Layout**: Sidebar navigation, organized dashboard

### Technical Features
- **RESTful API**: Clean API endpoints for all banking operations
- **Session Management**: Secure user sessions with Flask
- **Database Integration**: PostgreSQL with proper transaction handling
- **Error Handling**: Comprehensive error handling and validation
- **CORS Support**: Cross-origin requests enabled
- **Production Ready**: Gunicorn WSGI server configuration

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd royal-bank-fullstack
   ```

2. **Setup Backend**
   ```bash
   cd server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   
   Update `server/.env` with your database credentials:
   ```env
   DB_NAME=royal_bank_of_india
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=your-secret-key
   FLASK_ENV=development
   ```

4. **Setup PostgreSQL Database**
   ```sql
   CREATE DATABASE royal_bank_of_india;
   ```

5. **Run the Application**
   ```bash
   # Development mode
   npm run dev
   
   # Or directly with Python
   cd server
   source venv/bin/activate
   python src/main.py
   ```

6. **Access the Application**
   - Open your browser to `http://localhost:5000`
   - Login with default credentials:
     - Username: `sk`
     - Password: `00`
     - Table Name: `bank_transactions`

## 🌐 Deployment

### Render.com Deployment

1. **Connect Repository**
   - Connect your GitHub repository to Render.com
   - Select "Web Service" deployment type

2. **Configuration**
   - **Build Command**: `cd server && pip install -r requirements.txt`
   - **Start Command**: `cd server && gunicorn -w 4 -b 0.0.0.0:$PORT src.main:app`
   - **Python Version**: `3.11.0`

3. **Environment Variables**
   Set these in Render dashboard:
   ```
   PYTHON_VERSION=3.11.0
   DB_NAME=royal_bank_of_india
   DB_USER=postgres
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=5432
   SECRET_KEY=your_production_secret_key
   FLASK_ENV=production
   ```

4. **Database Setup**
   - Create a PostgreSQL database on Render or use external provider
   - Update environment variables with production database credentials

### Alternative Deployment Options

#### Heroku
```bash
# Install Heroku CLI and login
heroku create royal-bank-app
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set PYTHON_VERSION=3.11.0
git push heroku main
```

#### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY server/requirements.txt .
RUN pip install -r requirements.txt
COPY server/ .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:app"]
```

## 📚 API Documentation

### Authentication
- `POST /api/login` - Admin login
- `POST /api/logout` - Logout
- `GET /api/session-status` - Check session status

### User Management
- `POST /api/check-user` - Check if user exists
- `POST /api/create-user` - Create new user

### Banking Operations
- `POST /api/deposit` - Process deposit
- `POST /api/withdraw` - Process withdrawal
- `POST /api/mini-statement` - Generate mini statement
- `POST /api/balance-enquiry` - Get account balance

### Example API Usage

```javascript
// Login
const response = await fetch('/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    username: 'sk',
    password: '00',
    table_name: 'bank_transactions'
  })
});

// Deposit money
const depositResponse = await fetch('/api/deposit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    aadhar_no: '123456789012',
    amount: 1000
  })
});
```

## 🗄️ Database Schema

```sql
CREATE TABLE bank_transactions (
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
```

## 🔧 Development

### Project Structure
- **Backend**: Flask application with modular structure
- **Frontend**: React components with modern UI
- **Database**: PostgreSQL with transaction history
- **Deployment**: Production-ready configuration

### Key Components

#### Backend (`server/src/`)
- `main.py`: Flask application setup and routing
- `models/bank.py`: Database operations and business logic
- `routes/bank.py`: API endpoints and request handling

#### Frontend (`client/public/`)
- `index.html`: Single-page React application with all components

### Adding New Features

1. **Backend**: Add new routes in `routes/bank.py`
2. **Database**: Extend `models/bank.py` for new operations
3. **Frontend**: Add new components in the React application
4. **Testing**: Test locally before deployment

## 🔒 Security Features

- Session-based authentication
- Input validation and sanitization
- SQL injection prevention with parameterized queries
- CORS configuration for secure cross-origin requests
- Environment variable protection for sensitive data

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Port Already in Use**
   ```bash
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9
   ```

3. **Module Import Errors**
   - Ensure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`

4. **Frontend Not Loading**
   - Check if files are in `server/src/static/`
   - Verify Flask is serving static files correctly

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**Royal Bank of India** - Modern Banking Solutions

