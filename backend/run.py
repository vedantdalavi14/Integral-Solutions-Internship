from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Flask API server...")
    print("📍 Running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
