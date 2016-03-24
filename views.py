# module contains all general views 

from flask import request,render_template,g,redirect,session,url_for
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
         session['username']=user
         if count >0:
             access=1
         else:
             access=0
         if access==0:
             return "authentication error"
         else:
             return redirect(url_for('dashboard',username=username,password=password))

@app.route('/logout')
def logout():
    print session['username'] 
    return render_template('main/login.html')

@app.route('/dashboard/<username>/<password>',methods=['POST','GET'])
def dashboard(username,password):
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
def find_rider(to_place,from_place):
    riders=list(r.db('udio').table('rides').filter(r.row['from_place']==from_place and r.row['to_place']==to_place).run(g.rdb_conn))
    return render_template('admin/profile.html',riders=riders,name="Akshaynathr")
    
     
