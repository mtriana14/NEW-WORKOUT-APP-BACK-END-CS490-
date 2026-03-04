# Fitness App - Backend API

A production-grade REST API for a fitness application built with **Python Flask**, **SQLAlchemy**, and **MySQL**. This backend handles coach management, admin operations, and push notifications.

---

## Tech Stack

- **Language:** Python 3.14
- **Framework:** Flask
- **ORM:** SQLAlchemy + Flask-Migrate
- **Database:** MySQL (XAMPP)
- **Authentication:** JWT (Flask-JWT-Extended)
- **Password Hashing:** Bcrypt

---

## Project Structure

```
fitness-app/
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   └── db.py               # Database connection
│   │   ├── controllers/
│   │   │   ├── coach_availability_controller.py
│   │   │   ├── client_request_controller.py
│   │   │   ├── exercise_controller.py
│   │   │   ├── coach_registration_controller.py
│   │   │   ├── coach_management_controller.py
│   │   │   ├── payment_dashboard_controller.py
│   │   │   └── notification_controller.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── coach.py
│   │   │   ├── coach_availability.py
│   │   │   ├── client_request.py
│   │   │   ├── exercise.py
│   │   │   ├── notification.py
│   │   │   └── payment.py
│   │   ├── routes/
│   │   │   ├── coach_availability_routes.py
│   │   │   ├── client_request_routes.py
│   │   │   ├── exercise_routes.py
│   │   │   ├── coach_registration_routes.py
│   │   │   ├── coach_management_routes.py
│   │   │   ├── payment_dashboard_routes.py
│   │   │   └── notification_routes.py
│   │   ├── seeders/
│   │   │   ├── user_seeder.py
│   │   │   ├── coach_seeder.py
│   │   │   ├── availability_seeder.py
│   │   │   ├── exercise_seeder.py
│   │   │   ├── client_request_seeder.py
│   │   │   └── run_seeders.py
│   │   └── __init__.py
│   ├── migrations/
│   ├── .env
│   ├── requirements.txt
│   └── run.py
└── frontend/                        # Next.js (handled separately)
```

---

## Getting Started

### Prerequisites

- Python 3.14+
- XAMPP with MySQL running
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fitness-app/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create the `.env` file:
```env
FLASK_ENV=development
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=fitness_app
```

5. Create the database in phpMyAdmin:
   - Open `http://localhost/phpmyadmin`
   - Create a new database named `fitness_app`
   - Set collation to `utf8mb4_unicode_ci`

6. Run migrations:
```bash
python -m flask db upgrade
```

7. Start the server:
```bash
python run.py
```

The API will be running at `http://localhost:5000`

---

## Database Models

| Model | Description |
|-------|-------------|
| `User` | Base model for all users (client, coach, admin) |
| `Coach` | Coach profile with specialization and status |
| `CoachAvailability` | Weekly schedule slots for coaches |
| `ClientRequest` | Coaching requests from clients to coaches |
| `Exercise` | Master exercise database managed by admin |
| `Notification` | Push notifications for all users |
| `Payment` | Payment transactions between clients and coaches |

---

## API Endpoints

### Coach Availability (UC 9.3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/coach/availability` | Set or update coach schedule |
| GET | `/api/coach/availability/:coach_id` | Get coach schedule |

### Client Requests (UC 9.4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/coach/:coach_id/requests` | Get pending requests for a coach |
| PUT | `/api/coach/requests/:request_id/respond` | Accept or decline a request |

### Admin - Exercise Database (UC 10.1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/exercises` | Get all exercises |
| POST | `/api/admin/exercises` | Create new exercise |
| PUT | `/api/admin/exercises/:id` | Update exercise |
| DELETE | `/api/admin/exercises/:id` | Soft delete exercise |

### Admin - Coach Registrations (UC 10.2)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/coaches` | Get all coaches |
| GET | `/api/admin/coaches/pending` | Get pending coaches |
| PUT | `/api/admin/coaches/:id/process` | Approve or reject registration |

### Admin - Coach Management (UC 10.3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/api/admin/coaches/:id/suspend` | Suspend a coach |
| PUT | `/api/admin/coaches/:id/reactivate` | Reactivate a coach |
| PUT | `/api/admin/coaches/:id/disable` | Permanently disable a coach |

### Admin - Payment Dashboard (UC 10.4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/payments/summary` | Get overall payment summary |
| GET | `/api/admin/payments` | Get all payments (paginated) |
| GET | `/api/admin/payments/coach/:id` | Get payment summary by coach |

### Notifications (UC 11.1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/user/:id` | Get all user notifications |
| GET | `/api/notifications/user/:id/unread` | Get unread notifications |
| PUT | `/api/notifications/:id/read` | Mark one as read |
| PUT | `/api/notifications/user/:id/read-all` | Mark all as read |
| POST | `/api/notifications` | Send a notification |
| DELETE | `/api/notifications/:id` | Delete a notification |

---

## Seeder Data

The following test accounts are seeded automatically on first run:

| Name | Email | Password | Role |
|------|-------|----------|------|
| Admin User | admin@fitnessapp.com | password123 | admin |
| John Smith | john.coach@fitnessapp.com | password123 | coach |
| Sarah Johnson | sarah.coach@fitnessapp.com | password123 | coach |
| Mike Davis | mike.client@fitnessapp.com | password123 | client |
| Emily Brown | emily.client@fitnessapp.com | password123 | client |

---

## Testing

Import the provided Postman collection `FitnessApp.postman_collection.json` to test all endpoints. The collection includes pre-configured requests for every endpoint with sample request bodies.

---

## Team

| Name | Role | Features |
|------|------|----------|
| Kevin | Backend | UC 1.x - Account & Profile |
| Gaby | Backend | UC 2.x - Coach & Payments |
| Nick | Backend | UC 3.x - Workout Planning |
| Justin | Backend | UC 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 11.1 |
| Michael | Frontend | Next.js |

---

## License

This project was built as part of CS490 - Software Engineering at university level.