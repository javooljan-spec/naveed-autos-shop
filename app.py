from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =============================
# Database Models
# =============================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    cost_price = db.Column(db.Float)
    sell_price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    quantity_sold = db.Column(db.Integer)
    profit = db.Column(db.Float)
    date = db.Column(db.String(20))

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    amount = db.Column(db.Float)
    shop_name = db.Column(db.String(100))

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(200))
    amount = db.Column(db.Float)
    date = db.Column(db.String(20))

with app.app_context():
    db.create_all()

# =============================
# Routes
# =============================

@app.route('/')
def index():
    products = Product.query.all()
    sales = Sale.query.all()
    investments = Investment.query.all()
    expenses = Expense.query.all()

    # ========== Dashboard Summary ==========
    total_profit = sum(s.profit for s in sales)
    total_investment = sum(i.amount for i in investments)
    total_expense = sum(e.amount for e in expenses)
    net_balance = total_profit - total_expense  # profit minus expense

    # ========== Chart Data (Last 7 days) ==========
    chart_data = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_profit = sum(s.profit for s in sales if s.date == day)
        chart_data.append({"date": day, "profit": day_profit})

    return render_template(
        'index.html',
        products=products,
        sales=sales,
        investments=investments,
        expenses=expenses,
        chart_data=chart_data,
        total_profit=total_profit,
        total_investment=total_investment,
        total_expense=total_expense,
        net_balance=net_balance
    )

# ---------------------------
# Add Product
# ---------------------------
@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    company = request.form['company']
    cost_price = float(request.form['cost_price'])
    sell_price = float(request.form['sell_price'])
    quantity = int(request.form['quantity'])
    product = Product(name=name, company=company, cost_price=cost_price, sell_price=sell_price, quantity=quantity)
    db.session.add(product)
    db.session.commit()
    return redirect('/')

# ---------------------------
# Add Sale
# ---------------------------
@app.route('/add_sale', methods=['POST'])
def add_sale():
    product_id = int(request.form['product_id'])
    qty_sold = int(request.form['quantity_sold'])
    product = Product.query.get(product_id)

    if not product or product.quantity < qty_sold:
        return "Error: Not enough quantity available"

    profit = (product.sell_price - product.cost_price) * qty_sold
    sale = Sale(
        product_id=product.id,
        product_name=product.name,
        company=product.company,
        quantity_sold=qty_sold,
        profit=profit,
        date=datetime.now().strftime('%Y-%m-%d')
    )

    product.quantity -= qty_sold
    db.session.add(sale)
    db.session.commit()
    return redirect('/')

# ---------------------------
# Add Investment
# ---------------------------
@app.route('/add_investment', methods=['POST'])
def add_investment():
    product_id = int(request.form['product_id'])
    amount = float(request.form['amount'])
    shop_name = request.form['shop_name']

    product = Product.query.get(product_id)
    investment = Investment(
        product_id=product.id,
        product_name=product.name,
        company=product.company,
        amount=amount,
        shop_name=shop_name
    )
    db.session.add(investment)
    db.session.commit()
    return redirect('/')

# ---------------------------
# Add Expense
# ---------------------------
@app.route('/add_expense', methods=['POST'])
def add_expense():
    desc = request.form['desc']
    amount = float(request.form['amount'])
    date = request.form['date']
    expense = Expense(desc=desc, amount=amount, date=date)
    db.session.add(expense)
    db.session.commit()
    return redirect('/')

# =============================
# Main
# =============================
if __name__ == '__main__':
    app.run(debug=True)