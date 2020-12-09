#$user/bin/python3

# include libraries
import datetime
import requests
import config
import MySQLdb
import xlsxwriter
from flask import Flask , render_template,request , redirect,jsonify, flash, url_for, Response, session
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# start flask app
app = Flask(__name__)

# config
app.config.update(
    SECRET_KEY = config.secret_key
)

# configure flask limmiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return "%d" % (self.id)


# create some users with ids 1 to 20       
user = User(0)

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    ''' this is function for logouting from server site '''
    logout_user()
    return redirect('login')   
    
@app.route('/login',methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    '''this function return login page'''
    error = None
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["Password"]
        if check(username,password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            error = '!!!invalid user!!!' 
               
    return render_template('login.html', error=error)

# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)    

@app.route("/ok")
def sys_check():
    '''this function tell that falsk server is ok and running!!'''
    ret = {'status':'ok','message':'[+] flask server is running'}
    return jsonify(ret) , 200

@app.route('/',methods=["GET", "POST"])
@login_required
def index(): 

    if request.method == 'POST':
        cityname = request.form["name"]
        datalist = readdata(cityname, config.API_KEY)

    latestdata = reading_latestwritedatas_to_database()
    datas = []
    # f = temp
    for data in latestdata:
        f, pressure, humidity, croodlon, croodlat, weathermain, weatherdescription, visibility, windspeed, winddeg, cloudsall, syscountry, syssunrise, syssunset, timezone, name, timestamp = data
        datas.append({"tempmanualc":'%.1f' % float(f),"pressure":pressure, "humidity":humidity, "croodlon":croodlon,"weathermain":weathermain,"weatherdescription":weatherdescription,"visibility":visibility,"windspeed":windspeed,"winddeg":winddeg,"cloudsall":cloudsall,"syscountry":syscountry,"syssunrise":syssunrise,"syssunset":syssunset,"timezone":timezone,"name":name,"timestamp":timestamp})
    
    return render_template('index.html', data = {"datas" : datas})

@app.route('/photos')
@login_required
def photos_page(): 

    return render_template('photos.html')

@app.route('/history',methods=["GET", "POST"])
@login_required
def history_page(): 

    if request.method == 'POST':
        smsxlsx = request.form["smsxlsx"]
        print(smsxlsx)

    latestdata = read_from_database()
    datas = []
    # f = temp
    for data in latestdata:
        f, pressure, humidity, croodlon, croodlat, weathermain, weatherdescription, visibility, windspeed, winddeg, cloudsall, syscountry, syssunrise, syssunset, timezone, name, timestamp = data
        datas.append({"tempmanualc":'%.1f' % float(f),"pressure":pressure, "humidity":humidity, "croodlon":croodlon,"weathermain":weathermain,"weatherdescription":weatherdescription,"visibility":visibility,"windspeed":windspeed,"winddeg":winddeg,"cloudsall":cloudsall,"syscountry":syscountry,"syssunrise":syssunrise,"syssunset":syssunset,"timezone":timezone,"name":name,"timestamp":timestamp})

    allsms = []
    latestdata_sms = read_sms_from_database()
    for smss in latestdata_sms:
        smstext, timestamp = smss
        allsms.append({"smstext":smstext,"timestamp":timestamp})

    return render_template('history.html', data = {"datas" : datas,"allsms":allsms})

@app.route('/contact',methods=["GET", "POST"])
@login_required
def contact():
    ''' this is function for routing to the contact  '''
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        cpname = request.form["cpname"]
        website = request.form["website"]
        text = request.form["text"]
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alltext = f"""sender : {name}\nemail : {email}\ncompany name : {cpname}\nwebsite : {website}\ntext : {text}"""
        sendsms(alltext)
        writing_sms_to_database(timestamp,alltext)
        
        return render_template('contact.html')
    else:
        return render_template('contact.html')

def sendsms(mess):
    url = config.url
    data = {'receptor':config.phone, 'message':mess}
    respon = requests.post(url,data=data)
    return respon

def check(username,password):
    res = False
    if username == config.usernamein and password == config.passwordin:
        res = True
    return res 

def readdata(city_name,API_KEY):
    ''' this is function for collecting datas from api online '''
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}"

    result = requests.get(base_url)

    crood = result.json()['coord']
    weather = result.json()['weather']
    visibility = result.json()['visibility']
    wind = result.json()['wind']
    clouds = result.json()['clouds']
    sys = result.json()['sys']
    timezone = result.json()['timezone']
    cod = result.json()['cod']
    name = result.json()['name']


    if (cod == 200):
        tempmanualk = (result.json()['main']['temp'] + result.json()['main']['feels_like'] + result.json()['main'][
            'temp_min'] + result.json()['main']['temp_max']) / 4
        tempmanualc = tempmanualk - 273.15

        pressure = result.json()['main']['pressure']
        humidity = result.json()['main']['humidity']

        lista = [tempmanualc,pressure,humidity,crood['lon'],crood['lat'],weather[0]['main'],weather[0]['description'],visibility,wind['speed'],wind['deg'],clouds["all"],sys['country'],sys['sunrise'],sys['sunset'],timezone,name]
        writing_weather_to_database(lista)
        return lista

    else:
        return "error"

def read_from_database():

    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM works;")
    db.close()
    return cur.fetchall()

def read_sms_from_database():

    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM messages;")
    db.close()
    return cur.fetchall()

def reading_latestwritedatas_to_database():
    '''this function read alllatestwritedatas statuss from mysql database from past to today and return them'''

    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM works ORDER BY timestamp DESC LIMIT 1;")
    db.close()
    return cur.fetchall()

def connect_to_database():
    '''this function make connection to mysql service'''

    db = MySQLdb.connect(
        host=config.host,
        user=config.user,
        passwd=config.passwd,
        db=config.db,
        charset=config.charset,
        auth_plugin=config.auth_plugin,
        port=config.port,
    )

    return db

def writing_sms_to_database(timestamp,alltext):
    '''this function write collected sms datas to mysql database'''

    db = connect_to_database()    
    cur = db.cursor()    
    qury = f'INSERT INTO messages VALUES ("{alltext}","{timestamp}");'
    cur.execute(qury)
    db.commit()
    db.close()

def writing_weather_to_database(lista):
    '''this function write collected weather datas to mysql database'''

    db = connect_to_database()    
    cur = db.cursor()
    tempmanualc = lista[0]
    pressure = lista[1]
    humidity = lista[2]
    croodlon = lista[3]
    croodlat = lista[4]
    weathermain = lista[5]
    weatherdescription = lista[6]
    visibility = lista[7]
    windspeed = lista[8]
    winddeg = lista[9]
    cloudsall = lista[10]
    syscountry = lista[11]
    syssunrise = lista[12]
    syssunset = lista[13]
    timezone = lista[14]
    name = lista[15]
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    qury = f'INSERT INTO works VALUES ("{tempmanualc}","{pressure}","{humidity}","{croodlon}","{croodlat}","{weathermain}","{weatherdescription}","{visibility}","{windspeed}","{winddeg}","{cloudsall}","{syscountry}","{syssunrise}","{syssunset}","{timezone}","{name}","{timestamp}");'
    cur.execute(qury)
    db.commit()
    db.close()

# main first run part
if __name__ == '__main__':
    app.run("0.0.0.0",5000,debug=True)