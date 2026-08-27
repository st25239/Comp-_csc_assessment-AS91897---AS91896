import datetime
import sqlite3


from flask import Flask, app, json, redirect, redirect, render_template, request, session, flash, redirect, url_for
import json
app = Flask(__name__)
app.secret_key = 'I_love_my_mom'
app.secret_key = 'i_love_Liam_Nguyen'
app.secret_key = 'i_love_Lucas_Smith'
app.secret_key = 'i_love_Leo_Chen'

def initialise_database():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pizza_name TEXT,
                size TEXT,
                quantity INTEGER,
                total_price REAL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()

def load_data():
    try:
        with open('data/pizza.json') as f:
            pizza = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pizza data: {e}")
        pizza = []
    try:
        with open('data/addons.json') as f:
            addons = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading addons data: {e}")
        addons = []
    return pizza, addons

@app.route('/orders')
# the code that displays the order history page and retrieves the order data from the database.
def order_history():
    with sqlite3.connect('Pizza_Place.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY id DESC')
        rows = cursor.fetchall()
        orders = []
        for row in rows:
            orders.append({
                'id': row[0],
                'Invoice Number': row[1],
                'Customer Name': row[2],
                'size': row[3],
                'Total': row[4],
                'addons': row[5],
                'total_price': row[6],
                'order_date': row[7]
            })
    return render_template('order_history.html', orders=orders)

@app.route('/cancel_saved_order/<int:order_id>', methods=['POST'])
# the code that cancels a saved order from the order history page and removes it from the database.
def cancel_saved_order(order_id):
    with sqlite3.connect('Pizza_Place.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
    flash(f'Order {order_id} has been cancelled.')
    return redirect(url_for('order_history'))

@app.route('/calculate_total')
# the code that calculates the total price of the order based on the selected pizza, size, quantity, and any selected add-ons.
def calculate_total(cart, selected_addons):
    total = sum(details['quantity'] * details['price'] for details in cart.values())
    total += sum(price for price in selected_addons.values())
    discount_applied = False
    total = sum(details['quantity'] * details['price'] for details in cart.values())
    
    if total > 100 and not discount_applied:
        discount = total * 0.10  # Calculate the discount amount
        total -= discount  # Apply the discount
        discount_applied = True
        display_discount_message = f"A 10% discount has been applied to your order. You saved ${discount:.2f}."
        flash(display_discount_message)

    return total

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    session.pop('cart', None)
    session.pop('selected_addons', None)
    flash('Your order has been cancelled.')
    session.modified = True 
    return redirect(url_for('index'))

@app.route('/')
def index():
    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {}) # get selected add-ons from session
    pizza, addons = load_data()
    total = calculate_total(cart, selected_addons) #calculate total price based on cart and selected add-ons
    return render_template('index.html', pizza=pizza, addons=addons, cart=cart, total=total, selected_addons=selected_addons)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    customer_name = request.form.get['customer_name'].strip().title()
    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})
    total = calculate_total(cart, selected_addons)
    invoice_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    invoice_number = f"INV-{customer_name.replace(' ', '_')}_{invoice_date}"

    with sqlite3.connect('Pizza_Place.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (invoice_number, customer_name, size, cart, total, addons, order_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_number, customer_name, json.dumps(cart), total, json.dumps(selected_addons), total))
        conn.commit()



















        # make invoice file
    invoice_filename = f"invoice_{invoice_number}.txt"

    try:
            with open(invoice_filename, 'w') as f:
                f.write(f"Invoice Number: {invoice_number}\n")
                f.write(f"Customer Name: {customer_name}\n")
                f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write("Items:\n")
                for item, details in cart.items():
                    f.write(f"- {item} (Size: {details['size']}, Quantity: {details['quantity']}, Price: ${details['price']:.2f})\n")
                if selected_addons:
                    f.write("Add-ons:\n")
                    for addon, price in selected_addons.items():
                        f.write(f"- {addon}: ${price:.2f}\n")
                f.write(f"Total: ${total:.2f}\n")
    except Exception as e:
            flash(f"could not create invoice file")
            print(f"Error creating invoice file: {e}")

        # this rests the cart are purchase
    session.pop('cart', None)
    session.pop('selected_addons', None)
    session.modified = True
    return redirect(url_for('index'))


if __name__ == '__main__':
    initialise_database()
    app.run(debug=True )