
1. Make sure Python 3 is installed on your device
2. Open terminal in the project root folder
3. Run: python basic_function_testing/test_calofit.py
4. It creates a temporary test database, runs all the tests, then deletes the test database when its done


What it tests:


- Daily calorie totals add up correctly
- That the remaining calories vs the users goal calories is accurate
- Weekly summary shows the right calorie total for each day
- Weekly calorie average across multiple days is correct
- Number of meals logged per day is correct
- Adding a new meal actually updates the daily total calories
- Deleting a meal brings the total calories back down
- A day with no meals logged returns zero instead of an error


What to expect:


- 16 total tests
- All of them should say PASS
- At the end it prints how many passed and how many failed, should be: 16 passed, 0 failed, 16 total