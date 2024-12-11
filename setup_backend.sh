# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # for Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database (only needed once)
python init_db.py