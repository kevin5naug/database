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
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

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
    date=request.form['date'] #required input

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
        error = 'No flights found  satisfying your search constraints. Please make sure you input the right flight information: flight_number: '+str(flight_number)+' date: '+str(date)
        return render_template('view_public_info.html', error=error, results=data)

@app.route('/search_upcoming_flights', methods=['GET', 'POST'])
def search_public_info():
    #grabs information from the forms
    source_city = request.form['source_city']
    source_airport = request.form['source_airport']
    destination_city = request.form['destination_city']
    destination_airport = request.form['destination_airport']
    date=request.form['date'] #required input

    #deal with NULL type
    if(!source_city):
        source_city = ""
    if(!source_airport):
        source_airport = ""
    if(!destination_city):
        destination_city = ""
    if(!destination_airport):
        destination_airport = ""

    source_city="%"+source_city+"%"
    source_airport="%"+source_airport+"%"
    destination_city="%"+destination_city+"%"
    destination_airport="%"+destination_airport+"%"

    #cursor used to send queries
    cursor = conn.cursor()

    query='select * from flight as F, airport as D, airport as A where F.departure_airport like %s and F.arrival_airport like %s and F.departure_airport=D.airport_name and D.airport_city like %s and F.arrival_airport=A.airport_name and A.airport_city like %s and (date(F.departure_time)=%s or date(F.arrival_time=%s))'
    cursor.execute(query, (source_airport, destination_airport, source_city, destination_city, date, date))
    #executes query
    #stores the results in a variable
    data = cursor.fetchall()
    cursor.close()
    error = None
    if(data):
        return render_template('view_public_info.html', error=error, results=data)
    else:
        error = 'No flights found  satisfying your search constraints. Please relax your search criterion: source_city: '+source_city+' source_airport: '+source_airport+' destination_city: '+destination_city+' destination_airport: '+destination_airport+' date: '+date
        return render_template('view_public_info.html', error=error, results=data)


#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    usertype = request.form['usertype']
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()

    #different usertype
    if(usertype=="customer"):
        query='select * from customer where email = %s and password = %s'
    elif(usertype=="booking_agent"):
        query='select * from booking_agent where email = %s and password = %s'
    elif(usertype=="airline_staff"):
        query='select * from airline_staff where username = %s and password = %s'
    else:
        #query will not be defined
        query=None

    #executes query
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
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username for usertype: '+usertype
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO user VALUES(%s, %s)'
        cursor.execute(ins, (username, password))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@app.route('/home')
def home():
    
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)

                
@app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    cursor = conn.cursor();
    blog = request.form['blog']
    query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
    cursor.execute(query, (blog, username))
    conn.commit()
    cursor.close()
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')
                
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
