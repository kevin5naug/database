#Import Flask Library
from flask import Flask, Markup, render_template, request, session, url_for, redirect
import pymysql.cursors
import MySQLdb
import hashlib
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
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
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
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
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
        session['booking_agent_id']=get_agent_info(email)
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
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
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
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
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
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

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
        query='select IFNULL(MAX(booking_agent_id),0) as booking_agent_id from booking_agent'
        cursor.execute(query)
        data=cursor.fetchone()
        booking_agent_id=int(data['booking_agent_id'])+1
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
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
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
        try:
            cursor.execute(ins, (email, password, first_name, last_name, date_of_birth, airline_name))
            conn.commit()
            cursor.close()
        except Exception as e:
            return render_template('register.html', error=e)
        return render_template('front_page.html')

@app.route('/log_out')
def log_out():
    session.clear()
    return   render_template('front_page.html')

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

@app.route('/booking_agent_home')
def booking_agent_home():
    if not check_agent_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))

    email=session['email']
    agent_id=session['booking_agent_id']
    flight_info=get_agent_upflight(email)
    error=None
    if(flight_info):
        return render_template('agent_home.html',agent_id=agent_id,results=flight_info,error=error)
    else:
        error='No upcoming flight scheduled in 30 days'
        return render_template('agent_home.html',agent_id=agent_id,results=flight_info,error=error)

