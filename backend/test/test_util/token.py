def get_bearer_token_header(client, user):
    response = client.post("/token", data={'username': user.email, 'password': 'asdf'})
    token = response.json()["access_token"]
    return {"Authorization": "Bearer " + token}
