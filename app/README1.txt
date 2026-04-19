How to run:

1. Make sure Python 3 is installed on your device
2. Open terminal in the project root folder
3. create a virtual environment: python -m venv venv

4. Activate the virtual environment:
- Windows:
venv\Scripts\activate
- Mac/Linux:
source venv/bin/activate

5. Install dependencies in terminal:
pip install -r requirements.txt

6. If Flask is not installed, run in terminal:
pip install flask

7. Run the application in terminal:
python run.py

8. Open a browser and go to(link will also appear in the terminal in bolded color):
http://127.0.0.1:5000

What it does:
- Runs the CaloFit web application
- Automatically creates the database and default user on first startup
- Allows users to:
  - Add meals
  - Edit meals
  - Delete meals
  - View daily and weekly nutrition data

What it's used for:
- Demonstrating the full functionality of the application
- Testing meal tracking and CRUD features
- Viewing calorie and macro tracking in real time

