# module contains all general views 
import json
from flask import request,render_template,g,redirect,session,url_for,flash
from app import application as app
from app.model import create_connection, close_connection
from rethinkdb.errors import RqlRuntimeError,RqlDriverError
import rethinkdb as r
from app.configuration import RDB_PORT,UDIO_DB,RDB_HOST

@app.route('/',methods=['GET'])
@app.route('/home',methods=['GET'])
def home():
        title="Welcome to Udio"
        form=To_From_Form()
        to=form.to.data
        return render_template('index.html',title=title,form=form)

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
         return render_template('main/login.html')
    elif request.method=='POST':
         
         username=request.form['username']
         password=request.form['password']
         if username == '' or password=='':
             flash('enter valid username or password')
             return render_template('main/login.html')
         user=list(r.db('udio').table('users').filter(r.row['username']==username and r.row['password']==password).run(g.rdb_conn))
         count=r.db('udio').table('users').filter(r.row['username']==username and r.row['password']==password).count().run(g.rdb_conn)
         session['user']=user
         if count >0:
             access=1
         else:
             access=0
         if access==0:
             return "authentication error"
         else:
             return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    username=session['user'][0]['username']
    password=session['user'][0]['password']
    name=''
    if request.method=='GET':
        user=list(r.db('udio').table('users').filter(r.row['username']==username and r.row['password']==password).run(g.rdb_conn))
        name=user[0]['firstname']+user[0]['lastname']
        return render_template('admin/select_ride.html',name=name)
    if request.method=='POST':
        to_place=request.form['to_place']
        from_place=request.form['from_place']
        return redirect(url_for('find_rider',to_place=to_place,from_place=from_place))

@app.route('/find_rider/<to_place>/<from_place>')
def find_rider(from_place,to_place):

    print (from_place)
    print (to_place)
    riders=list(r.db('udio').table('rides').filter(r.row['from_place']==from_place and r.row['to_place']==to_place).run(g.rdb_conn))
    return render_template('admin/ride_list.html',riders=riders,name="Akshaynathr")
    
   
@app.route('/session')
def session_view():
    sess=session['user']
    return json.dumps(sess)



@app.route('/tripplan',methods=['GET','POST'])
def tripplan():
    if request.method=='GET':
        if 'user' in session:
            name=session['user'][0]['firstname']+session['user'][0]['lastname']

            return render_template('admin/tripplan.html',name=name)
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
        ride=r.db('udio').table('rides').insert([ {
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
                        'name':session['user'][0]['firstname']+session['user'][0]['secondname']
                        }]).run(g.rdb_conn)
        return "Ride created"




@app.route('/ride_request',methods=['POST'])
def ride_request():
    sender_id=session['user'][0]['id']
    ride_id=request.form['rider_id']
    return "Ride request"

