from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from configs.base_config import *
import pygal 
import email_validator
from flask_login import UserMixin, logout_user, login_user, LoginManager, login_required, current_user,login_manager
from wtforms import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from passlib.apps import custom_app_context as pwd_context
from flask_bcrypt import Bcrypt,generate_password_hash,check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisisanapp'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.config.from_object(Staging)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:nelsonkimathi123@localhost:5432/sales_database'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_message_category = 'info'
login_manager.login_view = 'login'


@app.before_first_request
def create_tables():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Item(db.Model):
    __tablename__ = 'inventories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    stock = db.Column(db.Integer, unique=False, nullable=False)
    buying_price = db.Column(db.Integer, unique=False, nullable=False)
    selling_price = db.Column(db.Integer, unique=False, nullable=False)

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    quantity = db.Column(db.Integer, primary_key=True)
    created_at =  db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    inv_id = db.Column(db.Integer, db.ForeignKey('inventories.id'),nullable=False)
    inventories = db.relationship('Item',backref=db.backref('sales', lazy=True))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    fullname = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class RegistrationForm(Form):
    fullname = StringField('Full name', validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=200)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up') 


class LoginForm(Form):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


@app.route('/add_details', methods = ['GET','POST'])
@login_required
def add_details():
    if request.method == 'POST':
       name = request.form['name']
       stock = request.form['stock']
       buying_price = request.form['buying_price']
       selling_price = request.form['selling_price']
     
       print(name ,stock, buying_price ,selling_price)
       inventories = Item(name = name, stock = stock, buying_price = buying_price, selling_price = selling_price)
       print('Record successfully added')
       db.session.add(inventories)
       db.session.commit()
       return redirect(url_for('add_details'))
    else:
        goods = Item.query.all()
        return render_template('items.html', goods = goods)

@app.route('/register', methods = ['GET','POST'])
def register(): 
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.validate():
            bcrypt = Bcrypt()
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(fullname = form.fullname.data, email = form.email.data, password = hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(u'Your account has been created! You are now logged in', 'success')
            return redirect(url_for('add_details', title = 'Register', form = form))
    return render_template('register.html', form = form)
@app.route('/', methods = ['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
       if form.validate():
           bcrypt = Bcrypt()
           user = User.query.filter_by(email=form.email.data).first()
           if user and bcrypt.check_password_hash(user.password, form.password.data):
               login_user(user, remember=form.remember.data)
               return redirect(url_for('add_details'))
           else:
               flash(u'Login Unsuccessful. Please check your email and password', 'danger')
    return render_template('login.html', title = 'Login', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
  

@app.route('/sale/<int:inv_id>', methods = ['GET','POST'])
@login_required
def make_sales(inv_id):
    if request.method == 'POST':
       quantity = request.form['quantity']
       inv_id = request.form['inv_id']
       
       n = Item.query.filter_by(id = inv_id).first()
       n.stock = int(n.stock) - int(quantity)
       if int(n.stock) < 0:
           flash(u"Quantity entered is more than stock", 'error')
           return redirect(url_for('add_details'))
       elif int(quantity) <= 0:
           flash(u"Invalid quantity entered. Enter amount greater than 0", 'error')
           return redirect(url_for('add_details'))
       elif Item.stock == 0:
           flash(u"There is no stock available for this item.", 'error')
           return redirect(url_for('add_details'))
       print(quantity ,inv_id)
       db.session.add(n)
       db.session.commit()    
       sale = Sale(quantity = quantity, inv_id = inv_id)
       db.session.add(sale)
       db.session.commit()
       return redirect(url_for('add_details'))        
    else:
        return render_template('items.html')

@app.route('/edit/<int:y>', methods = ['GET','POST'])
@login_required
def edititem(y):
    if request.method == 'GET':
        editem = Item.query.filter_by(id = y).first()
        print(editem)
        return render_template('edititem.html', form = editem)
    else:    
        editem = Item.query.filter_by(id = y).first()
        editem.name = request.form['name']
        editem.stock = request.form['stock']
        editem.buying_price = request.form['buying_price']
        editem.selling_price = request.form['selling_price']

        db.session.add(editem)
        db.session.commit()
        print("Record successfully edited")
        return redirect(url_for('add_details'))

@app.route('/viewsales/<int:x>', methods = ['GET'])
@login_required
def viewsales(x):
    if request.method == 'GET':
        item_sale = Sale.query.filter_by(inv_id = x).all()
        s_item = Item.query.filter_by(id = x).all()
        print(item_sale)
        return render_template('viewsales.html', posts = item_sale)

@app.route('/all_sales', methods = ['GET'])
@login_required
def all_sales():
    if request.method == 'GET':
        sale_all = Sale.query.all()
        print(sale_all)
        return render_template('all_sale.html', invent = sale_all)

@app.route('/inventory', methods = ['GET'])
@login_required
def inventory():
    if request.method == 'GET':
        inv_all = Item.query.with_entities(Item.id,Item.name,Item.stock).all()
        print(inv_all)
        return render_template('inventory.html',advant = inv_all)


@app.route('/charting')
@login_required
def charting():
    sale_data = Sale.query.with_entities(Sale.quantity).all()
    sale_date = Sale.query.with_entities(Sale.created_at).all()
    sales = Sale.query.all()

    chart_data = {}
   
    # Adding values in a dictionary according to their keys if the keys are the same 
    for s in sales:
        dt = s.created_at.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        if str(dt) in chart_data.keys():
            chart_data[str(dt)] = chart_data[str(dt)] + s.quantity
        else:
            chart_data[str(dt)] = s.quantity
    print(chart_data)

    line_chart = pygal.Bar()
    line_chart.title = 'Sales Made in 2021'
    for k,v in chart_data.items():
        line_chart.add(k, v)
    chart = line_chart.render()
    return render_template('charting.html', chart = chart)

if __name__=="__main__":
    app.run(debug=True)

