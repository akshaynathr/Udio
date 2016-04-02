# module contains all general views 
import os
import json
from flask import request,render_template,g,redirect,session,url_for,flash
from app import application as app
from app.model import create_connection, close_connection
from rethinkdb.errors import RqlRuntimeError,RqlDriverError
import rethinkdb as r
from app.configuration import RDB_PORT,UDIO_DB,RDB_HOST



APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/tmp/')
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

@app.route('/',methods=['GET','POST'])
@app.route('/home',methods=['GET','POST'])
def home():
        if request.method=='GET':
            title="Welcome to Udio"
            return render_template('home/udio.html',title=title)
        if request.method=='POST':
            return redirect(url_for('login'),code=307)

@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT,db=UDIO_DB)
    except RqlDriverError:
        abort(503, "Database connection could not be established.")

@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
         if 'user' in session:
             return redirect(url_for('dashboard'))
         else:
            return render_template('main/login.html')
    elif request.method=='POST':
         username=request.form['username']
         password=request.form['password']
         if username == '' or password=='':
             flash('enter valid username or password')
             return render_template('main/login.html')
         user=list(r.db('udio').table('users').filter(r.row['username']==username ).run(g.rdb_conn))
         count=r.db('udio').table('users').filter(r.row['username']==username and r.row['password']==password).count().run(g.rdb_conn)
         if count >0:
             access=1
         else:
             access=0
         if access==0:
             return "authentication error"
         else:
             session['user']=user
             return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    session.pop('user',None)
    flash("Logged out")
    return redirect(url_for('login'))

@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    if request.method=='GET':
        if 'user' not in session:
            flash('Please Login')
            return redirect(url_for('login'))
        username=session['user'][0]['username']
        password=session['user'][0]['password']
        name=''
        print("Username:")
        print(username)
        user=list(r.db('udio').table('users').filter(r.row['username']==username ).run(g.rdb_conn))
        name=user[0]['firstname']+user[0]['lastname']
        image_path=user[0]['image_path']
        print "Image Path"
        print image_path
        return render_template('admin/select_ride.html',name=name,img=image_path)
    if request.method=='POST':
        to_place=request.form['to_place']
        from_place=request.form['from_place']
        date=request.form['date']
        return redirect(url_for('find_rider',to_place=to_place,from_place=from_place,__date__=date))

@app.route('/find_rider/<to_place>/<from_place>/<__date__>')
def find_rider(from_place,to_place,__date__):
    print (from_place)
    print (to_place)
    riders=list(r.db('udio').table('rides').filter(r.row['from_place']==from_place and r.row['to_place']==to_place and r.row['date']==__date__).order_by(r.desc('date')).run(g.rdb_conn))
    return render_template('admin/ride_list.html',riders=riders,name=session['user'][0]['firstname']+session['user'][0]['lastname'],img=session['user'][0]['image_path'])
    
   
@app.route('/session')
def session_view():
    sess=session['user']
    return json.dumps(sess)


@app.route('/delivery',methods=['GET','POST'])
def delivery():
    return render_template("admin/delivery.html",name=session['user'][0]['firstname']+session['user'][0]['lastname'],img=session['user'][0]['image_path'])

@app.route('/tripplan',methods=['GET','POST'])
def tripplan():
    if request.method=='GET':
        if 'user' in session:
            name=session['user'][0]['firstname']+session['user'][0]['lastname']

            return render_template('admin/tripplan.html',name=name,img=session['user'][0]['image_path'],)
        else:
            return redirect(url_for('login'))
    if request.method=='POST':
        to_place=request.form['to_place']
        from_place=request.form['from_place']
        date=request.form['date']
        vehicle=request.form['vehicle']
        extra_info=request.form['extra_info']
        time=request.form['time']
        conn=create_connection()
        ride=list(r.db('udio').table('rides').insert([ {
                        'to_place':to_place,
                        'licence':session['user'][0]['licence'],
                        'from_place':from_place,
                        'date':date,
                        'time':time,
                        'vehicle':vehicle,
                        'extra_info':extra_info,
                        'availability':0,
                        'done':0,
                        'created_date':r.now(),
                        'rider_id':session['user'][0]['id'],
                        'email':session['user'][0]['email'],
                        'name':session['user'][0]['firstname']+session['user'][0]['lastname'],
                        'review':0

                        }]).run(g.rdb_conn,time_format="raw"))
        return json.dumps(ride)

        return render_template('admin/ride_created.html',riders=ride[0],name=session['user'][0]['firstname']+session['user'][0]['lastname'],img=session['user'][0]['image_path'])




@app.route('/ride_request',methods=['POST'])
def ride_request():
    sender_id=session['user'][0]['id']
    ride_id=request.form['rider_id']
    return "Ride request"


@app.route('/add_location',methods=['POST'])
def add_location():
    ride_id=request.form['ride_id']
    lat=request.form['lat']
    lon=request.form['lon']
    ride=r.db('udio').table('rides').filter({'id':ride_id}).insert([{'lat':lat, 'lon':lon}]).run(g.rdb_conn)
    return  "locations added"




@app.route('/consignments',methods=['GET','POST'])
def consignments():
    if request.method=='GET':
        rides=list(r.db('udio').table('rides').filter({'id':session['user'][0]['id'] }).run(g.rdb_conn))
        return render_template('admin/consignments.html',name=session['user'][0]['firstname']+session['user'][0]['lastname'] ,img=session['user'][0]['image_path'])
    if request.method=='POST':
        return "consignments"


