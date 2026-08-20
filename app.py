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

@app.route('/orders')
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
def cancel_saved_order(order_id):
    with sqlite3.connect('Pizza_Place.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
    flash(f'Order {order_id} has been cancelled.')
    return redirect(url_for('order_history'))





if __name__ == '__main__':
    initialise_database()
    app.run(debug=True)