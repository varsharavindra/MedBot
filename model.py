from flask import render_template, request
from flask import Flask
from flaskext.mysql import MySQL
import os.path
from uitemplates import button_template,text_template,quick_reply_type,quick_reply_template_class
import json
import nlp

app=Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = ''
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = ''
app.config['MYSQL_DATABASE_HOST'] = ''


def med():
    mysql = MySQL()
    mysql.init_app(app)
    return mysql


def med_query(medicine):
    mysql = med()
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT med_id from med_det where trade_name=" + medicine)
    data = cursor.fetchone()
    # cursor.execute("insert into med_det values('1002','Aspirin','Acetyl Salysilic Acid','muscle ache' ")
    # data=cursor.fetchone()
    cursor.close()
    return data


def insert_query_users(uname, location, phoneno, email, cust_id):
    mysql = med()
    db = mysql.connect()
    cursor=db.cursor()
    print("""insert into users values( '%s','%s','%s','%s','%s')"""%(uname,location,phoneno,email,cust_id))
    cursor.execute("""insert into users values('%s','%s','%s','%s','%s')""" % (uname,location,phoneno,email,cust_id))
    db.commit()

def insert_query_med_acc(cust_id, med_id, batch_id, qty):
    mysql = med()
    db=mysql.connect()
    cursor=db.cursor()
    ("""insert into med_acc values( %d,%d,%s,%d)""")
    cursor.execute("""insert into med_acc values(%d,%d,%s,%d)""",(cust_id,med_id,batch_id,qty))
    db.commit()

def insert_query_med_list(batch_id, mfg_date, exp_date, cost, med_id):
    mysql = med()
    db = mysql.connect()
    cursor=db.cursor()
    ("""insert into med_list values( %s,%d,%d,%d,%d)""")
    cursor.execute("""insert into med_list values(%s,%d,%d,%d,%d )""",(batch_id,mfg_date,exp_date,med_id))
    db.commit()
    db.close()


def insert_query_med_det(med_id, drug_name, descp, trade_name):
    mysql = med()
    db = mysql.connect()
    cursor=db.cursor()
    ("""insert into med_det values( %d,%s,%s,%s)""")
    cursor.execute("""insert into med_det values(%d,%s,%s,%s)""",(med_id,drug_name,descp,trade_name))
    db.commit()


def insert_query_drug(drug_name, trade_name):
    mysql = med()
    db = mysql.connect()
    cursor=db.cursor()
    ("""insert into drug values( %s,%s )""")
    cursor.execute("""insert into drug values( %s,%s )""",(drug_name,trade_name))
    db.commit()
    db.close()


def search_user(fb_id):
    mysql=med()
    db = mysql.connect()
    cursor=db.cursor()
    cursor.execute("""SELECT * from users where cust_id=%s""", ( fb_id))
    id_data = cursor.fetchone()
    db.commit()
    db.close()
    print(id_data)
    return id_data



if __name__ == '__main__':
    #    insert_query_drug("abc","xyz")
    #     insert_query_med_det("100","abc","zts","xyz")
    #   insert_query_users('vivek', '37.483872693672,-122.14900441942', '7406160779', 'v@gmail.com', '11')
    #   x=search_user(100)
    search_uploader_for_med("10","crocin")