# module contains all general views 

from flask import request,render_template,g
from app import application as app
from rethinkdb.errors import RqlDriverError
import rethinkdb as r
from model import dbSetUp
from app.configuration import RDB_HOST, RDB_PORT ,UDIO_DB
from forms import To_From_Form

dbSetUp()



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



@app.route('/login')
def login():
    return render_template('login.html')



