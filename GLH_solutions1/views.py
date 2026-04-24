"""
Routes and views for the flask application.
"""


from datetime import datetime #imports the date and time to aid the project in keeping track of events and necessary time stamps.
from arrow import get
from flask import flash, jsonify, render_template, request, redirect, url_for,session
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import sqlite3
from GLH_solutions1 import DATABASE, app
from werkzeug.security import check_password_hash, generate_password_hash

from GLH_solutions1.contact import get_db_connection
app.secret_key = 'oluisthegoat1'


login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password



@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        username = current_user
    )

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    user_row = conn.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    if user_row:
        return User(user_row['id'], user_row['username'], user_row['email'], user_row['password'])
    return None



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phonenumber = request.form['phonenumber']
        email = request.form['email']
        message = request.form['subject']

        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (firstname, lastname, phonenumber, email, message) VALUES (?, ?, ?, ?, ?)", 
                           (firstname, lastname, phonenumber, email, message))
            conn.commit()
            conn.close()
            flash('Your message has been sent!', 'success')
        except:
            flash('Something went wrong. Please try again.', 'error')
        

        #Renders the contact page.
    return render_template(
        'contact.html',
        title='GLH Contact page',
        year=datetime.now().year,
        message1='Your direct line to contact us at the Greenfield Local Hub'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )



def add_products():
    conn = get_db_connection()
    cursor = conn.cursor()

    existing_products = cursor.execute("SELECT COUNT(*) FROM product_item").fetchone()[0]
    if existing_products >= 3:
        cursor.execute(
            "INSERT INTO product_item(name, descr, price, img, stock, producer) VALUES (?, ?, ?, ?, ?, ?)",
            ("Cornish Crab", "Delectable and delicious crab", 11.99, "crab.jpg", 25, "John")
            )
        cursor.execute(
            "INSERT INTO product_item(name, descr, price, img, stock, producer) VALUES (?, ?, ?, ?, ?, ?)",
            ("Eggs", "Farm fresh free to range eggs, 30 per crate", 22.00, "eggs.jpg", 25, "Erick")
        )
        cursor.execute(
            "INSERT INTO product_item(name, descr, price, img, stock, producer) VALUES (?, ?, ?, ?, ?, ?)",
            ("Mackarel", "Fresh Whole Mackerel Fish (1kg) | Raw Premium Quality Seafood", 15.00, "mackarel.jpg", 25, "Brooks")
            )
        cursor.execute(
            "INSERT INTO product_item(name, descr, price, img, stock, producer) VALUES (?, ?, ?, ?, ?, ?)",
            ("Prawns", "Cooked Shell On Frozen Cold Water Prawns 90 - 120 Prawns 5kg  Premium Wild-Caught Seafood for Salads, Cocktails, BBQ & Gourmet Dishes", 60.00, "prawn.jpg", 25, "Ally")
            )

        cursor.execute(
            "INSERT INTO product_item(name, descr, price, img, stock, producer) VALUES (?, ?, ?, ?, ?, ?)",
            ("Milk", "Semi-skimmed and refreshing jug milk", 4.50, "milk.jpg", 25, "Carlinhos")
            )
        conn.commit()
        conn.close()


@app.route('/products')
def product():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM product_item").fetchall()
    conn.close()
    return render_template(
        'product.html',
        products = products,
        title='Product page',
        year=datetime.now().year,
        message='Your product page.'
    )


@app.route("/cart")
@login_required
def cart():
    conn = get_db_connection()
    cart_items = conn.execute("""
       SELECT 
         product_item.id AS product_id,
         product_item.name,
         product_item.price,
         product_item.img,
         COUNT(cart_item.id) AS quantity,
         SUM(product_item.price) AS subtotal
       FROM cart_item
       JOIN product_item ON cart_item.product_id = product_item.id
       GROUP BY product_item.id, product_item.name, product_item.price, product_item.img
    """).fetchall()

    total_price = conn.execute("""
       SELECT COALESCE(SUM(product_item.price), 0)AS total
       FROM cart_item
       JOIN product_item ON cart_item.product_id = product_item.id
    
    """).fetchone()["total"]

    conn.close()
    return render_template(
        "cart.html",
        cart_items = cart_items,
        total_price = total_price
        )


