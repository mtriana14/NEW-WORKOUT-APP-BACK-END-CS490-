"""
Seeder script to populate the database with sample data.
Run with: python -m app.seeders.seed_all
"""

from app.config.db import db
from app.models.user import User
from app.models.coach import Coach
from app.models.client_request import ClientRequest
from app.models.coach_availability import CoachAvailability
from app.models.WorkoutPlan import WorkoutPlan
from app.models.MealPlan import MealPlan
from app.models.exercise import Exercise
from app.models.notification import Notification
from app.models.payment import Payment
import bcrypt

from datetime import datetime, time, timedelta
import random


def seed_all():
    """Seed all tables with sample data."""
    
    print("🌱 Starting database seeding...")
    
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))
    db.session.execute(db.text("TRUNCATE TABLE Notifications"))
    db.session.execute(db.text("TRUNCATE TABLE Payments"))
    db.session.execute(db.text("TRUNCATE TABLE mealplans"))
    db.session.execute(db.text("TRUNCATE TABLE workoutplans"))
    db.session.execute(db.text("TRUNCATE TABLE ClientRequests"))
    db.session.execute(db.text("TRUNCATE TABLE CoachAvailability"))
    db.session.execute(db.text("TRUNCATE TABLE Exercises"))
    db.session.execute(db.text("TRUNCATE TABLE Coaches"))
    db.session.execute(db.text("TRUNCATE TABLE Users"))
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
    db.session.commit() 
    
    users = []
    
    # Admin user
    admin = User(
        first_name="Admin",
        last_name="User",
        email="admin@herahealth.com",
        password= bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        role="admin"
    )
    users.append(admin)
    
    # Coach users (10)
    coach_data = [
        ("Mike", "Johnson", "Strength Training"),
        ("Sarah", "Williams", "Weight Loss"),
        ("Carlos", "Rodriguez", "HIIT & Cardio"),
        ("Emma", "Davis", "Yoga & Flexibility"),
        ("James", "Brown", "Bodybuilding"),
        ("Lisa", "Martinez", "Nutrition & Wellness"),
        ("David", "Wilson", "Sports Performance"),
        ("Anna", "Taylor", "Pilates"),
        ("Chris", "Anderson", "CrossFit"),
        ("Maria", "Garcia", "Prenatal Fitness"),
    ]
    
    coach_users = []
    for i, (first, last, spec) in enumerate(coach_data):
        user = User(
            first_name=first,
            last_name=last,
            email=f"{first.lower()}.coach@herahealth.com",
            password= bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role="coach"
        )
        coach_users.append((user, spec))
        users.append(user)
    
    # Client users (10)
    client_data = [
        ("Emily", "Clark"),
        ("Michael", "Lee"),
        ("Jessica", "White"),
        ("Daniel", "Harris"),
        ("Olivia", "Martin"),
        ("Matthew", "Thompson"),
        ("Sophia", "Moore"),
        ("Andrew", "Jackson"),
        ("Isabella", "Lewis"),
        ("Ryan", "Walker"),
    ]
    
    client_users = []
    for first, last in client_data:
        user = User(
            first_name=first,
            last_name=last,
            email=f"{first.lower()}.{last.lower()}@email.com",
            password= bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            role="client"
        )
        client_users.append(user)
        users.append(user)
    
    db.session.add_all(users)
    db.session.commit()
    print(f"   ✅ Created {len(users)} users")
    
    # ==================== COACHES ====================
    print("🏋️ Creating coaches...")
    
    
    
    coaches = []
    bios = [
        "Certified personal trainer with 8+ years of experience helping clients achieve their fitness goals.",
        "Passionate about helping people transform their lives through sustainable fitness habits.",
        "Former competitive athlete turned coach, specializing in high-intensity training programs.",
        "Holistic approach to fitness, combining physical training with mindfulness practices.",
        "Expert in muscle building and body composition with a science-based approach.",
        "Registered dietitian and fitness coach focused on the nutrition-exercise connection.",
        "Sports scientist dedicated to optimizing athletic performance at all levels.",
        "Certified Pilates instructor with expertise in core strength and rehabilitation.",
        "CrossFit Level 3 trainer with experience coaching competitive athletes.",
        "Specialized in pre and postnatal fitness with certifications in women's health.",
    ]
    
    specializations = ['fitness', 'nutrition', 'both']
    
    for i, (user, spec) in enumerate(coach_users):
        coach = Coach(
            user_id=user.user_id,
            specialization=random.choice(specializations),
            experience_years=random.randint(3, 15),
            bio=bios[i],
            gym=f"FitLife Gym {i+1}" if i % 2 == 0 else None,
            cost=random.randint(50, 150),
            hourly_rate=random.randint(40, 120),
            certifications="ACE, NASM, CPR/AED" if i % 2 == 0 else "ISSA, NSCA, First Aid",
            status="approved"
        )
        coaches.append(coach)
    
    db.session.add_all(coaches)
    db.session.commit()
    print(f"   ✅ Created {len(coaches)} coaches")
    
    # ==================== COACH AVAILABILITY ====================
    print("📅 Creating coach availability...")
    
    availabilities = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for coach in coaches:
        # Each coach available 4-6 days per week
        available_days = random.sample(days, random.randint(4, 6))
        for day in available_days:
            start_hour = random.choice([7, 8, 9])
            end_hour = random.choice([17, 18, 19, 20])
            
            avail = CoachAvailability(
                coach_id=coach.coach_id,
                day_of_week=day,
                start_time=time(start_hour, 0),
                end_time=time(end_hour, 0),
                is_available=True
            )
            availabilities.append(avail)
    
    db.session.add_all(availabilities)
    db.session.commit()
    print(f"   ✅ Created {len(availabilities)} availability slots")
    
    # ==================== CLIENT REQUESTS ====================
    print("📨 Creating client requests...")
    
    requests = []
    messages = [
        "Hi! I'm looking to get in shape and would love your guidance.",
        "I've heard great things about your training style. Would love to work with you!",
        "I need help with my fitness goals. Can you help me?",
        "Looking for a coach to help me lose weight and build strength.",
        "I'm new to fitness and need someone to guide me through the basics.",
        "Interested in your training program. When can we start?",
        "I want to improve my overall health and fitness level.",
        "Can you help me prepare for a marathon?",
        "Looking for personalized workout and nutrition plans.",
        "I need accountability and motivation to reach my goals.",
    ]
    
    statuses = ["pending", "accepted", "declined"]
    
    for i, client in enumerate(client_users):
        # Each client sends 1-2 requests
        num_requests = random.randint(1, 2)
        selected_coaches = random.sample(coaches, num_requests)
        
        for j, coach in enumerate(selected_coaches):
            status = "accepted" if j == 0 else random.choice(statuses)
            
            req = ClientRequest(
                client_id=client.user_id,
                coach_id=coach.coach_id,
                message=random.choice(messages),
                status=status,
                responded_at=datetime.utcnow() if status != "pending" else None
            )
            requests.append(req)
    
    db.session.add_all(requests)
    db.session.commit()
    print(f"   ✅ Created {len(requests)} client requests")
    
    # ==================== EXERCISES ====================
   # ==================== EXERCISES ====================
    print("💪 Creating exercises...")
    
    exercise_data = [
        ("Push-ups", "Classic bodyweight exercise for chest, shoulders, and triceps", "chest", "bodyweight", "beginner"),
        ("Bench Press", "Barbell exercise for building chest strength", "chest", "barbell", "intermediate"),
        ("Pull-ups", "Upper body pulling exercise for back and biceps", "back", "bodyweight", "intermediate"),
        ("Deadlift", "Compound exercise for posterior chain development", "back", "barbell", "advanced"),
        ("Squats", "Fundamental lower body exercise for quads and glutes", "legs", "bodyweight", "beginner"),
        ("Barbell Squat", "Heavy compound movement for leg strength", "legs", "barbell", "intermediate"),
        ("Lunges", "Unilateral leg exercise for balance and strength", "legs", "dumbbell", "beginner"),
        ("Plank", "Isometric core exercise for stability", "core", "bodyweight", "beginner"),
        ("Russian Twists", "Rotational core exercise for obliques", "core", "bodyweight", "intermediate"),
        ("Shoulder Press", "Overhead pressing movement for deltoids", "shoulders", "dumbbell", "intermediate"),
        ("Lateral Raises", "Isolation exercise for side deltoids", "shoulders", "dumbbell", "beginner"),
        ("Bicep Curls", "Isolation exercise for biceps", "arms", "dumbbell", "beginner"),
        ("Tricep Dips", "Bodyweight exercise for triceps", "arms", "bodyweight", "intermediate"),
        ("Leg Press", "Machine-based quad and glute exercise", "legs", "machine", "beginner"),
        ("Calf Raises", "Isolation exercise for calves", "legs", "machine", "beginner"),
        ("Face Pulls", "Rear delt and upper back exercise", "shoulders", "cables", "intermediate"),
        ("Hip Thrusts", "Glute-focused exercise", "glutes", "barbell", "intermediate"),
        ("Mountain Climbers", "Dynamic core and cardio exercise", "core", "bodyweight", "beginner"),
        ("Burpees", "Full-body cardio exercise", "full_body", "bodyweight", "intermediate"),
        ("Kettlebell Swings", "Explosive hip hinge movement", "full_body", "other", "intermediate"),
    ]
    
    exercises = []
    for name, desc, muscle, equip, diff in exercise_data:
        ex = Exercise(
            name=name,
            description=desc,
            muscle_group=muscle,
            equipment_type=equip,
            difficulty=diff,
            is_active=True
        )
        exercises.append(ex)
    
    db.session.add_all(exercises)
    db.session.commit()
    print(f"   ✅ Created {len(exercises)} exercises")
    
    # ==================== WORKOUT PLANS ====================
    print("🏃 Creating workout plans...")
    
    workout_plans = []
    workout_names = [
        "Beginner Full Body Program",
        "Strength Building Basics",
        "Weight Loss Kickstart",
        "Muscle Gain Blueprint",
        "Core Strength Focus",
        "Upper Body Power",
        "Lower Body Sculpt",
        "HIIT Fat Burner",
        "Flexibility & Mobility",
        "Athletic Performance",
    ]
    
    workout_descs = [
        "A comprehensive program designed for beginners to build foundational strength.",
        "Progressive overload program focused on building raw strength.",
        "Combination of cardio and strength training for maximum calorie burn.",
        "Hypertrophy-focused program for muscle growth.",
        "Dedicated core training for stability and strength.",
        "Chest, back, and arms focused training split.",
        "Quads, hamstrings, and glutes emphasis.",
        "High-intensity interval training for conditioning.",
        "Stretching and mobility work for recovery.",
        "Sport-specific training for competitive athletes.",
    ]
    
    # Create plans for accepted client-coach relationships
    accepted_requests = [r for r in requests if r.status == "accepted"]
    
    for i, req in enumerate(accepted_requests):
        # 1-2 workout plans per client
        num_plans = random.randint(1, 2)
        for j in range(num_plans):
            idx = (i + j) % len(workout_names)
            plan = WorkoutPlan(
                user_id=req.client_id,
                coach_id=req.coach_id,
                name=workout_names[idx],
                description=workout_descs[idx],
                status=random.choice(["active", "active", "completed"])
            )
            workout_plans.append(plan)
    
    db.session.add_all(workout_plans)
    db.session.commit()
    print(f"   ✅ Created {len(workout_plans)} workout plans")
    
    # ==================== MEAL PLANS ====================
    print("🥗 Creating meal plans...")
    
    meal_plans = []
    meal_names = [
        "Clean Eating Basics",
        "High Protein Diet",
        "Weight Loss Nutrition",
        "Muscle Building Meals",
        "Balanced Macro Plan",
        "Low Carb Lifestyle",
        "Mediterranean Diet",
        "Vegan Power Plan",
        "Intermittent Fasting Guide",
        "Performance Nutrition",
    ]
    
    meal_descs = [
        "Focus on whole foods and eliminating processed items.",
        "High protein intake for muscle recovery and growth.",
        "Calorie-controlled plan for sustainable fat loss.",
        "Surplus calories with optimal macro ratios for gains.",
        "Balanced approach to proteins, carbs, and fats.",
        "Reduced carbohydrate intake for metabolic benefits.",
        "Heart-healthy eating based on Mediterranean principles.",
        "Plant-based nutrition for optimal health.",
        "Time-restricted eating for metabolic flexibility.",
        "Nutrition optimized for athletic performance.",
    ]
    
    for i, req in enumerate(accepted_requests):
        idx = i % len(meal_names)
        plan = MealPlan(
            user_id=req.client_id,
            coach_id=req.coach_id,
            name=meal_names[idx],
            description=meal_descs[idx],
            status=random.choice(["active", "active", "completed"])
        )
        meal_plans.append(plan)
    
    db.session.add_all(meal_plans)
    db.session.commit()
    print(f"   ✅ Created {len(meal_plans)} meal plans")
    
    # ==================== NOTIFICATIONS ====================
    print("🔔 Creating notifications...")
    
    notifications = []
    notif_types = [
        ("Welcome to HeraHealth!", "Your account has been created successfully.", "welcome"),
        ("New Message", "You have a new message from your coach.", "message"),
        ("Workout Reminder", "Don't forget your workout today!", "reminder"),
        ("Goal Achieved!", "Congratulations on reaching your weekly goal.", "achievement"),
        ("Plan Updated", "Your coach has updated your workout plan.", "plan_update"),
    ]
    
    for user in client_users + [u for u, _ in coach_users]:
        # 2-4 notifications per user
        num_notifs = random.randint(2, 4)
        for _ in range(num_notifs):
            title, msg, ntype = random.choice(notif_types)
            notif = Notification(
                user_id=user.user_id,
                title=title,
                message=msg,
                type=ntype,
                is_read=random.choice([True, False])
            )
            notifications.append(notif)
    
    db.session.add_all(notifications)
    db.session.commit()
    print(f"   ✅ Created {len(notifications)} notifications")
    
    
    
    # ==================== SUMMARY ====================
    print("\n" + "="*50)
    print("🎉 Database seeding complete!")
    print("="*50)
    print(f"""
📊 Summary:
   • Users: {len(users)} (1 admin, {len(coach_users)} coaches, {len(client_users)} clients)
   • Coaches: {len(coaches)}
   • Availability Slots: {len(availabilities)}
   • Client Requests: {len(requests)}
   • Exercises: {len(exercises)}
   • Workout Plans: {len(workout_plans)}
   • Meal Plans: {len(meal_plans)}
   • Notifications: {len(notifications)}
    

🔑 Login Credentials:
   Admin:  admin@herahealth.com / admin123
   Coach:  mike.coach@herahealth.com / coach123
   Client: emily.clark@email.com / client123
    """)


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_all()