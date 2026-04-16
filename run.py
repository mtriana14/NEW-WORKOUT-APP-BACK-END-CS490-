from app import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            from app.seeders.run_seeders import run_all_seeders
            run_all_seeders()
        except Exception as e:
            print(f"Seeder skipped: {e}")
    app.run(debug=False, port=5000)
