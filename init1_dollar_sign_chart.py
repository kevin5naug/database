#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='192.168.64.2',
                       user='user',
                       password='',
                       db='air_ticket_reservation',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('front_page.html', error=None)

#Define route for customer login
@app.route('/login_customer')
def login_customer():
    return render_template('login_customer.html')

#Define route for booking agent login
@app.route('/login_agent')
def login_agent():
    return render_template('login_agent.html')

#Define route for login
@app.route('/login_staff')
def login_staff():
    return render_template('login_staff.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/view_public_info')
def view_public_info():
    return render_template('view_public_info.html')

@app.route('/check_flight_status', methods=['GET', 'POST'])
def check_flight_status():
    flight_num=request.form['flight_num']
    date=request.form['date']
    cursor=conn.cursor()
    if(flight_num):
        query='''select * 
        from flight as F 
        where F.flight_num=%s 
        and ((date(F.arrival_time)=%s)
        or (date(F.departure_time)=%s))'''
        cursor.execute(query, (flight_num, date, date))
    else:
        query='''select * 
        from flight as F 
        where (date(F.arrival_time)=%s)
        or (date(F.departure_time)=%s)'''
        cursor.execute(query, (date, date))
    data=cursor.fetchall()
    cursor.close()
    error=None
    if(data):
        return render_template('view_public_info.html', error=error, results=data)
    else:
        error = 'No flights found  satisfying your search constraints. Please make sure you input the right flight information'
        return render_template('view_public_info.html', error=error, results=data)

