#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='192.168.64.2',
                       user='user',
                       password='',
                       db='blog',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('front_page.html')

#Define route for customer login
@app.route('/login_customer')
def login():
    return render_template('login_customer.html')

#Define route for booking agent login
@app.route('/login_agent')
def login():
    return render_template('login_agent.html')

#Define route for login
@app.route('/login_staff')
def login():
    return render_template('login_staff.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuthCustomer', methods=['GET', 'POST'])
def loginAuthCustomer():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s and password = %s'
    cursor.execute(query, (email, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
	#creates a session for the the user
	#session is a built in
	session['email'] = email
	return redirect(url_for('customer_home'))
    else:
	#returns an error message to the html page
	error = 'Invalid login or username'
	return render_template('login_customer.html', error=error)

#Authenticates the login
@app.route('/loginAuthAgent', methods=['GET', 'POST'])
def loginAuthAgent():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s'
    cursor.execute(query, (email, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
	#creates a session for the the user
	#session is a built in
	session['email'] = email
	return redirect(url_for('booking_agent_home'))
    else:
	#returns an error message to the html page
	error = 'Invalid login or username'
	return render_template('login_agent.html', error=error)
    #Authenticates the login

@app.route('/loginAuthStaff', methods=['GET', 'POST'])
def loginAuthStaff():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
	#creates a session for the the user
	#session is a built in
	session['username'] = username
	return redirect(url_for('airline_staff_home'))
    else:
	#returns an error message to the html page
	error = 'Invalid login or username'
	return render_template('login_staff.html', error=error)

#Authenticates Customer Registration
@app.route('/registerCustomer', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    email=request.form['email']
    name=request.form['name']
    password=request.form['password']
    building_number=request.form['building_number']
    street=request.form['street']
    city=request.form['city']
    state=request.form['state']
    phone_number=request.form['phone_number']
    passport_number=request.form['passport_number']
    passport_expiration=request.form['passport_expiration']
    passport_country=request.form['passport_country']
    date_of_birth=request.form['date_of_birth']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email,))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This email address has already been registered by a customer"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
        conn.commit()
        cursor.close()
        return render_template('front_page.html')

#Authenticates Booking Agent Registration
@app.route('/registerBookingAgent', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    email=request.form['email']
    password=request.form['password']
    booking_agent_id=request.form['booking_agent_id']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM booking_agent WHERE email = %s'
    cursor.execute(query, (email,))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This email address has already been registered by a booking agent"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO booking_agent VALUES(%s, %s, %s)'
        cursor.execute(ins, (email, password, booking_agent_id))
        conn.commit()
        cursor.close()
        return render_template('front_page.html')

#Authenticates Airline Staff Registration
@app.route('/registerAirlineStaff', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    email=request.form['username']
    password=request.form['password']
    first_name=request.form['first_name']
    last_name=request.form['last_name']
    date_of_birth=request.form['date_of_birth']
    airline_name=request.form['airline_name']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (email,))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This username has already been registered by an airline staff member"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, password, first_name, last_name, date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        return render_template('front_page.html')

@app.route('/airline_staff_home')
def airline_staff_home():
    username=session['username']
    first_name, last_name, airline_name=get_airline_staff_info(username)
    return render_template('airline_staff_home.html', username=username, flight_info=data)
	
@app.route('/logout_staff')
def logout():
    session.pop('username')
    return redirect('/')

app.secret_key = 'some key that you will never guess'

def get_airline_staff_airline_name(username):
    cursor=conn.cursor()
    query='select * from airline_staff where username=%s'
    cursor.execute(query, (username,))
    data=cursor.fetchone

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
