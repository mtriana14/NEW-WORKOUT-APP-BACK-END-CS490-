# This is a helper file to make the test code shorter and easier to read

def create_user(n=1, role='client'):
    match n:
        case 1:
            return {
            "first_name":"John",
            "last_name":"Doe",
            "email":"john@example.com",
            "password":"password",
            "role":f"{role}"
        }

        case 2:
            return {
                "first_name":"Jane",
                "last_name":"Smith",
                "email":"jane@example.com",
                "password":"password",
                "role":f"{role}"
            }
        
def register_and_login(client, n, role='client'):
    resp = client.post('/api/auth/register', json=create_user(n, role))
    assert resp.status_code == 201

    resp = client.post('/api/auth/login', json={
        "email": create_user(n)['email'],
        "password": "password"
    })
    assert resp.status_code == 200

    return resp.json['token']