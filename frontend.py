import os
import pandas as pd
from datetime import datetime
from flask import Flask, flash, render_template, redirect, request, url_for


# Define flask application variables
# Website will run on following URL and port
HOST_NAME = "localhost"
HOST_PORT = 5000

app = Flask(__name__)

BOOK_FILE_PATH = app.config.get('BOOK_FILE_PATH', 'Data/Books.csv')
USER_FILE_PATH = app.config.get('USER_FILE_PATH', 'Data/Users.csv')
CHECKOUT_FILE_PATH = app.config.get('CHECKOUT_FILE_PATH', 'Data/Checkouts.csv')

# Random secret key for flash messages
# This key can safely be changed with 'secrets' package - current is for dev purposes only
app.secret_key='a31592993900b64f97b2120b9b20fdc5'

@app.route('/', methods=['GET'])
def index_page():
    return render_template('landing.html')

@app.route('/about')
def about_page():
    return redirect("https://youtu.be/HtTUsOKjWyQ") # The funny video

# Endpoints for book functions

@app.route('/all_books')
def allbooks():

    # Load books and checkouts data
    try:
        book_df = pd.read_csv(BOOK_FILE_PATH)
        checkout_df = pd.read_csv(CHECKOUT_FILE_PATH)
        
        # Fill NaN values in ReturnDate column
        checkout_df['ReturnDate'] = checkout_df['ReturnDate'].fillna(pd.NA)

        # Determine status of each book using a separate DataFrame to avoid inplace setting
        status_series = book_df['ID'].apply(
            lambda book_id: 'Checked Out' 
            if not checkout_df[(checkout_df['BookID'] == book_id) & (checkout_df['ReturnDate'].isna())].empty 
            else 'Available'
        )
        book_df = book_df.assign(Status=status_series)
        
        # Render the table
        return render_template('allbooks.html', tables=[book_df], titles=['Library Books'])
    
    except Exception as e:
        print("An error occurred:", e)
        flash("An error occurred while loading book data.")
        return redirect(url_for('index_page'))
    
    #return render_template('allbooks.html', tables=[book_df.to_html()], titles=[''])

@app.route('/addbook', methods=['GET', 'POST'])
def add_book():
   
    if request.method == 'POST':
        # Retrieve form data
        # ID skipped as it will auto-increment or start at 1 if field not found
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        
        # Validation to ensure no fields are empty
        if not title or not author or not isbn:
            flash('All fields are required.')
            return render_template('addbook.html')
        
        # Check if CSV exists and read existing data
        if os.path.exists(BOOK_FILE_PATH):
            try:
                existing_data = pd.read_csv(BOOK_FILE_PATH)
                if 'ID' in existing_data.columns and not existing_data.empty:
                    new_id = existing_data['ID'].max() + 1  # Set the next ID as the max ID + 1
                else:
                    new_id = 1  # Start from 1 if the file is empty or missing 'id' column
            except pd.errors.EmptyDataError:
                new_id = 1  # If file is empty, start IDs from 1
        else:
            new_id = 1  # If file doesn't exist, start IDs from 1
        
        # Create a dictionary of the new data
        new_data = {
            "id": new_id,
            "Title": title,
            "Author": author,
            "ISBN": isbn
        }
        
        # Convert the dictionary to a DataFrame
        new_df = pd.DataFrame([new_data])
        
        # Append the new data to the CSV file
        new_df.to_csv(BOOK_FILE_PATH, mode='a', header=not os.path.exists(BOOK_FILE_PATH), index=False)
        
        # Flash a success message and redirect to the form page
        flash('Book information saved successfully!')
        return redirect('/addbook')
    
    # Render the form on GET request
    return render_template('addbook.html')


