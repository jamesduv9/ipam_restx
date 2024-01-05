def test_register(client, headers, testcases):

    path = "/auth/register"
    for user in testcases:
        response = client.post(path, json=user, headers=headers)
        assert response.status_code == 200
        assert response.json.get("status") == "Success"

def test_login(client, headers, testcases):
    for tc in testcases:
        tc.pop("permission_level", None)
    path = "/auth/login"
    for tc in testcases:
        response = client.post(path, json=tc, headers=headers)
        assert response.status_code == 200
        assert response.json.get("status") == "Success"
        assert response.json.get("data").get("X-Ipam-Apikey")