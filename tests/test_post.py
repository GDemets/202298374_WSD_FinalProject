
class TestPosts:

    def test_get_posts(self, client):
        response = client.get("/posts")
        assert response.status_code == 200

    def test_get_posts_wrong(self, client):
        response = client.get("/posts/9999")
        assert response.status_code==404
    
    def test_create_post_not_authenticated(self, client, category,user):
        data = {
            "title": "New post",
            "content": "Lorem ipsum",
            "category_id": category,
            "user_id":user
        }

        response = client.post("/posts", json=data)
        assert response.status_code == 401
    
    def test_create_post_user(self, client, category, user, user_token):
        data = {
            "title": "New post",
            "content": "Lorem ipsum dolor sit amet",
            "category_id": category,
            "user_id": user,
        }
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post("/posts", json=data, headers=headers)
        assert response.status_code == 201
    
    def test_update_post_author(self, client, post, user_token):
        data = {
            "title": "Author update",
            "content": "Author updated content"
        }

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.put(f"/posts/{post}", json=data, headers=headers)
        assert response.status_code == 200