@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    
    # Read the CSV file into a DataFrame
    book_df = pd.read_csv(BOOK_FILE_PATH)
    
    # Filter out the book with the specified ID
    updated_df = book_df[book_df['ID'] != book_id]
    
    # Save the updated DataFrame back to the CSV file, overwriting it
    updated_df.to_csv(BOOK_FILE_PATH, index=False)
    
    # Flash a success message and redirect to the list of books
    flash(f'Book with ID {book_id} deleted successfully!')
    return redirect(url_for('allbooks'))


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    
    # Read the CSV file into a DataFrame
    book_df = pd.read_csv(BOOK_FILE_PATH)
    
    # Find the book by ID and check if it exists
    book = book_df[book_df['ID'] == book_id]
    
    if book.empty:
        flash("Book not found.")
        return redirect(url_for('allbooks'))
    
    # Convert the single-row DataFrame to a dictionary (fill missing values if any)
    book_data = book.iloc[0].fillna('').to_dict()

    # Process the form data if the request is a POST
    if request.method == 'POST':
        # Retrieve updated form data
        updated_title = request.form.get('title')
        updated_author = request.form.get('author')
        updated_isbn = request.form.get('isbn')
        
        # Validate form data to avoid empty values
        if not updated_title or not updated_author or not updated_isbn:
            flash("All fields are required.")
            return redirect(url_for('edit_book', book_id=book_id))

        # Update the book details in the DataFrame
        book_df.loc[book_df['ID'] == book_id, 'Title'] = updated_title
        book_df.loc[book_df['ID'] == book_id, 'Author'] = updated_author
        book_df.loc[book_df['ID'] == book_id, 'ISBN'] = updated_isbn
        
        # Save the updated DataFrame back to the CSV file
        book_df.to_csv(BOOK_FILE_PATH, index=False)
        
        # Flash a success message and redirect to the list of books
        flash('Book updated successfully!')
        return redirect(url_for('allbooks'))
    
    # Render the edit page with the existing book data in dictionary format
    return render_template('editbook.html', book=book_data)



## Endpoints for user functions

