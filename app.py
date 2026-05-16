from enum import nonmember

import requests
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    note = db.Column(db.String(200), nullable=True)

API_KEY = os.environ.get('API_KEY')
@app.route('/', methods=['GET', 'POST'])
def home():
    stock_data = None
    watchlist_data = watchlist.query.all()
    if request.method == "POST":
        ticker = request.form['ticker'].upper()
        note = request.form['note']
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={API_KEY}"

        response = requests.get(url)
        data = response.json()
        if "c" in data:
            stock_data = {
                "ticker": ticker,
                "price": data["c"],
                "high": data["h"],
                "low": data["l"],
                "note": note
            }
    return render_template(
        "index.html",
        stock_data=stock_data,
        watchlist = watchlist_data
    )
@app.route('/add/<ticker>')
def add_stock(ticker):
    ticker = ticker.upper()
    note = request.args.get('note')
    new_stock = watchlist(
        ticker = ticker,
        note = note
    )
    db.session.add(new_stock)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_stock(id):
    stock_to_delete = watchlist.query.get(id)
    if stock_to_delete:
        db.session.delete(stock_to_delete)
        db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)