@app.route("/checkout")
def checkout():
    conn = get_db_connection()
    cart_items = conn.execute("""
       SELECT 
         product_item.id AS product_id,
         product_item.name,
         product_item.price,
         product_item.img,
         COUNT(cart_item.id) AS quantity,
         SUM(product_item.price) AS subtotal
       FROM cart_item
       JOIN product_item ON cart_item.product_id = product_item.id
       GROUP BY product_item.id, product_item.name, product_item.price, product_item.img
    """).fetchall()

    total_price = conn.execute("""
       SELECT COALESCE(SUM(product_item.price), 0)AS total
       FROM cart_item
       JOIN product_item ON cart_item.product_id = product_item.id
    
    """).fetchone()["total"]

    conn.close()
    return render_template(
        "checkout.html",
        cart_items = cart_items,
        total_price = total_price
        )

@app.route("/order_confirmed")
def order_confirmed():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart_item")
    conn.commit()
    conn.close()
    return redirect(url_for("udashboard"))



@app.route("/cart/add/<int:product_id>", methods = ["POST"])
def add_to_cart(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO cart_item(product_id)VALUES(?)",(product_id,))
    conn.commit()
    conn.close()
    return jsonify({"message":"Item added to cart"})

#reduce how many items in cart
@app.route("/cart/decrease/<int:product_id>", methods=["POST"])
def decrease_quantity(product_id):
    # Open connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find one cart row for this product
    cart_row = cursor.execute("""
        SELECT id
        FROM cart_item
        WHERE product_id = ?
        LIMIT 1
    """, (product_id,)).fetchone()

    # If found, delete one row
    if cart_row:
        cursor.execute(
            "DELETE FROM cart_item WHERE id = ?",
            (cart_row["id"],)
        )
        conn.commit()

    # Close connection
    conn.close()

    # Go back to cart page
    return redirect(url_for("cart"))

#add number of products
@app.route("/cart/increase/<int:product_id>", methods=["POST"])
def increase_quantity(product_id):
    # Open connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Add one more of this product to the cart
    cursor.execute(
        "INSERT INTO cart_item (product_id) VALUES (?)",
        (product_id,)
    )

    # Save change
    conn.commit()

    # Close connection
    conn.close()

    # Go back to cart page
    return redirect(url_for("cart"))

#remove all items of a product
@app.route("/cart/remove_all/<int:product_id>", methods=["POST"])
def remove_all_of_item(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM cart_item WHERE product_id = ?",
        (product_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("cart"))



#clear all items
@app.route("/cart/clear", methods=["POST"])
def clear_cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart_item")
    conn.commit()
    conn.close()
    return redirect(url_for("product"))


#to view the cart and final prices
@app.route("/view_cart")
def view_cart():

    conn = get_db_connection()

    cart_items = conn.execute("""
        SELECT
            product_item.name,
            product_item.price,
            COUNT(cart_item.id) AS quantity
        FROM cart_item
        JOIN product_item ON cart_item.product_id = product_item.id
        GROUP BY product_item.id, product_item.name, product_item.price
    """).fetchall()


    total_price = conn.execute("""
        SELECT COALESCE(SUM(product_item.price), 0) AS total
        FROM cart_item
        JOIN product_item ON cart_item.product_id = product_item.id
    """).fetchone()["total"]


    conn.close()
    cart_contents = {}

    for item in cart_items:
        cart_contents[item["name"]] = item["quantity"]

    return jsonify({
        "cart_contents": cart_contents,
        "total_price": total_price
    })



#to register new users
@app.route('/register', methods=['GET', 'POST'])
def register():
        if request.method == 'POST':
            username = request.form["username"].strip()
            email = request.form["email"].strip()
            firstname = request.form["firstname"]
            lastname = request.form["lastname"]
            phonenumber = request.form["phonenumber"]
            birthday = request.form["birthday"]
            county = request.form["county"]
            password = request.form["password"]

            if not username or not password:
                flash("Username and password are required.")
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)

            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user (username, email, firstname, lastname, phonenumber, birthday, county, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (username,  email, firstname, lastname, phonenumber, birthday, county, hashed_password))
                conn.commit()
                conn.close()
                flash("Registration successful! Please log in.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username already exists.")
                return redirect(url_for("register"))
        return render_template('register.html',
            title = 'Register page',
            year = datetime.now().year)

#to log in the system
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row

        user_row = conn.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user_row and check_password_hash(user_row['password'], password):

            user_obj = User(user_row['id'], user_row['username'], user_row['email'], user_row['password'])
            

            login_user(user_obj)
            flash("Logged in successfully!")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template(
        'login.html',
        title = 'Login page',
        year = datetime.now().year)


#to log out the system
@login_required
@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("home"))
