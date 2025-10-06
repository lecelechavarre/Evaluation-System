# Performance Evaluation System v1.0.0

A comprehensive employee performance evaluation system with role-based access control.

## Quick Start

1. **Install Dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Initialize System**
   ```bash
   cp .env.example .env
   python scripts/init_admin.py
   ```

3. **Run Application**
   ```bash
   # Web application
   python src/web_app.py
   
   # Desktop application
   python src/desktop_app.py
   ```

## Features

- ✅ Secure authentication with bcrypt
- ✅ Role-based access (Admin, Evaluator, Employee)
- ✅ JSON-based storage with file locking
- ✅ Excel report exports
- ✅ Web interface (Flask)
- ✅ Desktop app (Tkinter)
- ✅ Comprehensive test suite
- ✅ Docker support

## Documentation

See DEPLOYMENT_GUIDE.md for complete deployment instructions.

## Default Admin Credentials

- Username: `admin`
- Password: `Admin@123`

**⚠️ Change immediately after first login!**

## License

MIT License
