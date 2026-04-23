def create_user(n=1):
    match n:
        case 1:
            return {
            "first_name":"John",
            "last_name":"Doe",
            "email":"john@example.com",
            "password":"password"
        }

        case 2:
            return {
                "first_name":"Jane",
                "last_name":"Smith",
                "email":"jane@example.com",
                "password":"password"
            }