@app.route('/all_users')
def allusers():
    user_df = pd.read_csv('Data/Users.csv')
    return render_template('allusers.html', users=user_df.to_dict(orient='records'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Server-side validation
        if not name or not email:
            flash('Both name and email are required.')
            return render_template('adduser.html')
        
        # Determine the new ID
        if os.path.exists(USER_FILE_PATH):
            try:
                user_df = pd.read_csv(USER_FILE_PATH)
                new_id = user_df['ID'].max() + 1 if 'ID' in user_df.columns and not user_df.empty else 1
            except pd.errors.EmptyDataError:
                new_id = 1
        else:
            new_id = 1
        
        # Create new user entry
        new_user = {"ID": new_id, "Name": name, "Email": email}
        
        # Append to CSV
        user_df = pd.DataFrame([new_user])
        user_df.to_csv(USER_FILE_PATH, mode='a', header=not os.path.exists(USER_FILE_PATH), index=False)
        
        # Flash a success message and redirect to the form page
        flash('User information saved successfully!')
        return redirect('/add_user')
    
    # Render the form on GET request
    return render_template('adduser.html')


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    
    # Read the CSV file
    user_df = pd.read_csv(USER_FILE_PATH)
    
    # Filter out the user by ID
    updated_df = user_df[user_df['ID'] != user_id]
    
    # Save the updated DataFrame to CSV
    updated_df.to_csv(USER_FILE_PATH, index=False)
    
    flash('User deleted successfully!')
    return redirect(url_for('allusers'))


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):

    # Read the CSV file into a DataFrame
    try:
        user_df = pd.read_csv(USER_FILE_PATH)
    except pd.errors.EmptyDataError:
        flash("The CSV file is empty or could not be read.")
        return redirect(url_for('allusers'))

    # Ensure 'ID' column exists in the CSV
    if 'ID' not in user_df.columns:
        flash("CSV structure is incorrect. 'ID' column missing.")
        return redirect(url_for('allusers'))

    # Find the user by ID, use squeeze to get a Series
    user = user_df[user_df['ID'] == user_id]
    
    if user.empty:
        flash("User not found.")
        return redirect(url_for('allusers'))

    # Convert to dictionary so Jinja2 can access it easily
    user_data = user.iloc[0].to_dict()

    # Handle the form submission for updating user data
    if request.method == 'POST':
        # Retrieve updated form data
        updated_name = request.form.get('name')
        updated_email = request.form.get('email')
        
        # Update the user details in the DataFrame
        user_df.loc[user_df['ID'] == user_id, 'Name'] = updated_name
        user_df.loc[user_df['ID'] == user_id, 'Email'] = updated_email
        
        # Save the updated DataFrame back to the CSV file
        user_df.to_csv(USER_FILE_PATH, index=False)
        
        # Flash a success message and redirect to the list of users
        flash('User updated successfully!')
        return redirect(url_for('allusers'))
    
    # Render the edit page with the existing user data
    return render_template('edituser.html', user=user_data)




## Endpoints for checkout functions
@app.route('/checkout_book/<int:book_id>', methods=['GET', 'POST'])
def checkout_book(book_id):

    # Load data
    book_df = pd.read_csv(BOOK_FILE_PATH)
    user_df = pd.read_csv(USER_FILE_PATH)
    checkout_df = pd.read_csv(CHECKOUT_FILE_PATH)

    # Verify that the book exists
    if book_id not in book_df['ID'].values:
        flash("Book not found.")
        return redirect(url_for('allbooks'))

    # Check if the book is already checked out
    if not checkout_df[(checkout_df['BookID'] == book_id) & (checkout_df['ReturnDate'].isna())].empty:
        flash("Book is already checked out.")
        return redirect(url_for('allbooks'))

    if request.method == 'POST':
        # Initialize user_id to handle possible cases where it is not set correctly
        user_id = None

        # Retrieve user_id from the form data
        form_user_id = request.form.get('user_id')
        if form_user_id:
            try:
                user_id = int(form_user_id)  # Convert user_id to an integer if it exists
            except ValueError:
                flash("Invalid User ID format.")
                return redirect(url_for('checkout_book', book_id=book_id))

        # Ensure user_id is valid and exists in user_df
        if user_id is None or user_id not in user_df['ID'].values:
            flash("User not found.")
            return redirect(url_for('checkout_book', book_id=book_id))

        # Create a new checkout entry
        new_checkout = pd.DataFrame([{
            'BookID': book_id,
            'UserID': user_id,
            'CheckoutDate': datetime.now().strftime('%Y-%m-%d'),
            'ReturnDate': None  # Indicates the book is not yet returned
        }])

        # Append the new entry to checkout_df and save
        checkout_df = pd.concat([checkout_df, new_checkout], ignore_index=True)
        checkout_df.to_csv(CHECKOUT_FILE_PATH, index=False)

        flash("Book checked out successfully!")
        return redirect(url_for('allbooks'))

    # Render the checkout page for GET request
    return render_template('checkout.html', book_id=book_id, users=user_df.to_dict(orient='records'))


@app.route('/return_book/<int:book_id>', methods=['POST'])
def return_book(book_id):
    checkout_df = pd.read_csv(CHECKOUT_FILE_PATH)

    # Find the latest checkout entry for the book and mark as returned
    latest_checkout = checkout_df[(checkout_df['BookID'] == book_id) & (checkout_df['ReturnDate'].isna())]
    
    if not latest_checkout.empty:
        latest_index = latest_checkout.index[-1]
        checkout_df.loc[latest_index, 'ReturnDate'] = datetime.now().strftime('%Y-%m-%d')
        checkout_df.to_csv(CHECKOUT_FILE_PATH, index=False)
        
        flash("Book returned successfully!")
    else:
        flash("Book is not currently checked out.")
    
    return redirect(url_for('allbooks'))


if __name__ == '__main__':
    app.run(HOST_NAME, HOST_PORT, debug=True)
