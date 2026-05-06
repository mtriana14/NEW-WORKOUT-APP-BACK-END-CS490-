# This is a helper file to make the test code shorter and easier to read

def create_user(n=1, role='client'):
    match n:
        case 1:
            return {
            "first_name":"John",
            "last_name":"Doe",
            "email":"john@example.com",
            "password":"password",
            "username":"apple",
            "role":f"{role}"
        }

        case 2:
            return {
                "first_name":"Jane",
                "last_name":"Smith",
                "email":"jane@example.com",
                "password":"password",
                "username":"sauce",
                "role":f"{role}"
            }
        
def create_mealplan_food_item(n=1):
    match n:
        case 1:
            return {
                "meal_plan_id": 1,
                "day_of_week": "Monday",
                "meal_type": "breakfast",
                "food_name": "Overnight Oats with Berries",
                "calories": 350,
                "protein": 12.50,
                "carbs": 55.00,
                "fat": 8.00,
                "portion_size": "1 bowl",
                "notes": "Top with flaxseeds for extra Omega-3",
                "sort_order": 1
            }
        case 2:
            return {
                "meal_plan_id": 2,
                "day_of_week": "Tuesday",
                "meal_type": "lunch",
                "food_name": "Grilled Salmon and Avocado Salad",
                "calories": 550,
                "protein": 35.00,
                "carbs": 10.00,
                "fat": 42.00,
                "portion_size": "250g",
                "notes": "Use olive oil dressing only",
                "sort_order": 2
            }
        
def register_and_login(client, n, role='client'):
    resp = client.post('/api/auth/register', json=create_user(n, role))
    print(resp.status_code, resp.get_json())
    assert resp.status_code == 201

    resp = client.post('/api/auth/login', json={
        "email": create_user(n)['email'],
        "password": "password"
    })
    assert resp.status_code == 200

    return resp.json['token']