@app.route('/searchFlightsAgent',methods=['GET','POST'])
def searchFlightsAgent():
    
    if not check_agent_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
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
    having seats_left>0
    '''
    cursor.execute(query,(d_airport,a_airport,date))
    flight_info=cursor.fetchall()
    cursor.close()
    error=None
    if (flight_info):
        return render_template('agent_search_flights.html',results=flight_info,error=error)
    else:
        error='No flights available'
        return render_template('agent_search_flights.html',results=flight_info,error=error)

@app.route('/agent_purchase_page/<airline_name>/<flight_num>/<int:seats_left>', methods=['GET','POST'])
def agent_purchase_page(airline_name,flight_num,seats_left):
    
    if not check_agent_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))

    return render_template('agent_purchase_page.html',airline_name=airline_name,flight_num=flight_num,seats_left=seats_left)

@app.route('/agent_purchase/<airline_name>/<flight_num>/<int:seats_left>',methods=['GET','POST'])
def agent_purchase(airline_name,flight_num,seats_left):

    if not check_agent_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    customer_email = request.form['customer_email']
    agent_email=session['email']
    cursor=conn.cursor()
    message=None
    query='''select *
    from customer
    where email=%s
    '''
    cursor.execute(query, (customer_email,))
    data=cursor.fetchone()
    if (not data):
        return render_template('agent_purchase_finish.html', message='Purchase fails. Customer email address not registered.')
    agent_id=session['booking_agent_id']
    if (seats_left>0):
        query='select IFNULL(MAX(ticket_id),0) as ticket_id from ticket'
        cursor.execute(query)
        data=cursor.fetchone()
        new_id=int(data['ticket_id'])+1
        query='insert into ticket values(%s, %s, %s)'
        cursor.execute(query,(new_id, airline_name, flight_num))
        query='insert into purchases(ticket_id,customer_email,booking_agent_id,purchase_date) values(%s, %s, %s, CURDATE())'
        cursor.execute(query,(new_id,customer_email,agent_id))
        conn.commit()
        cursor.close()
        message='Purchase Succeeds.'
        return render_template('agent_purchase_finish.html',message=message)
    else:
        message='Purchase fails. There is no seat left.'
        return render_template('agent_purchase_finish.html',message=message)

@app.route('/agent_commission', methods=['GET','POST'])
def agent_commission():

    if not check_agent_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    agent_email=session['email']
    agent_id=session['booking_agent_id']
    cursor=conn.cursor()
    query='''select coalesce(SUM(price),0)/10 as total_commission
            from flight natural join ticket natural join purchases
            where purchases.booking_agent_id=%s
            and (date(purchase_date) between (CURDATE()-INTERVAL 30 DAY) and CURDATE())
            '''
    cursor.execute(query,(agent_id,))
    data=cursor.fetchone()
    total_commission=int(data['total_commission'])
    query='''select count(purchases.ticket_id) as total_num
            from ticket natural join flight natural join purchases
            where purchases.booking_agent_id=%s
            and (date(purchase_date) between (CURDATE()-INTERVAL 30 DAY) and CURDATE())
        '''
    cursor.execute(query,(agent_id,))
    data=cursor.fetchone()
    total_num=int(data['total_num'])
    if (total_num==0):
        average=0
    else:
        average=total_commission/total_num
    cursor.close()
    return render_template('agent_view_commission.html',total_commission=total_commission,total_num=total_num,average=average,history_commission="")

@app.route('/check_commission',methods=['GET','POST'])
def check_commission():

    if not check_agent_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    agent_email=session['email']
    agent_id=session['booking_agent_id']
    start_date=request.form['start']
    end_date=request.form['end']
    cursor=conn.cursor()
    query='''select coalesce(SUM(price),0)/10 as total_commission
            from flight natural join ticket natural join purchases
            where purchases.booking_agent_id=%s
            and (date(purchase_date) between (CURDATE()-INTERVAL 30 DAY) and CURDATE())
            '''
    cursor.execute(query,(agent_id,))
    data=cursor.fetchone()
    total_commission=int(data['total_commission'])
    query='''select count(purchases.ticket_id) as total_num
            from ticket natural join flight natural join purchases
            where purchases.booking_agent_id=%s
            and (date(purchase_date) between (CURDATE()-INTERVAL 30 DAY) and CURDATE())
        '''
    cursor.execute(query,(agent_id,))
    data=cursor.fetchone()
    total_num=int(data['total_num'])
    if (total_num==0):
        average=0
    else:
        average=total_commission/total_num
    query='''select coalesce(SUM(price),0)/10 as total_commission
            from flight natural join ticket natural join purchases
            where purchases.booking_agent_id=%s
            and purchase_date between %s and %s
            '''
    cursor.execute(query,(agent_id, start_date, end_date))
    data=cursor.fetchone()
    history_commission="My history commission from "+str(start_date)+" to "+str(end_date)+": "+str(data['total_commission'])
    cursor.close()
    return render_template('agent_view_commission.html',total_commission=total_commission,total_num=total_num,average=average,history_commission=history_commission)

@app.route('/top_tickets')
def top_tickets():

    if not check_agent_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    email=session['email']
    agent_id=session['booking_agent_id']
    cursor=conn.cursor()
    query='''select customer.email AS email, count(purchases.ticket_id) AS ticket_num
            from customer
            left join purchases on customer.email=purchases.customer_email
            where purchases.booking_agent_id=%s and (date(purchases.purchase_date) between (CURDATE() - INTERVAL 6 MONTH) AND CURDATE())
            group by customer.email 
            ORDER BY ticket_num DESC
        '''
    cursor.execute(query,(agent_id,))
    data=cursor.fetchall()
    i=0
    top5s = [("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0)]
    if(data):
        for item in data:
            if(i<5):
                top5s[i]=(item['email'], int(item['ticket_num']))
                i=i+1
            else:
                break

    query='''select customer.email AS email, coalesce(sum(price)/10,0) as total_commission
            from customer
            left join (purchases natural join ticket natural join flight) on customer.email=purchases.customer_email 
            where purchases.booking_agent_id=%s and (date(purchases.purchase_date) between (CURDATE() - INTERVAL 1 YEAR) AND CURDATE())
            group by customer.email
            order by total_commission DESC
    '''
    cursor.execute(query,(agent_id,))
    data=cursor.fetchall()
    i=0
    top5commission = [("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0)]
    if(data):
        for item in data:
            if(i<5):
                top5commission[i]=(item['email'], int(item['total_commission']))
                i=i+1
            else:
                break
    cursor.close()
    return render_template('agent_tops.html',top5s=top5s,top5commission=top5commission)

@app.route('/customer_home')
def customer_home():

    if not check_customer_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
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

    if not check_customer_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
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
    cursor=conn.cursor()
    
    query='''select F.airline_name, F.flight_num, F.departure_airport, F.departure_time, F.arrival_airport, F.arrival_time, F.price, F.airplane_id, (AI.seats - (select count(*) from ticket as T where T.airline_name=F.airline_name and T.flight_num=F.flight_num)) as seats_left
    from flight as F, airport as D, airport as A, airplane as AI
    where F.departure_airport like %s
    and F.arrival_airport like %s
    and F.departure_airport=D.airport_name
    and D.airport_city like %s
    and F.arrival_airport=A.airport_name
    and A.airport_city like %s
    and F.airplane_id=AI.airplane_id
    and ((date(F.arrival_time)=%s)
    or (date(F.departure_time)=%s))'''
    cursor.execute(query, (source_airport, destination_airport, source_city, destination_city, date, date))
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

    if not check_customer_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
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

    if not check_customer_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
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
    months_spending=[]
    months_label=[]
    for i in range(6,0,-1):
        cursor.execute(query,(email,i,i-1))
        data=cursor.fetchone()
        months_spending.append(int(data['month_spend']))
        months_label.append(str(i)+" month ago")
    cursor.close()
    print(months_spending, months_label)
    upperbound=max(months_spending)
    return render_template('customer_spending_script.html', max=upperbound, year_spending=year_spending, labels=months_label, values=months_spending)

@app.route('/rangeSpending',methods=['GET','POST'])
def rangeSpending():

    if not check_customer_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    
    email=session['email']
    cursor=conn.cursor()
    start_date=request.form['start_date']
    end_date=request.form['end_date']
    query='''select COALESCE(SUM(flight.price),0) as spendings
            from ticket natural join purchases natural join flight
            where purchases.customer_email=%s
            and (date(purchase_date) >= date(%s))
            and (date(purchase_date) <= date(%s))
    '''
    cursor.execute(query,(email,start_date,end_date))
    data=cursor.fetchone()
    range_spending=int(data['spendings'])
    query='''select DATE_FORMAT(purchase_date, '%%m-%%Y') as y_m, COALESCE(SUM(price),0) as spendings 
            from ticket natural join purchases natural join flight
            where purchases.customer_email=%s
            and (date(purchase_date) >= date(%s))
            and (date(purchase_date) <= date(%s))
            GROUP BY DATE_FORMAT(purchase_date, '%%m-%%Y')
        '''
    cursor.execute(query,(email,start_date,end_date))
    data=cursor.fetchall()
    labels=[]
    values=[]
    for item in data:
        labels.append(item['y_m'])
        values.append(int(item['spendings']))
    upperbound=max(values)
    return render_template('customer_spending_custom.html',s_date=start_date,e_date=end_date,max=upperbound,range_spending=range_spending,labels=labels,values=values)
    

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

@app.route('/staff_create_flight')
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
        cursor=conn.cursor()
        ins='insert into flight values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        try:
            cursor.execute(ins, (airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id))
            conn.commit()
            cursor.close()
        except Exception as e:
            return render_template('staff_create_flight.html', username=username, results=None, error=e, message=None)
        results=staff_get_future_flight_info(airline_name)
        return render_template('staff_create_flight.html', username=username, results=results, error=None, message="Success: the flight has been added to the system")

@app.route('/staff_change_flight_status')
def staff_change_flight_status():

    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))

    username=session['username']
    message=None
    error=None
    return render_template('staff_change_flight_status.html', username=username, message=None, error=None)

@app.route('/staff_update_flight_status', methods=['GET', 'POST'])
def staff_update_flight_status():

    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))

    username=session['username']
    airline_name=session['airline_name']
    flight_num=request.form['flight_num']
    new_status=request.form['flight_status']

    cursor=conn.cursor()
    query='''select * 
    from flight
    where airline_name=%s
    and flight_num=%s
    '''
    cursor.execute(query, (airline_name, flight_num))
    data=cursor.fetchone()
    if(not data):
        return render_template('staff_change_flight_status.html', username=username, message=None, error="Failure: No such flight found.")

    query='''update flight 
    set status=%s
    where airline_name=%s
    and flight_num=%s
    '''
    try:
        cursor.execute(query, (new_status, airline_name, flight_num))
        conn.commit()
        cursor.close()
    except Exception as e:
        return render_template('staff_change_flight_status.html', username=username, message=None, error=e)
    
    return render_template('staff_change_flight_status.html', username=username, message="Success: Flight Status Updated.", error=None)

@app.route('/staff_add_airplane_in_system')
def staff_add_airplane_in_system():

    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))

    username=session['username']
    message=None
    error=None
    return render_template('staff_add_airplane_in_system.html', username=username, message=None, error=None)

@app.route('/staff_insert_airplane', methods=['GET', 'POST'])
def staff_insert_airplane():

    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))

    username=session['username']
    airline_name=session['airline_name']
    airplane_id=request.form['airplane_id']
    seats=request.form['seats']
    message=None
    error=None
    query='''insert into airplane values(%s, %s, %s)'''
    cursor=conn.cursor()
    try:
        cursor.execute(query, (airline_name, airplane_id, seats))
        conn.commit()
        cursor.close()
    except Exception as e:
        return render_template('staff_add_airplane_in_system.html', username=username, message=None, error=e)
    message="Success: the airplane has been added to the system."
    return render_template('staff_add_airplane_in_system.html', username=username, message=message, error=None)


@app.route('/staff_add_airport')
def staff_add_airport():

    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))

    username=session['username']
    message=None
    error=None
    return render_template('staff_add_airport.html', username=username, message=None, error=None)

@app.route('/staff_insert_airport', methods=['GET', 'POST'])
def staff_insert_airport():

    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))

    username=session['username']
    airport_name=request.form['airport_name']
    airport_city=request.form['airport_city']
    message=None
    error=None
    query='''insert into airport values(%s, %s)'''
    cursor=conn.cursor()
    try:
        cursor.execute(query, (airport_name, airport_city))
        conn.commit()
        cursor.close()
    except Exception as e:
        return render_template('staff_add_airport.html', username=username, message=None, error=e)
    message="Success: this airport has been added to the system."
    return render_template('staff_add_airport.html', username=username, message=message, error=None)

@app.route('/staff_view_top_booking_agents')
def staff_view_top_booking_agents():
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
 
    airline_name=session['airline_name']
    cursor=conn.cursor()
    query='''select B.email as email, count(P.ticket_id) as ticket_sales
    from booking_agent as B, purchases as P, ticket as T
    where P.booking_agent_id is not null
    and P.ticket_id=T.ticket_id
    and P.booking_agent_id=B.booking_agent_id
    and (date(purchase_date) between (CURDATE()-INTERVAL 1 Month) and CURDATE())
    and T.airline_name=%s
    group by email
    order by ticket_sales desc
    '''
    cursor.execute(query, (airline_name,))
    data=cursor.fetchall()
    i=0
    top5month = [("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0)]
    if(data):
        for item in data:
            if(i<5):
                top5month[i]=(item['email'], int(item['ticket_sales']))
                i=i+1
            else:
                break
    
    query='''select B.email as email, count(P.ticket_id) as ticket_sales
    from booking_agent as B, purchases as P, ticket as T
    where P.booking_agent_id is not null 
    and P.ticket_id=T.ticket_id
    and P.booking_agent_id=B.booking_agent_id
    and (date(purchase_date) between (CURDATE()-INTERVAL 1 Year) and CURDATE())
    and T.airline_name=%s
    group by email
    order by ticket_sales desc
    '''
    cursor.execute(query, (airline_name,))
    data=cursor.fetchall()
    i=0
    top5year = [("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0)]
    if(data):
        for item in data:
            if(i<5):
                top5year[i]=(item['email'], int(item['ticket_sales']))
                i=i+1
            else:
                break
    
    query='''select email, coalesce(sum(price)/10, 0) as total_commission
    from booking_agent left join (purchases natural join ticket natural join flight)
    on booking_agent.booking_agent_id=purchases.booking_agent_id
    where purchases.booking_agent_id is not null
    and (date(purchase_date) between (CURDATE()-INTERVAL 1 Year) and CURDATE())
    and airline_name=%s
    group by email
    order by total_commission desc
    '''
    cursor.execute(query, (airline_name,))
    data=cursor.fetchall()
    i=0
    top5commission = [("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0),("Vacant",0)]
    if(data):
        for item in data:
            if(i<5):
                top5commission[i]=(item['email'], int(item['total_commission']))
                i=i+1
            else:
                break
    cursor.close()
    return render_template('staff_view_top_booking_agents.html', top5month=top5month, top5year=top5year, top5commission=top5commission)

@app.route('/staff_view_frequent_customers')
def staff_view_frequent_customers():
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    username=session['username']
    airline_name=session['airline_name']
    cursor=conn.cursor()
    query='''select C.email as email, count(T.ticket_id) as travel_num
    from customer as C, purchases as P, ticket as T, flight as F
    where C.email=P.customer_email
    and P.ticket_id=T.ticket_id
    and T.airline_name=F.airline_name
    and T.flight_num=F.flight_num
    and (date(F.arrival_time) between (CURDATE()-INTERVAL 1 Year) and CURDATE())
    and T.airline_name=%s
    group by email
    order by travel_num desc
    '''
    cursor.execute(query, (airline_name,))
    data=cursor.fetchone()
    print(data)
    cursor.close()
    return render_template('staff_view_frequent_customers.html', username=username, results=data, flight_info=None, error=None, searching=False)

@app.route('/staff_list_customer_flights', methods=['GET', 'POST'])
def staff_list_customer_flights():
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    username=session['username']
    airline_name=session['airline_name']
    email=request.form['email']
    cursor=conn.cursor()
    query='''select F.flight_num, F.departure_airport, F.departure_time, F.arrival_airport, F.arrival_time
    from purchases as P, ticket as T, flight as F
    where P.customer_email=%s
    and P.ticket_id=T.ticket_id
    and T.airline_name=F.airline_name
    and T.flight_num=F.flight_num
    and F.airline_name=%s
    and (date(F.arrival_time) <= CURDATE())
    '''
    cursor.execute(query, (email, airline_name))
    flight_info=cursor.fetchall()
    
    query='''select C.email as email, count(T.ticket_id) as travel_num
    from customer as C, purchases as P, ticket as T, flight as F
    where C.email=P.customer_email
    and P.ticket_id=T.ticket_id
    and F.airline_name=T.airline_name
    and F.flight_num=T.flight_num
    and (date(F.arrival_time) between (CURDATE()-INTERVAL 1 Year) and CURDATE())
    and T.airline_name=%s
    group by email
    order by travel_num desc
    '''
    cursor.execute(query, (airline_name,))
    data=cursor.fetchone()
    cursor.close()
    return render_template('staff_view_frequent_customers.html', username=username, results=data, flight_info=flight_info, error=None, searching=True)

@app.route('/staff_view_report')
def staff_view_report():
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    airline_name=session['airline_name']
    cursor=conn.cursor()
    query='''select COALESCE(count(ticket_id),0) as ticket_sales
             from ticket natural join purchases
             where airline_name=%s 
             and (date(purchase_date) between (CURDATE()-INTERVAl 365 DAY) and CURDATE())
    '''
    cursor.execute(query,(airline_name,))
    data=cursor.fetchone()
    year_sales=int(data['ticket_sales'])
    query='''select COALESCE(count(ticket_id),0) as ticket_sales
            from ticket natural join purchases
            where airline_name=%s
            and (date(purchase_date) > (CURDATE()-INTERVAL %s MONTH))
            and (date(purchase_date) <= (CURDATE()-INTERVAL %s MONTH))
    '''
    months_sales=[]
    months_label=[]
    for i in range(6,0,-1):
        cursor.execute(query,(airline_name,i,i-1))
        data=cursor.fetchone()
        months_sales.append(int(data['ticket_sales']))
        months_label.append(str(i)+" month ago")
    cursor.close()
    print(months_sales, months_label)
    upperbound=max(months_sales)
    return render_template('staff_view_report.html', max=upperbound, year_sales=year_sales, labels=months_label, values=months_sales)

@app.route('/staff_view_report_custom', methods=['GET', 'POST'])
def staff_view_report_custom():
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    airline_name=session['airline_name']
    cursor=conn.cursor()
    start_date=request.form['start_date']
    end_date=request.form['end_date']
    query='''select COALESCE(count(ticket_id),0) as ticket_sales
    from ticket natural join purchases
    where airline_name=%s
    and (date(purchase_date) >=date(%s))
    and (date(purchase_date) <=date(%s))
    '''
    cursor.execute(query,(airline_name, start_date, end_date))
    data=cursor.fetchone()
    range_ticket_sales=int(data['ticket_sales'])
    query='''select DATE_FORMAT(purchase_date, '%%m-%%Y') as y_m, COALESCE(count(ticket_id),0) as ticket_sales
    from ticket natural join purchases
    where airline_name=%s
    and (date(purchase_date)>=date(%s))
    and (date(purchase_date)<=date(%s))
    group by DATE_FORMAT(purchase_date, '%%m-%%Y')
    '''
    cursor.execute(query, (airline_name, start_date, end_date))
    data=cursor.fetchall()
    labels=[]
    values=[]
    for item in data:
        labels.append(item['y_m'])
        values.append(int(item['ticket_sales']))
    upperbound=max(values)
    return render_template('staff_view_report_custom.html', s_date=start_date, e_date=end_date, max=upperbound, range_sales=range_ticket_sales, labels=labels, values=values)

@app.route('/staff_revenue')
def staff_revenue():
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    airline_name=session['airline_name']
    cursor=conn.cursor()
    query='''select COALESCE(SUM(flight.price),0) as revenue
    from ticket natural join purchases natural join flight
    where purchases.booking_agent_id is null
    and flight.airline_name=%s
    and (date(purchase_date) between (CURDATE()-INTERVAL 1 Year) and CURDATE())
    '''
    cursor.execute(query,(airline_name,))
    data=cursor.fetchone()
    direct_sales_year=int(data['revenue'])
    query='''select COALESCE(SUM(flight.price),0)/10*9 as revenue
    from ticket natural join purchases natural join flight
    where purchases.booking_agent_id is not null
    and flight.airline_name=%s
    and (date(purchase_date) between (CURDATE()-INTERVAL 1 Year) and CURDATE())
    '''
    cursor.execute(query,(airline_name,))
    data=cursor.fetchone()
    indirect_sales_year=int(data['revenue'])
    query='''select COALESCE(SUM(flight.price),0) as revenue
    from ticket natural join purchases natural join flight
    where purchases.booking_agent_id is null
    and flight.airline_name=%s
    and (date(purchase_date) between (CURDATE()-INTERVAL 1 Month) and CURDATE())
    '''
    cursor.execute(query,(airline_name))
    data=cursor.fetchone()
    direct_sales_month=int(data['revenue'])
    query='''select COALESCE(SUM(flight.price),0)/10*9 as revenue
    from ticket natural join purchases natural join flight
    where purchases.booking_agent_id is not null
    and flight.airline_name=%s
    and (date(purchase_date) between (CURDATE()-INTERVAL 1 Month) and CURDATE())
    '''
    cursor.execute(query,(airline_name,))
    data=cursor.fetchone()
    indirect_sales_month=int(data['revenue'])
    cursor.close()
    labels=['direct_sales', 'indirect_sales']
    values_year=[direct_sales_year, indirect_sales_year]
    values_month=[direct_sales_month, indirect_sales_month]
    colors=["#F7464A", "#46BFBD"]
    print(values_year, values_month)
    return render_template('staff_revenue_script.html', set1=zip(values_month, labels, colors), set2=zip(values_year, labels, colors))

@app.route('/staff_view_top_destinations')
def staff_view_top_destinations():
    if not check_staff_authorization(session):
        error='You are not authorized as an airline staff to perform such action.'
        return redirect(url_for('universal_logout'))
    airline_name=session['airline_name']
    cursor=conn.cursor()
    query='''select A.airport_city as destination, count(T.ticket_id) as visit_num
    from purchases as P, ticket as T, flight as F, airport as A
    where P.ticket_id=T.ticket_id
    and (date(F.arrival_time) between (CURDATE()-INTERVAL 3 Month) and CURDATE())
    and T.airline_name=F.airline_name
    and T.airline_name=%s
    and T.flight_num=F.flight_num
    and F.arrival_airport=A.airport_name
    group by destination
    order by visit_num desc
    '''
    cursor.execute(query,(airline_name,))
    data=cursor.fetchall()
    i=0
    top3=[("vacant",0), ("Vacant",0), ("vacant",0)]
    if(data):
        for item in data:
            if(i<3):
                top3[i]=(item['destination'], item['visit_num'])
                i=i+1
            else:
                break
    query='''select A.airport_city as destination, count(T.ticket_id) as visit_num
    from purchases as P, ticket as T, flight as F, airport as A
    where P.ticket_id=T.ticket_id
    and (date(F.arrival_time) between (CURDATE()-INTERVAL 1 Year) and CURDATE())
    and T.airline_name=F.airline_name
    and T.airline_name=%s
    and T.flight_num=F.flight_num
    and F.arrival_airport=A.airport_name
    group by destination
    order by visit_num desc
    '''
    cursor.execute(query,(airline_name,))
    data=cursor.fetchall()
    i=0
    top3_year=[("vacant",0), ("Vacant",0), ("vacant",0)]
    if(data):
        for item in data:
            if(i<3):
                top3_year[i]=(item['destination'], item['visit_num'])
                i=i+1
            else:
                break
    cursor.close()
    return render_template('staff_view_top_destinations.html', top3=top3, top3year=top3_year)

@app.route('/staff_logout')
def staff_logout():
    session.pop('username')
    session.pop('first_name')
    session.pop('last_name')
    session.pop('airline_name')
    return redirect('/')

@app.route('/universal_logout')
def universal_logout():
    session.clear()
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

def check_customer_authorization(session):
    if('email' not in session.keys()):
        return False
    if('name' not in session.keys()):
        return False
    email=session['email']
    name=session['name']
    cursor=conn.cursor()
    query='select * from customer where email=%s and name=%s'
    cursor.execute(query, (email, name))
    info=cursor.fetchone()
    cursor.close()
    if(info):
        return True
    else:
        return False

def check_agent_authorization(session):
    if('booking_agent_id' not in session.keys()):
        return False
    if('email' not in session.keys()):
        return False
    email=session['email']
    booking_agent_id=session['booking_agent_id']
    cursor=conn.cursor()
    query='select * from booking_agent where email=%s and booking_agent_id=%s'
    cursor.execute(query, (email, booking_agent_id))
    info=cursor.fetchone()
    cursor.close()
    if(info):
        return True
    else:
        return False

def check_staff_authorization(session):
    if('airline_name' not in session.keys()):
        return False
    if('username' not in session.keys()):
        return False
    else:
        username=session['username']
        airline_name=session['airline_name']
        cursor=conn.cursor()
        query='select * from airline_staff where username=%s and airline_name=%s'
        cursor.execute(query, (username, airline_name))
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

def get_agent_info(email):
    cursor=conn.cursor()
    query='select booking_agent_id from booking_agent where email=%s'
    cursor.execute(query,(email,))
    info=cursor.fetchone()
    cursor.close()
    error=None
    if(info):
        return info['booking_agent_id']
    else:
        print("ERROR: booking agent doesn't exist")
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

def get_agent_upflight(email):
    cursor=conn.cursor()
    query='''select customer_email, airline_name,flight_num,departure_airport,departure_time,arrival_airport,arrival_time,price,status,airplane_id
            from purchases natural join ticket natural join flight natural join booking_agent 
            where booking_agent.email=%s
            and ((date(departure_time) between CURDATE() and (CURDATE()+ INTERVAL 30 DAY)) 
    or (date(arrival_time) between CURDATE() and (CURDATE()+ INTERVAL 30 DAY)))
        '''
    cursor.execute(query,(email,))
    flight_info=cursor.fetchall();
    cursor.close()
    return flight_info

#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
