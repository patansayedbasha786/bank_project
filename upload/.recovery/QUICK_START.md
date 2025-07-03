# 🚀 Quick Start Guide - Royal Bank of India

Get your banking application running in minutes!

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL database (local or cloud)
- Git (optional)

## ⚡ Quick Setup (5 minutes)

### 1. Extract & Navigate
```bash
# Extract the application
tar -xzf royal-bank-fullstack.tar.gz
cd royal-bank-fullstack

# Or clone from repository
git clone <your-repo-url>
cd royal-bank-fullstack
```

### 2. Setup Backend
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Database
Edit `server/.env`:
```env
DB_NAME=royal_bank_of_india
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
```

### 4. Run Application
```bash
# From project root
./run.sh

# Or manually
cd server
source venv/bin/activate
python src/main.py
```

### 5. Access Application
- Open: http://localhost:5000
- Login: username=`sk`, password=`00`
- Table: `bank_transactions`

## 🌐 Deploy to Production

### Render.com (Recommended)
1. Push to GitHub
2. Connect to Render
3. Set environment variables
4. Deploy!

**Build Command**: `cd server && pip install -r requirements.txt`
**Start Command**: `cd server && gunicorn -w 4 -b 0.0.0.0:$PORT src.main:app`

### Environment Variables for Production:
```
PYTHON_VERSION=3.11.0
DB_NAME=royal_bank_of_india
DB_USER=postgres
DB_PASSWORD=your_production_password
DB_HOST=your_production_host
DB_PORT=5432
SECRET_KEY=your_production_secret
FLASK_ENV=production
```

## 🔧 Features

✅ **Admin Login** - Secure authentication  
✅ **User Management** - Create and check users  
✅ **Deposits** - Process money deposits  
✅ **Withdrawals** - Handle withdrawals with validation  
✅ **Mini Statements** - Generate transaction history  
✅ **Balance Enquiry** - Check account balances  
✅ **Modern UI** - Responsive design with animations  
✅ **Production Ready** - Deployment configurations included  

## 📱 Default Credentials

- **Username**: `sk`
- **Password**: `00`
- **Table Name**: `bank_transactions`

## 🆘 Need Help?

1. Check `README.md` for detailed documentation
2. See `DEPLOYMENT.md` for deployment guides
3. Review error logs in terminal
4. Ensure PostgreSQL is running

## 📞 Support

- 📧 Create an issue in the repository
- 📖 Read the full documentation
- 🔍 Check troubleshooting section

---
**Royal Bank of India** - Modern Banking Solutions 🏦

