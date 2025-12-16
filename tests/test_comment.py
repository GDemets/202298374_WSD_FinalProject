class TestComments:

    def test_get_comments_by_post(self, client, post):
        response = client.get(f"/posts/{post}/comments")
        assert response.status_code == 200

    def test_get_comments_post_not_found(self, client):
        response = client.get("/posts/9999/comments")
        assert response.status_code == 404

    def test_create_comment_not_authenticated(self, client, post):
        data = {
            "content": "Nice post!"
        }

        response = client.post(f"/posts/{post}/comments", json=data)
        assert response.status_code == 401

    def test_create_comment_user(self, client, post, user_token):
        data = {
            "content": "Very interesting post"
        }

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(
            f"/posts/{post}/comments",
            json=data,
            headers=headers
        )

        assert response.status_code == 201
        assert response.json["data"]["content"] == "Very interesting post"

    def test_update_comment_author(self, client, comment, user_token):
        data = {"content": "Updated comment"}
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.put(
            f"/comments/{comment}",
            json=data,
            headers=headers
        )
        assert response.status_code == 200

    def test_update_comment_not_author(self, client, comment, admin_token):
        data = {
            "content": "Admin update attempt"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.put(
            f"/comments/{comment}",
            json=data,
            headers=headers
        )
        assert response.status_code == 403

    def test_delete_comment_author(self, client, comment, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.delete(
            f"/comments/{comment}",
            headers=headers
        )
        assert response.status_code == 200

    def test_delete_comment_admin(self, client, comment, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(
            f"/comments/{comment}",
            headers=headers
        )
        assert response.status_code == 200
