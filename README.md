# 202298374 wSD Term Project

# Blog API
This project is a RESTful API built with Flask for managing users, posts, comments, categories, and favorites.

Key Components

- Flask Application
- REST endpoints defined using Flask routes
- Swagger documentation via Flasgger
- Authentication & Security 
- JWT managed by flask-jwt-extended 
- Access token expiration: 15 minutes
- Role-based access using JWT claims (Admin/user)
- ORM: SQLAlchemy
- Sensitive values stored in .env
- Custom error responses via error_response

## Data Models Overview

* **User**: pseudo, email, password (hashed), role
* **Post**: author, title, category, linked comments
* **Category**: name, linked posts
* **Comment**: post id, user id, content
* **Favoritte**: user id, post id
---

## Tech Stack
- Python 3
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-Caching
- Swagger (Flasgger)
- Google auth
- Docker

## Installation

```bash
pip install -r requirements.txt
```
## Run the Application

```bash
python seed.py
python app.py
```

## Run tests 
```bash
pytest -v
```

### Swagger Documentation

Swagger UI is available in localhost at:

```
http://127.0.0.1:3000/apidocs
```

Swagger UI is available with Jcloud and Docker at:
```
http://113.198.66.75:13216/apidocs//apidocs
```

---