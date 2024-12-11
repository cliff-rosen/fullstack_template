# Full Stack Repo Template

## Stack Overview

Frontend:
- vite / react
- tailwindcss
- shadcn

Backend:
- fastapi
- sqlalchemy
- PostgreSQL
- Alembic
- Uvicorn
- SQLModel

Database:
- mariadb

Functionalities:
- Authentication
- Authorization
- User Management
- Healthcheck


## Backend Setup

1. create virtual environment
```
cd backend
python -m venv venv
```

2. activate virtual environment
```
.\.venv\Scripts\activate
# for PowerShell
venv\Scripts\Activate.ps1
```

3. install dependencies
```
pip install -r requirements.txt
```

4. configure backend
a. create .env file (see .env.example)
b. configure database connection in .env
c. set app name and version in settings.py

5. create alembic.ini file (see alembic.ini.example)


5. run backend
```
uvicorn main:app --reload
``` 

6. Verify backend is running
a. open browser and navigate to
```
http://localhost:8000/docs
```

b. verify that healthcheck endpoint is accessible


## Frontend Setup

1. install dependencies
```
cd frontend
npm install
```

2. run frontend
```
npm run dev
```