@app.route('/search_upcoming_flights', methods=['GET', 'POST'])
def search_upcoming_flights():
    #grabs information from the forms
    source_city = request.form['source_city']
    source_airport = request.form['source_airport']
    destination_city = request.form['destination_city']
    destination_airport = request.form['destination_airport']
    date=request.form['date'] #required

    #deal with NULL type
    if(source_city is None):
        source_city = ""
    if(source_airport is None):
        source_airport = ""
    if(destination_city is None):
        destination_city = ""
    if(destination_airport is None):
        destination_airport = ""

    source_city="%"+source_city+"%"
    source_airport="%"+source_airport+"%"
    destination_city="%"+destination_city+"%"
    destination_airport="%"+destination_airport+"%"

    #cursor used to send queries
    cursor = conn.cursor()

    query='''select * 
    from flight as F, airport as D, airport as A 
    where F.departure_airport like %s 
    and F.arrival_airport like %s 
    and F.departure_airport=D.airport_name 
    and D.airport_city like %s 
    and F.arrival_airport=A.airport_name 
    and A.airport_city like %s 
    and ((date(F.arrival_time)=%s) 
    or (date(F.departure_time)=%s))'''
    cursor.execute(query, (source_airport, destination_airport, source_city, destination_city, date, date))
    #executes query
    #stores the results in a variable
    data = cursor.fetchall()
    cursor.close()
    error = None
    if(data):
        return render_template('view_public_info.html', error=error, results=data)
    else:
        error = 'No flights found  satisfying your search constraints. Please relax your search criteria'
        return render_template('view_public_info.html', error=error, results=data)

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
        session['name']=get_customer_info(email)
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
        first_name, last_name, airline_name=get_airline_staff_info(username)
        session['first_name'] = first_name
        session['last_name'] = last_name
        session['airline_name'] = airline_name
        return redirect(url_for('staff_home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login_staff.html', error=error)

#Authenticates Customer Registration
@app.route('/registerCustomer', methods=['GET', 'POST'])
def registerCustomer():
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
def registerBookingAgent():
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
def registerAirlineStaff():
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

@app.route('/staff_home')
def staff_home():
    
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    username=session['username']
    first_name=session['first_name']
    last_name=session['last_name']
    airline_name=session['airline_name']
    error=None

    flight_info=staff_get_future_flight_info(airline_name)
    if(flight_info):
        return render_template('staff_home.html', username=username, results=flight_info, error=error)
    else:
        error='No upcoming flight scheduled in 30 days'
        return render_template('staff_home.html', username=username, results=flight_info, error=error)

@app.route('/customer_home')
def customer_home():
        email=session['email']
        name=session['name']

        flight_info=get_customer_upflight(email)
        error=None
        if(flight_info):
            return render_template('customer_home.html',name=name, results=flight_info,error=error)
        else:
            error='No upcoming flight scheduled in 30 days'
            return render_template('customer_home.html',name=name, results=flight_info,error=error)

@app.route('/searchFlightsCustomer', methods=['GET', 'POST'])
def searchFlightsCustomer():
    d_airport=request.form['departure_airport']
    a_airport=request.form['arrival_airport']
    date=request.form['date']
    cursor=conn.cursor()
    
    query='''select F.airline_name, F.flight_num, F.departure_airport, F.departure_time, F.arrival_airport, F.arrival_time, F.price, F.airplane_id, (A.seats - (select count(*) from ticket as T where T.airline_name=F.airline_name and T.flight_num=F.flight_num)) as seats_left  
    from flight as F, airplane as A
    where F.airline_name=A.airline_name
    and F.airplane_id=A.airplane_id
    and departure_airport=%s 
    and arrival_airport=%s
    and (date(arrival_time)=%s)
    group by airline_name, flight_num
    '''
    cursor.execute(query,(d_airport,a_airport,date))
    flight_info=cursor.fetchall()
    cursor.close()
    error=None
    if (flight_info):
        return render_template('customer_search_flights.html',results=flight_info,error=error)
    else:
        error='No flights available'
        return render_template('customer_search_flights.html',results=flight_info,error=error)

@app.route('/customer_purchase/<airline_name>/<flight_num>/<int:seats_left>',methods=['GET','POST'])
def customer_purchase(airline_name,flight_num,seats_left):
    email=session['email']
    cursor=conn.cursor()
    message=None
    if (seats_left>0):
        query='select IFNULL(MAX(ticket_id),0) as ticket_id from ticket'
        cursor.execute(query)
        data=cursor.fetchone()
        new_id=int(data['ticket_id'])+1
        query='insert into ticket values(%s, %s, %s)'
        cursor.execute(query,(new_id, airline_name, flight_num))
        query='insert into purchases(ticket_id,customer_email,purchase_date) values(%s, %s, CURDATE())'
        cursor.execute(query,(new_id,email))
        conn.commit()
        cursor.close()
        message='Purchase Succeeds.'
        return render_template('customer_purchase.html',message=message)
    else:
        message='Purchase fails. There is no seat left.'
        return render_template('customer_purchase.html',message=message)
    
@app.route('/track_customer_spending')
def track_customer_spending():
    email=session['email']
    cursor=conn.cursor()
    query='''select COALESCE(SUM(flight.price),0) as spendings
             from ticket natural join purchases natural join flight
             where purchases.customer_email=%s 
             and (date(purchase_date) between (CURDATE()-INTERVAl 365 DAY) and CURDATE())
    '''
    cursor.execute(query,(email,))
    data=cursor.fetchone()
    year_spending=int(data['spendings'])
    query='''select COALESCE(SUM(flight.price),0) as month_spend
            from ticket natural join purchases natural join flight
            where purchases.customer_email=%s
            and (date(purchase_date) > (CURDATE()-INTERVAL %s MONTH))
            and (date(purchase_date) <= (CURDATE()-INTERVAL %s MONTH))
    '''
    months_data=[]
    for i in range(6,0,-1):
        cursor.execute(query,(email,i,i-1))
        data=cursor.fetchone()
        months_data.append(int(data['month_spend']))
    cursor.close()
    return render_template('customer_spending.html',year_spending=year_spending,months_data=months_data)
    

@app.route('/staff_customize_view')
def staff_customize_view():
    
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    username=session['username']
    flight_info=None
    error=None
    return render_template('staff_customize_view.html', username=username, results=flight_info, error=error)

@app.route('/staff_search_flights', methods=['GET', 'POST'])
def staff_search_flights():
    
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    username=session['username']
    airline_name=session['airline_name']
    start_date=request.form['start_date'] #required
    end_date=request.form['end_date'] #required
    source_city = request.form['source_city']
    source_airport = request.form['source_airport']
    destination_city = request.form['destination_city']
    destination_airport = request.form['destination_airport']
    airline_name=session['airline_name']

    #deal with NULL type
    if(source_city is None):
        source_city = ""
    if(source_airport is None):
        source_airport = ""
    if(destination_city is None):
        destination_city = ""
    if(destination_airport is None):
        destination_airport = ""

    source_city="%"+source_city+"%"
    source_airport="%"+source_airport+"%"
    destination_city="%"+destination_city+"%"
    destination_airport="%"+destination_airport+"%"

    #cursor used to send queries
    cursor = conn.cursor()

    query='''select * 
    from flight as F, airport as D, airport as A 
    where F.airline_name=%s
    and F.departure_airport like %s
    and F.arrival_airport like %s 
    and F.departure_airport=D.airport_name 
    and D.airport_city like %s 
    and F.arrival_airport=A.airport_name 
    and A.airport_city like %s 
    and ((date(F.arrival_time)<=%s)
    or (date(F.departure_time)>=%s))'''
    cursor.execute(query, (airline_name, source_airport, destination_airport, source_city, destination_city, end_date, end_date))
    #executes query
    #stores the results in a variable
    data = cursor.fetchall()
    cursor.close()
    error = None
    if(data):
        return render_template('staff_customize_view.html', username=username, error=error, results=data)
    else:
        error = 'No flights found  satisfying your search constraints. Please relax your search criterion.'
        return render_template('staff_customize_view.html', username=username, error=error, results=data)

@app.route('/staff_customers_on_flight')
def staff_customers_on_flight():
    
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    username=session['username']
    results=None
    error=None
    return render_template('staff_customers_on_flight.html', username=username, results=None, error=None)

@app.route('/staff_list_customers_on_flight', methods=['GET', 'POST'])
def staff_list_customers_on_flight():
    
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    username=session['username']
    airline_name=session['airline_name']
    flight_num=request.form['flight_num']
    
    cursor=conn.cursor()
    query='''select C.email, C.name, C.phone_number
    from flight as F, ticket as T, purchases as P, customer as C
    where F.flight_num=%s
    and F.airline_name=%s
    and F.airline_name=T.airline_name 
    and F.flight_num=T.flight_num
    and T.ticket_id=P.ticket_id
    and P.customer_email=C.email'''
    cursor.execute(query, (flight_num, airline_name))
    data=cursor.fetchall()
    cursor.close()
    error=None
    if(data):
        return render_template('staff_customers_on_flight.html', username=username, results=data, error=error)
    else:
        error='No results found. Either the flight number is wrong or this flight is empty. Please make sure that this flight number indeed represents a flight in your company.'
        return render_template('staff_customers_on_flight.html', username=username, results=data, error=error)

@app.route('/staff_create_flight', methods=['GET', 'POST'])
def staff_create_flight():
    
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    username=session['username']
    first_name=session['first_name']
    last_name=session['last_name']
    airline_name=session['airline_name']
    error=None
    
    flight_info=staff_get_future_flight_info(airline_name)
    if(flight_info):
        return render_template('staff_create_flight.html', username=username, results=flight_info, error=None, message=None)
    else:
        error='No upcoming flight scheduled in 30 days'
        return render_template('staff_create_flight.html', username=username, results=flight_info, error=error, message=None)

@app.route('/staff_add_flight', methods=['GET', 'POST'])
def staff_add_flight():

    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    username=session['username']
    airline_name=session['airline_name']
    flight_num=request.form['flight_num']
    departure_airport=request.form['departure_airport']
    departure_time=request.form['departure_time']
    arrival_airport=request.form['arrival_airport']
    arrival_time=request.form['arrival_time']
    price=request.form['price']
    status=request.form['status']
    airplane_id=request.form['airplane_id']

    if flight_already_exist(airline_name, flight_num):
        results=staff_get_future_flight_info(airline_name)
        error='Sorry. A flight has already used this flight number. Operation Failed.'
        return render_template('staff_create_flight.html', username=username, results=results, error=error, message=None)
    else:
        success=staff_insert_new_flight(airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id)
        if success:
            results=staff_get_future_flight_info(airline_name)
            return render_template('staff_create_flight.html', username=username, results=results, error=None, message="Success: the flight has been added to the system")
        else:
            error='Fail: please provide flight information that is consistent with the current system'
            return render_template('staff_create_flight.html', username=username, results=results, error=error, message=None)

@app.route('/staff_logout')
def staff_logout():
    session.pop('username')
    session.pop('first_name')
    session.pop('last_name')
    session.pop('airline_name')
    return redirect('/')

@app.route('/universal_logout')
def universal_logout():
    for item in session.keys():
        session.pop(item)
    return render_template('front_page.html', error='Unauthorized Access: You are forced to be logged out.')

app.secret_key = 'some key that you will never guess'


#Utility Function
def get_customer_upflight(email):
    cursor=conn.cursor()
    query='''select airline_name,flight_num,departure_airport,departure_time,arrival_airport,arrival_time,price,status,airplane_id 
    from flight natural join ticket natural join purchases
    where purchases.customer_email=%s
    and ((date(departure_time) between CURDATE() and (CURDATE()+ INTERVAL 30 DAY)) 
    or (date(arrival_time) between CURDATE() and (CURDATE()+ INTERVAL 30 DAY)))
    '''
    cursor.execute(query,(email,))
    flight_info=cursor.fetchall();
    cursor.close()
    return flight_info

def staff_insert_new_flight(airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id):
    cursor=conn.cursor()
    
    #TODO: sanitize Input

    ins='insert into flight values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(ins, (airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id))
    conn.commit()
    cursor.close()
    return True

def staff_get_future_flight_info(airline_name):
    cursor=conn.cursor()
    query='''select * 
    from flight 
    where airline_name=%s 
    and ((date(departure_time) between CURDATE() and (CURDATE()+ INTERVAL 30 DAY)) 
    or (date(arrival_time) between CURDATE() and (CURDATE()+INTERVAL 30 DAY)))'''
    cursor.execute(query, (airline_name,))
    flight_info=cursor.fetchall()
    cursor.close()
    return flight_info

def flight_already_exist(airline_name, flight_num):
    cursor=conn.cursor()
    query='''select * 
    from flight
    where airline_name=%s
    and flight_num=%s'''
    cursor.execute(query, (airline_name, flight_num))
    data=cursor.fetchall()
    cursor.close()
    if(data):
        return True
    else:
        return False

def check_staff_authorization(session):
    if('username' not in session.keys()):
        return False
    else:
        username=session['username']
        cursor=conn.cursor()
        query='select * from airline_staff where username=%s'
        cursor.execute(query, (username))
        info=cursor.fetchone()
        cursor.close()
        if(info):
            return True
        else:
            return False

def get_customer_info(email):
    cursor=conn.cursor()
    query='select name from customer where email=%s'
    cursor.execute(query,(email,))
    info=cursor.fetchone()
    cursor.close()
    error=None
    if(info):
        return info['name']
    else:
        print("ERROR: person doesn't exist")
        return "ERROR"

def get_airline_staff_info(username):
    cursor=conn.cursor()
    query='select * from airline_staff where username=%s'
    cursor.execute(query, (username,))
    info=cursor.fetchone()
    cursor.close()
    error=None
    if(info):
        return info['first_name'], info['last_name'], info['airline_name']
    else:
        print("FATAL ERROR: cannot fetch attributes for this airline staff")
        return "ERROR", "ERROR", "ERROR"

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
