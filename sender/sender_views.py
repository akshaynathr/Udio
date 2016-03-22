from app.model import create_connection, close_connection
import rethinkdb as r
from app import application as app
from flask import render_template , request

def check_duplicate(username):
    conn=create_connection()
    count=r.db('udio').table('users').filter({'username':username }).count().run(conn)
    if count > 0:
        return 1
    else:
        return 0

    

@app.route('/find_rider',methods=['GET','POST'])
def find_riderr():
    if request.method=='GET':
        return "find rider"
    if request.method=='POST':
        to=request.form['to']
        from_place=request.form['from_place']
        conn=create_connection()
        data=r.db('UDIO').table('ride').filter({'from':from_place}).run(conn)
        close_connection(conn)
        return data

@app.route('/create_ride',methods=['GET','POST'])
def create_ride(sender_id):
    if request.method=='GET':
        return "create rider"
    if request.method=='POST':
        from_place=request.form['from']
        to=request.form['to']
        conn=create_connection()
        data=r.db('udio').table('rides').insert([
            {
                'sender_id':sender_id,
                'from_place':from_place,
                'to_place':to,
                'date':r.now(),
                'completed':0,
                'rider_id':None

            }]).run(conn)
        close_connection(conn)
        return "rider created"


@app.route('/reg',methods=['GET','POST'])
def sender_reg():
    if request.method=="GET":
        return render_template('main/snp.html')

    if request.method == "POST":
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        address=request.form['address']
        dob=request.form['dob']
        username=request.form['username']
        password=request.form['password']
        country=request.form['country']
        state=request.form['state']
        district=request.form['district']
        pin=request.form['pin']
        mobile=request.form['mobile']
        email=request.form['email']
        conn=create_connection()
        access=check_duplicate(username)
    if access==1:
        return "duplicate error"
    else:
        r.db('udio').table('users').insert([
                { 'firstname':firstname,
                  'lastname':lastname,
                  'address':address,
                  'dob':dob,
                  'username':username,
                  'password':password,
                  'country':country,
                  'state':state,
                  'district':district,
                  'pin':pin,
                  'mobile':mobile,
                  'email':email
                  }
                ]).run(conn)
        close_connection(conn)
        return "User registered"

@app.route('/selectride')
def select_ride():
    from_place=request.form['from']
    to_place=request.form['to']
    if from_place == to_place:
        flash ("Selected places are same")
        return render_template('admin/admin.html')
    else:
        conn=create_connection()
        rides=list(r.db('udio').table('users').filter(r.row['from_place']==from_place and r.row['to_place']==to_place).run(conn))
        conn.close()
        return render_template('admin/rides.html')






