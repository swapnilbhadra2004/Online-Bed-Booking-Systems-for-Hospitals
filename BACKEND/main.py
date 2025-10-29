from flask import Flask,redirect,render_template,request,flash,session
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
from flask_login import UserMixin
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import text
from flask.helpers import url_for
import json


#database connection
local_server=True
app = Flask(__name__)
app.secret_key = "swapnil" 
login_manager = LoginManager(app)
login_manager.login_view="login"


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/hospital'
db = SQLAlchemy(app)

with(open('config.json','r')) as c:
    params=json.load(c)["params"]


@login_manager.user_loader
def load_user(user_id):
    from flask import session
    user_type = session.get("user_type")

    if user_type == "user":
        return User.query.get(int(user_id))
    elif user_type == "hospital":
        return Hospitaluser.query.get(int(user_id))
    return None

   



class Test(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(50))
class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    srf = db.Column(db.String(20),unique = True)
    email = db.Column(db.String(100),unique = True)
    dob = db.Column(db.String(100))
class Hospitaluser(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    hcode = db.Column(db.String(20),unique = True)
    email = db.Column(db.String(100),unique = True)
    password = db.Column(db.String(1000))
class Hospitaldata(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    hcode = db.Column(db.String(200),unique = True)
    hname = db.Column(db.String(200))
    normal = db.Column(db.Integer)
    icu = db.Column(db.Integer)
    hicu = db.Column(db.Integer)
    ventilator = db.Column(db.Integer)
class Bookingpatients(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    srfid = db.Column(db.String(50),unique = True)
    bedtype = db.Column(db.String(50))
    hcode = db.Column(db.String(50))
    spo2 = db.Column(db.Integer)
    pname = db.Column(db.String(50))
    phone = db.Column(db.Integer)
    address = db.Column(db.String(200))
class Trigger_log(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key = True)
    hcode = db.Column(db.String(200))
    normal = db.Column(db.Integer)
    icu = db.Column(db.Integer)
    hicu = db.Column(db.Integer)
    ventilator = db.Column(db.Integer)
    action = db.Column(db.String(50))
    time = db.Column(db.String(50))

#connections to frontend
@app.route("/")
def home():
    return render_template("index.html")


#to check user sign - in
@app.route("/usersignup")
def usersignup():
   return render_template("usersignin.html")


#to check user login
@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")


@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method == "POST":
       # print(request.form)
        srf = request.form.get("srf")
        email = request.form.get("email")
        dob = request.form.get("dob")
        encpassword = generate_password_hash(dob) 
        user = User.query.filter_by(srf=srf).first()
        emailuser = User.query.filter_by(email=email).first()
        emailuser1 = Hospitaluser.query.filter_by(email=email).first()
        print(email)
        if emailuser1:
             flash("Email used by hospital staff","danger")
             return render_template("usersignin.html")
        elif user or emailuser:
            flash("Email or srf id is already taken","warning")
            return render_template("usersignin.html")
        db.session.execute(text("INSERT INTO user (srf, email, dob) VALUES (:srf, :email, :dob)"),{"srf": srf, "email": email, "dob": encpassword})
        db.session.commit()
        flash("Signup success.Please login","success")
        return render_template("userlogin.html")
    return render_template("userlogin.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful","Success")
    return redirect(url_for('login'))

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
       # print(request.form)
        srf = request.form.get("srf")
        dob = request.form.get("dob")
        user = User.query.filter_by(srf=srf).first()
        if(user and check_password_hash(user.dob,dob)):
            login_user(user)
            session["user_type"] = "user"
            flash("Authentication success","info")
            return render_template("index.html")
        else:
            flash("Invalid credentials","danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")


#admin login
@app.route("/admin",methods=["POST","GET"])
def admin():
    if request.method == "POST":
       # print(request.form)
        username = request.form.get("username")
        password = request.form.get("password")
        if(username==params["user"] and password==params["password"]):
                    session["user"] = username
                    flash("login success","success")
                    return render_template("addHospitalUser.html")
        else:
            flash("Invalid Credentials","danger")
    return render_template("admin.html")


@app.route("/addhospitaluser",methods=["POST","GET"])
def addhospitaluser():
    if("user" in session and session["user"] == params["user"]):
           if request.method == "POST":
                 hcode = request.form.get("hcode")
                 email = request.form.get("email")
                 password = request.form.get("password")
                 hcode = hcode.upper()
                 encpassword = generate_password_hash(password) 
                 emailuser = Hospitaluser.query.filter_by(email=email).first()
                 hcodeuser = Hospitaluser.query.filter_by(hcode=hcode).first()
                 if(emailuser or hcodeuser):
                          flash("Email or hcode is already taken","warning")
                          return render_template("addHospitalUser.html")
                 db.session.execute(text("INSERT INTO hospitaluser (hcode, email, password) VALUES (:hcode, :email, :password)"),{"hcode": hcode, "email": email, "password": encpassword})
                 db.session.commit()
                 flash("Data has been added successfully","success")
                 return render_template("addHospitalUser.html")
                

    else:
         flash("You need to login first","warning")
         return redirect("/admin")
    return render_template("addHospitalUser.html")

@app.route("/logoutadmin")
def logoutadmin():
     session.pop("user")
     flash("You are logged out","primary")
     return redirect("/admin")


@app.route("/hospitallogin",methods=["POST","GET"])
def hospitallogin():
    logout_user()
    if request.method == "POST":
       # print(request.form)
        email = request.form.get("email")
        password = request.form.get("password")
        user = Hospitaluser.query.filter_by(email=email).first()
        if(user and check_password_hash(user.password,password)):
            print(user.email)
            login_user(user)
            session["user_type"] = "hospital"
            flash("Authentication success","info")
            return render_template("index.html")
        else:
            flash("Invalid credentials","danger")
            return render_template("hospitallogin.html")

    return render_template("hospitallogin.html")




#checking connections to db
@app.route("/test")
def test():
    try:
        a = Test.query.all()
        print(a)
        return f'connection succesful'
    except Exception as e:
          print(e)
          print("connection lost")    


@app.route("/addhospitalinfo",methods=["POST","GET"])
def addhospitalinfo():
     #data = db.engine.execute("select * from hospitalusers")
     #logout_user()
     postdata=None
     if not current_user.is_authenticated:
        flash("Please log in to add hospital information", "warning")
        return render_template("hospitallogin.html")
     
     email = current_user.email
     
     print(email)
     if(email is None):
          flash("Hospital does not exist","danger")
          return render_template("hospitallogin.html")
     posts = Hospitaluser.query.filter_by(email=email).first()
     if posts is None:
        flash("No hospital user found for this account", "danger")
        return render_template("hospitallogin.html")
     code=posts.hcode
     postdata=Hospitaldata.query.filter_by(hcode=code).first()
     if request.method == "POST":
                 hcode = request.form.get("hcode")
                 hname = request.form.get("hname")
                 normal = request.form.get("normal")
                 icu = request.form.get("icu")
                 hicu = request.form.get("hicu")
                 ventilator = request.form.get("ventilator")
                 hcode = hcode.upper()
                 huser = Hospitaluser.query.filter_by(hcode=hcode).first()
                 hduser = Hospitaldata.query.filter_by(hcode=hcode).first()
                 if(hduser):
                      flash("Data has been addd already.You can only update it","info")
                      return render_template("hospitaldata.html",postdata=postdata)
                 if(huser):
                  db.session.execute(text("INSERT INTO hospitaldata(hcode,hname,normal,icu,ventilator,hicu) VALUES (:hcode, :hname, :icu,:normal,:ventilator,:hicu)"),{"hcode": hcode, "hname": hname,"normal":normal ,"icu": icu ,"ventilator":ventilator,"hicu":hicu})
                  db.session.commit()
                  flash("Data has been added","success")
                  postdata = Hospitaldata.query.filter_by(hcode=hcode).first()
                 
                 else:
                      flash("Hospital code does not exist","danger")
                      return redirect('/addhospitaluser')
     return render_template("hospitaldata.html",postdata=postdata,code=code)


@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
     post = Hospitaldata.query.filter_by(id=id).first()
     if request.method == "POST":
                 hcode = request.form.get("hcode")
                 hname = request.form.get("hname")
                 normal = request.form.get("normal")
                 icu = request.form.get("icu")
                 hicu = request.form.get("hicu")
                 ventilator = request.form.get("ventilator")
                 hcode = hcode.upper()
                 db.session.execute(text("UPDATE hospitaldata SET hname=:hname, normal=:normal, icu=:icu, ventilator=:ventilator, hicu=:hicu WHERE id =:id"), {"hcode": hcode, "hname": hname, "normal": normal, "icu": icu, "ventilator": ventilator, "hicu": hicu ,"id":id})
                 db.session.commit()
                 flash("Data updated","success")
                 return redirect("/addhospitalinfo")
     #post = Hospitaldata.query.filter_by(id=id).first()
     return render_template("hedit.html",posts=post)


@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    # post = Hospitaldata.query.filter_by(id=id).first()
     db.session.execute(text("DELETE FROM hospitaldata where id =:id "),{"id":id})
     db.session.commit()
     flash("Data has been deleted","success")
     return redirect("/addhospitalinfo")




@app.route("/bedbooking", methods=['POST', 'GET'])
@login_required
def bedbooking():
    hospitals = db.session.execute(text("SELECT * FROM hospitaldata")).fetchall()

    if request.method == "POST":
        srfid = request.form.get('srfid')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode')
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        phone = request.form.get('phone')
        address = request.form.get('address')

        # Check if patient already exists
        existing_patient = Bookingpatients.query.filter_by(srfid=srfid).first()
        if existing_patient:
            flash("This SRF ID is already registered.", "warning")
            return render_template("booking.html", query1=hospitals,query=hospitals)

        # Check hospital existence
        hospital = Hospitaldata.query.filter_by(hcode=hcode).first()
        if not hospital:
            flash("Invalid hospital code.", "danger")
            return render_template("booking.html", query1=hospitals,query=hospitals)

        # Determine seat availability based on bed type
        if bedtype == "normal":
            seat = hospital.normal
        elif bedtype == "hicu":
            seat = hospital.hicu
        elif bedtype == "icu":
            seat = hospital.icu
        elif bedtype == "ventilator":
            seat = hospital.ventilator
        else:
            flash("Invalid bed type selected.", "danger")
            return render_template("booking.html", query1=hospitals,query=hospitals)

        # Check seat availability
        if seat <= 0:
            flash("No available beds of selected type.", "danger")
            return render_template("booking.html", query1=hospitals,query=hospitals)

        # Deduct one seat and update DB
        if bedtype == "normal":
            hospital.normal -= 1
        elif bedtype == "hicu":
            hospital.hicu -= 1
        elif bedtype == "icu":
            hospital.icu -= 1
        elif bedtype == "ventilator":
            hospital.ventilator -= 1

        db.session.commit()

        # Create booking entry
        booking = Bookingpatients(
            srfid=srfid,
            bedtype=bedtype,
            hcode=hcode,
            spo2=spo2,
            pname=pname,
            phone=phone,
            address=address
        )
        db.session.add(booking)
        db.session.commit()

        flash("Bed booked successfully! Visit the hospital for further procedure.", "success")
        return render_template("booking.html", query1=hospitals,query=hospitals)

    # GET request — render the booking page
    return render_template("booking.html", query1=hospitals,query=hospitals)



@app.route("/details",methods=['GET'])
def details():
    srfid = current_user.srfid
    dbb = Bookingpatients.query.filter_by(srfid = srfid).first()
    return render_template("details.html",data=dbb)
 

@app.route("/trigger")
def trigger():
     query = Trigger_log.query.all()
     return render_template("trigger.html",query=query)

@app.route("/patients")
def patients():
     query = Bookingpatients.query.all()
     return render_template("patients.html",query=query)
app.run(debug=True)