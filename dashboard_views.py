from app import application as dashboard
from flask import render_template,request,session


@dashboard.route('/dashboard')
def dashboard_view():
    if True :
        return render_template('admin/admin.html')
    return "You are not logged in"

@dashboard.route('/consignments')
def consignments():
    return render_template('admin/consignments.html')

@dashboard.route('/checkpoint')
def checkpoint():
    return render_template('checkpoint.html')

@dashboard.route('/delivery')
def delivery():
    return render_template('admin/delivery_history.html')

