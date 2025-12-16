from app import app
from models import db, User, Post, Comment, Category, Favorite
from faker import Faker
import random

fake = Faker("en_US")

with app.app_context():
    db.drop_all()
    db.create_all()

    users = []
    # User alice
    u1 = User(
        pseudo="Alice",
        mail="alice@mail.com",
        role="user"
    )
    u1.set_password("1234")
    users.append(u1)

    

    for _ in range(30):
        user = User(
            pseudo=fake.user_name(),
            mail=fake.unique.email(),
            role="user"
        )
        user.set_password("1234")
        users.append(user)

    # Admin
    admin = User(
        pseudo="admin",
        mail="admin@mail.com",
        role="admin"
    )
    admin.set_password("admin")

    db.session.add_all(users + [admin])
    db.session.commit()

    category_names = [
        "Technology", "Lifestyle", "Travel", "Food",
        "Health", "Education", "Science", "Entertainment"
    ]
    categories = [Category(name=name) for name in category_names]
    db.session.add_all(categories)
    db.session.commit()

    posts = []

    post1 = Post(
        title=fake.sentence(nb_words=6),
        content=fake.text(max_nb_chars=500),
        user_id=u1.id,
        category_id=random.choice(categories).id
    )
    posts.append(post1)
    for _ in range(100):
        post = Post(
            title=fake.sentence(nb_words=6),
            content=fake.text(max_nb_chars=500),
            user_id=random.choice(users + [admin]).id,
            category_id=random.choice(categories).id
        )
        posts.append(post)

    db.session.add_all(posts)
    db.session.commit()
    comments = []
    for _ in range(200):
        comment = Comment(
            content=fake.sentence(),
            user_id=random.choice(users + [admin]).id,
            post_id=random.choice(posts).id
        )
        comments.append(comment)

    db.session.add_all(comments)
    db.session.commit()

    favorites = []
    for user in users:
        favorite_posts = random.sample(
            posts,
            k=random.randint(0, 10)
        )
        for post in favorite_posts:
            favorites.append(
                Favorite(
                    user_id=user.id,
                    post_id=post.id
                )
            )

    db.session.add_all(favorites)
    db.session.commit()

    print("Database seeded successfully!")
