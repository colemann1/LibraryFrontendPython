## Lab 5 - Library Manager

### Required Dependencies
os

pandas

datetime

flask

### How this works
1. Run 'frontend.py' from a terminal - 'python frontend.py'
2. Webapp will run on https://localhost:5000


### Additions from base project
- Added headers to Books.csv, Users.csv.
- Added Checkouts.csv for maintaining record of checked-out books that persist after restarting server.

---

## Lab 6 - Unit Tests
From the main project directory ('Lab 6 - NC'), run the following command:

`python -m unittest discover -s tests`