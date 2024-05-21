from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import jsonify
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chocolate_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

class Chocolate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

# routes
@app.route('/', methods=['GET'])
def index():
   query = request.args.get('query')
   print("Query Received:", query) 
   chocolates = None
   if query:
       chocolates = Chocolate.query.filter(Chocolate.name.like('%' + query + '%')).all()
       print("Chocolates Found:", chocolates) 
   else:
       chocolates = Chocolate.query.all()
   return render_template('index.html', chocolates=chocolates)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/chocolates')
def chocolates():
    chocolates = Chocolate.query.all()
    if not chocolates:
        return render_template('chocolates.html', chocolates=None)    
    return render_template('chocolates.html', chocolates=chocolates)


@app.route('/chocolates/<int:chocolate_id>')
def chocolate(chocolate_id):
    chocolate = Chocolate.query.get(chocolate_id)
    if not chocolate:
        return 'Chocolate not found', 404
    return render_template('chocolate_detail.html', chocolate=chocolate)

@app.route('/add_chocolate', methods=['GET', 'POST'])
def add_chocolate():
    if request.method == 'POST':
        data = request.form
        new_chocolate = Chocolate(name=data['name'], price=data['price'], stock=data['stock'], description=data['description'])
        db.session.add(new_chocolate)
        db.session.commit()
        return redirect(url_for('chocolates'))
    return render_template('add_chocolate.html')

@app.route('/edit_chocolate/<int:chocolate_id>', methods=['PATCH'])
def update(chocolate_id):
    chocolate = Chocolate.query.get_or_404(chocolate_id)
    data = request.get_json()
    chocolate.name = data.get('name', chocolate.name)
    chocolate.price = data.get('price', chocolate.price)
    chocolate.stock = data.get('stock', chocolate.stock)
    chocolate.description = data.get('description', chocolate.description)
    db.session.commit()
    return jsonify({'message': 'Chocolate updated successfully'}), 200

@app.route('/delete_chocolate/<int:chocolate_id>', methods=['POST'])
def delete(chocolate_id):
    chocolate = Chocolate.query.get(chocolate_id)
    if chocolate:
        db.session.delete(chocolate)
        db.session.commit()
        chocolates = Chocolate.query.all()  
        return render_template('chocolates.html', chocolates=chocolates)
    return 'Chocolate not found', 404


# run the app
if __name__ == '__main__':
    db.create_all()  
    app.run(debug=True)
