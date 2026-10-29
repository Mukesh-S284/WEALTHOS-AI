"""Security tests: multi-tenant isolation, cross-user data leakage, and deletion safety."""

def test_cross_user_profile_isolation(client, auth_headers, second_auth_headers):
    # User 1 profile
    resp1 = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp1.status_code == 200
    user1_data = resp1.json()

    # User 2 profile
    resp2 = client.get("/api/v1/auth/me", headers=second_auth_headers)
    assert resp2.status_code == 200
    user2_data = resp2.json()

    # Must be distinct user IDs and emails
    assert user1_data["id"] != user2_data["id"]
    assert user1_data["email"] != user2_data["email"]


def test_user_data_export_isolation(client, auth_headers, second_auth_headers):
    resp1 = client.get("/api/v1/users/export-data", headers=auth_headers)
    assert resp1.status_code == 200
    export1 = resp1.json()

    resp2 = client.get("/api/v1/users/export-data", headers=second_auth_headers)
    assert resp2.status_code == 200
    export2 = resp2.json()

    assert export1["user_id"] != export2["user_id"]
    assert export1["user_profile"]["email"] == "testuser@wealthos.ai"
    assert export2["user_profile"]["email"] == "seconduser@wealthos.ai"


def test_delete_account_requires_explicit_confirmation(client, auth_headers):
    # Attempt deletion with incorrect confirmation
    bad_resp = client.delete("/api/v1/users/account?confirmation=WRONG", headers=auth_headers)
    assert bad_resp.status_code == 400

    # Successful deletion
    good_resp = client.delete("/api/v1/users/account?confirmation=DELETE_MY_ACCOUNT", headers=auth_headers)
    assert good_resp.status_code == 200

    # User token must now fail authentication
    follow_up = client.get("/api/v1/auth/me", headers=auth_headers)
    assert follow_up.status_code == 401
