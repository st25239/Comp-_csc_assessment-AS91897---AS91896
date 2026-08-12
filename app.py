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
        c = conn.cursor()
      
        conn.commit()
















if __name__ == '__main__':
    initialise_database()
    app.run(debug=True)