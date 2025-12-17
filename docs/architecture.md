# API Endpoints Reference

---

## Health & Documentation

| Method | Endpoint    | Description            | Auth   |
| ------ | ----------- | ---------------------- | ------ |
| GET    | `/health`   | Health check           | Public |
| GET    | `/`         | Redirect to Swagger UI | Public |
| GET    | `/apidocs/` | Swagger documentation  | Public |

---

## Authentication

| Method | Endpoint                 | Description                 | Auth   |
| ------ | ------------------------ | --------------------------- | ------ |
| POST   | `/login`                 | User login (email/password) | Public |
| POST   | `/refresh`               | Refresh access token        | JWT    |
| GET    | `/login/google`          | Redirect to Google OAuth    | Public |
| GET    | `/login/google/callback` | Google OAuth callback       | Public |

---

## Users

| Method | Endpoint                      | Description              | Auth   |
| ------ | ----------------------------- | ------------------------ | ------ |
| GET    | `/users`                      | Get all users            | Public |
| GET    | `/users/me`                   | Get current user profile | JWT    |
| POST   | `/users`                      | Create a new user        | Public |
| PUT    | `/users/me`                   | Update current user      | JWT    |
| PATCH  | `/users/{user_id}/make_admin` | Promote user to admin    | Admin  |
| DELETE | `/users/me`                   | Delete current user      | JWT    |

---

## Posts

| Method | Endpoint                          | Description                  | Auth        |
| ------ | --------------------------------- | ---------------------------- | ----------- |
| GET    | `/posts`                          | Get paginated posts (cached) | Public      |
| GET    | `/posts/{post_id}`                | Get post by ID               | Public      |
| GET    | `/posts/category?category={name}` | Get posts by category name   | Public      |
| GET    | `/posts/search`                   | Search posts with filters    | Public      |
| POST   | `/posts`                          | Create a post                | JWT         |
| PUT    | `/posts/{post_id}`                | Update a post                | Owner       |
| DELETE | `/posts/{post_id}`                | Delete a post                | Owner/Admin |

---

## Categories

| Method | Endpoint                    | Description        | Auth   |
| ------ | --------------------------- | ------------------ | ------ |
| GET    | `/categories`               | Get all categories | Public |
| GET    | `/categories/{cat_id}`      | Get category by ID | Public |
| POST   | `/categories`               | Create a category  | Admin  |
| PATCH  | `/categories/{category_id}` | Update category    | Admin  |
| DELETE | `/categories/{category_id}` | Delete category    | Admin  |

---

## Comments

| Method | Endpoint                    | Description                 | Auth        |
| ------ | --------------------------- | --------------------------- | ----------- |
| GET    | `/comments/me`              | Get current user's comments | JWT         |
| GET    | `/posts/{post_id}/comments` | Get comments for a post     | Public      |
| POST   | `/posts/{post_id}/comments` | Add comment to a post       | JWT         |
| PUT    | `/comments/{comment_id}`    | Update a comment            | Owner       |
| DELETE | `/comments/{comment_id}`    | Delete a comment            | Owner/Admin |

---

## Favorites

| Method | Endpoint                           | Description                    | Auth  |
| ------ | ---------------------------------- | ------------------------------ | ----- |
| GET    | `/favorites/me`                    | Get current user's favorites   | JWT   |
| GET    | `/favorites/posts/{post_id}/users` | Get users who favorited a post | Admin |
| POST   | `/favorites/{post_id}`             | Add post to favorites          | JWT   |
| DELETE | `/favorites/{post_id}`             | Remove post from favorites     | JWT   |

---

## Notes

* All protected endpoints require an `Authorization: Bearer <token>` header.
* Pagination parameters: `page`, `limit`.
* Cached endpoint: `GET /posts` (Flask-Caching, 60s).

