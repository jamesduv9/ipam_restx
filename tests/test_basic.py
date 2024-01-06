def test_health(client):
    """
    Ensures the /health_check route is working
    """
    response = client.get("/health_check")
    assert response.text == "Healthy!"