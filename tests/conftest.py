import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as flask_app, db
from models import User, Post, Category, Comment, Favorite
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 
        'JWT_SECRET_KEY': 'test-secret-key',
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create Flask client for test"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Run cli runner"""
    return app.test_cli_runner()

@pytest.fixture
def user(app):
    user = User(
        pseudo="testuser",
        mail="test@example.com",
        role="user"
    )
    user.set_password("1234")
    db.session.add(user)
    db.session.commit()
    return user.id

@pytest.fixture
def user_token(app,user):
    return create_access_token(
        identity=str(user),
        additional_claims={"role": "user"}
    )

@pytest.fixture
def admin(app):
    admin = User(
        pseudo="admin",
        mail="admin@example.com",
        role="admin"
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    return admin.id

@pytest.fixture
def admin_token(app,admin):
    return create_access_token(
        identity=str(admin),
        additional_claims={"role": "admin"}
    )

@pytest.fixture
def category(app):
    category = Category(name="Fiction")
    db.session.add(category)
    db.session.commit()
    return category.id

@pytest.fixture
def post(app, user, category):
    post = Post(
        title="Test post",
        content="Test content",
        user_id=user,          
        category_id=category
    )
    db.session.add(post)
    db.session.commit()
    return post.id


@pytest.fixture
def comment(app, user, post):
    comment = Comment(
        content="Super post !",
        user_id=user,
        post_id=post
    )
    db.session.add(comment)
    db.session.commit()
    return comment.id

@pytest.fixture
def favorite(app, user, post):
    fav = Favorite(
        user_id=user,
        post_id=post
    )
    db.session.add(fav)
    db.session.commit()
    return fav.id

