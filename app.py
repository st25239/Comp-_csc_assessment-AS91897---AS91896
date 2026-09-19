import datetime
import sqlite3
import json
from flask import Flask, flash, redirect, render_template, request, session, url_for
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
            CREATE TABLE IF NOT EXISTS pizza_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                email TEXT,
                address TEXT,
                card_name TEXT,
                card_number TEXT,
                card_expiry TEXT,
                cart TEXT NOT NULL,
                total REAL NOT NULL,
                addons TEXT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def load_data():
    try:
        with open('data/pizza.json') as f:
            pizza = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pizza data: {e}")
        pizza = {}
    try:
        with open('data/addons.json') as f:
            addons = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading addons data: {e}")
        addons = {}
    return pizza, addons

@app.route('/orders')
# the code that displays the order history page and retrieves the order data from the database.
def order_history():
    initialise_database()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, invoice_number, customer_name, email, address, card_name, card_number, card_expiry,
                   cart, total, addons, order_date
            FROM pizza_orders
            ORDER BY id DESC
        ''')
        rows = cursor.fetchall()
        orders = []
        for row in rows:
            orders.append({
                'id': row[0],
                'invoice_number': row[1],
                'customer_name': row[2],
                'email': row[3],
                'address': row[4],
                'items': json.loads(row[8]),
                'total': row[9],
                'addons': json.loads(row[10] or '{}'),
                'date': row[11]
            })
    return render_template('order_history.html', orders=orders)

@app.route('/cancel_saved_order/<int:order_id>', methods=['POST'])
# the code that cancels a saved order from the order history page and removes it from the database.
def cancel_saved_order(order_id):
    initialise_database()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pizza_orders WHERE id = ?', (order_id,))
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
    return render_template('index.html', pizzas=pizza, addons=addons, cart=cart, total=total, selected_addons=selected_addons, featured_pizzas=list(pizza.items()))


@app.route('/home')
def home():
    return redirect(url_for('index'))


@app.route('/view_cart')
def view_cart():
    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})
    total = calculate_total(cart, selected_addons)
    return render_template('cart.html', cart=cart, selected_addons=selected_addons, total=total)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    pizza = request.form.get('pizza')
    size = request.form.get('size', 'medium')
    pizzas, addons = load_data()  # Load pizza and addons data
    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        quantity = 0
    cart = session.get('cart', {})

    if pizza not in pizzas:
        flash(f"{pizza} is not available.")
        return redirect(url_for('index')) # redirect to the index page if the pizza is not available    

    prices = pizzas[pizza].get('sizes', {})
    if size not in prices or quantity < 1:
        flash('Please choose a valid size and quantity.')
        return redirect(url_for('index'))

    if pizza in cart and cart[pizza]['size'] == size:
        cart[pizza]['quantity'] += quantity
    else:
        cart[pizza] = {
            'quantity': quantity, # store the quantity of the pizza in the cart
            'size': size,
            'price': float(prices[size])
        }

    session['cart'] = cart # update session with the new cart
    session.modified = True # force flask to save the session data
    flash(f'Added {quantity} {pizza}(s) added to cart')
    return redirect(url_for('index'))

@app.route("/remove_from_cart/<item>") #
def remove_from_cart(item):
    cart = session.get('cart', {})

    if item in cart:
        del cart[item]
        session['cart'] = cart
        session.modified = True
        flash(f'{item} removed from cart.')
    else:
        flash(f'{item} not found in cart.')
    return redirect('/')

@app.route ('/selection_addon',methods=['POST'])
def select_addon():
    selected_addons = {}
    _, addons = load_data() # we only need addons

    selected_keys = request.form.getlist('addons')# get     featured_pizzas=    featured_pizzas=list(pizza.items())[:3] of selected addons

    for addon in selected_keys:
        if addon in addons:
            selected_addons[addon] = float(addons[addon]['price']) # store selected addon and its price

    session['selected_addons'] = selected_addons  # store selected addons in session
    session.modified = True # force flask to save the session
    return redirect('/') # redirect to home or any other page where you want to display the selected addons





@app.route('/checkout', methods=['POST'])
def checkout():
    customer_name = request.form.get('customer_name', '').strip().title()
    customer_email = request.form.get('customer_email', '').strip()
    customer_address = request.form.get('customer_address', '').strip()
    card_name = request.form.get('card_name', '').strip().title()
    card_number = request.form.get('card_number', '').strip().replace(' ', '')
    card_expiry = request.form.get('card_expiry', '').strip()

    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})
    total = calculate_total(cart, selected_addons)
    invoice_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    invoice_number = f"INV-{customer_name.replace(' ', '_')}_{invoice_date}"

    masked_card = f"•••• •••• •••• {card_number[-4:]}" if card_number and card_number.isdigit() and len(card_number) >= 4 else 'Not provided'

    initialise_database()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pizza_orders (invoice_number, customer_name, email, address, card_name, card_number, card_expiry, cart, total, addons, order_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice_number,
            customer_name,
            customer_email,
            customer_address,
            card_name,
            masked_card,
            card_expiry,
            json.dumps(cart),
            total,
            json.dumps(selected_addons),
            invoice_date
        ))
        conn.commit()

    invoice_filename = f"invoice_{invoice_number}.txt"

    try:
        with open(invoice_filename, 'w') as f:
            f.write(f"Invoice Number: {invoice_number}\n")
            f.write(f"Customer Name: {customer_name}\n")
            f.write(f"Email: {customer_email}\n")
            f.write(f"Address: {customer_address}\n")
            f.write(f"Payment: {card_name} - {masked_card}\n")
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
        flash("could not create invoice file")
        print(f"Error creating invoice file: {e}")

    try:
        if not customer_name:
            flash("please enter your name before proceeding to checkout.")
            return redirect(url_for('index'))

        if not customer_email:
            flash("Please enter your email before checkout.")
            return redirect(url_for('view_cart'))

        if not customer_address:
            flash("Please enter your delivery address before checkout.")
            return redirect(url_for('view_cart'))

        if not cart:
            flash("Your cart is empty. Please add items to your cart before proceeding to checkout.")
            return redirect(url_for('index'))

        with open('data/pizza.json', 'r') as file:
            pizza_data = json.load(file)

        for pizza_name, details in cart.items():
            if pizza_name in pizza_data:
                pizza_data[pizza_name]['stock'] -= details['quantity']
                if pizza_data[pizza_name]['stock'] < 0:
                    pizza_data[pizza_name]['stock'] = 0

        with open('data/pizza.json', 'w') as file:
            json.dump(pizza_data, file, indent=4)

    except Exception as e:
        flash(f"An error occurred while updating the stock: {e}")
        return redirect(url_for('index'))

    session.pop('cart', None)
    session.pop('selected_addons', None)
    session.modified = True

    return render_template(
        'invoice.html',
        customer_name=customer_name,
        customer_email=customer_email,
        customer_address=customer_address,
        cart=cart,
        total=total,
        selected_addons=selected_addons,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        masked_card=masked_card,
        card_name=card_name
    )


if __name__ == '__main__':
    initialise_database()
    app.run(debug=True )