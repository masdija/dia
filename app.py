
import mysql.connector
from werkzeug.utils import secure_filename

from distutils.log import debug 

from flask import *  

from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime
# import sqlDatabaseCreation


app = Flask(__name__)


app.secret_key = 'your secret key'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'koren'
# app.config['MYSQL_DB'] = 'diaDB'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:koren@localhost/diaDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config["UPLOAD_FOLDER"] = "static/uploads/"



db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


all_entrys = []

current_year = datetime.now().year

with app.app_context():
    

    mydb = mysql.connector.connect(user='root',password='koren',host='localhost',)

    cursor = mydb.cursor()

    # cursor.execute("SHOW DATABASES")

    cursor.execute("CREATE DATABASE IF NOT EXISTS diaDB\
                   DEFAULT CHARACTER SET utf8\
                       COLLATE utf8_general_ci;")
    cursor.execute("USE diaDB;")
    
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
    #Line below only required once, when creating DB. 
    #db.create_all()
    
    class Orders(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        order_number = db.Column(db.Integer, unique=True)
        group = db.Column(db.String(100))
        system = db.Column(db.String(100))
        obiject = db.Column(db.String(100))
        machine = db.Column(db.String(100))
        tiype = db.Column(db.String(100))
        sort = db.Column(db.String(100))
        orderer = db.Column(db.String(100))
        date = db.Column(db.String(100))
        reliser = db.Column(db.String(100))
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():  
    return render_template("index.html", entrys=all_entrys, year=current_year)



@app.route('/index', methods=["GET", "POST"])
def home1():  
    return render_template("index1.html", entrys=all_entrys, year=current_year)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # login_user(new_user)
        return redirect(url_for("login"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
    
        user = User.query.filter_by(email=email).first()
        #Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        #Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        #Email exists and password correct
        else:
            login_user(user)
            return redirect(url_for('home1'))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/vibrodijagnostika")
def vibro():
    return render_template("vibrodijagnostika.html")


@app.route("/ultrazvuk")
def ultra():
    return render_template("ultrazvuk.html")


@app.route("/centriranje")
def cent():
    return render_template("centriranje.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST" :
        new_entry = {
            "order_number": request.form["order_number"],
            "group": request.form["group"],
            "system": request.form["system"],
            "obiject" : request.form["obiject"],
            "machine" : request.form["machine"],
            "tiype": request.form["tiype"],
            "sort": request.form["sort"],
            "orderer" : request.form["orderer"],
            "date" : request.form["date"],
            "reliser" : request.form["reliser"]
        }
        all_entrys.append(new_entry)

        new_order = Orders(
            order_number=request.form.get('order_number'),
            group=request.form.get('group'),
            system=request.form.get('system'),
            obiject=request.form.get('obiject'),
            machine=request.form.get('machine'),
            tiype=request.form.get('tiype'),
            sort=request.form.get('sort'),
            orderer=request.form.get('orderer'),
            date=request.form.get('date'),
            reliser=request.form.get('reliser')
        )
        db.session.add(new_order)
        db.session.commit()
        
        return redirect(url_for('show'))
    else:  
        return render_template("add.html",year=current_year)


#NOTE: You can use the redirect method from flask to redirect to another route 
# e.g. in this case to the home page after the form has been submitted.  
@app.route("/show")
@login_required
def show():
    return render_template("show.html",entrys=all_entrys)


@app.route("/show_permanent",methods=["GET", "POST"])
@login_required
def show_permanent():
    if request.method == "GET":
        order = db.session.query(Orders).all()
    return render_template("show_permanent.html",query=order)


@app.route("/forum")
def forum():
    return render_template("forum.html")



@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", name=current_user.name)


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', path="files/cheat_sheet.pdf")


# @app.route('/success', methods = ['POST'])   
# def success():   
#     if request.method == 'POST':   
#         f = request.files['file'] 
#         f.save(f.filename)   
#         return render_template("Acknowledgement.html", name = f.filename)
 


  
@app.route('/display', methods = ['GET', 'POST'])
def display_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)

        f.save(app.config['UPLOAD_FOLDER'] + filename)

        # file = open(app.config['UPLOAD_FOLDER'] + filename,"r",encoding='utf8')
        # # content = file.read()   
        
    return render_template('content.html') 
   # content=content
 
    
if __name__ == "__main__":
      app.run(host='0.0.0.0')
