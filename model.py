from flaskext.mysql import MySQL

def med():
    mysql = MySQL()
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'vaishnavi'
    app.config['MYSQL_DATABASE_DB'] = 'medicine'
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    mysql.init_app(app)
    return mysql


def med_query(medicines):
    mysql=med()
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from med_det where trade_name="+medicines)
    data=cursor.fetchone()
    return data

def search_user(fb_id):
    return False

def add_user(user_name,user_number,lat,long):
    pass