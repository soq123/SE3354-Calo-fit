from app import create_app

print("Before app creation")
app = create_app()
print("After app creation")

if __name__ == "__main__":
    print("About to run server")
    app.run(debug=True, host="127.0.0.1", port=5000)