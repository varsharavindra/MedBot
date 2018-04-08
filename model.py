from flask import render_template, request
from flask import Flask
from flaskext.mysql import MySQL

import os.path
from uitemplates import button_template,text_template,quick_reply_type,quick_reply_template_class
import json
from nlp import apiai_query

app=Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'bf07afc4f7181d'
app.config['MYSQL_DATABASE_PASSWORD'] = '3c67c0ac'
app.config['MYSQL_DATABASE_DB'] = 'heroku_f410f3c3cc58ba7'
app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-iron-east-05.cleardb.net'

def search_user(fb_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT * from users where cust_id='%s'""" % (fb_id))
    row = cursor.fetchone()
    db.close()
    print(row)
    return len(row[0])>0

class vendor:
    def __init__(self,cust_id,uname,location,phone,email,qty):
        self.cust_id=cust_id
        self.uname=uname
        self.lat,self.long=location.split(":")
        self.email=email
        self.phone=phone
        self.qty=qty

    def __str__(self):
        return str(self.__dict__)

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

def search_user_for_med(fb_id,quantity,name_of_med):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT u.cust_id,u.uname,u.location,u.phoneno,u.email,a.qty
                    from users u,med_acc a
                    where a.qty>='%s' and u.cust_id=a.cust_id and u.cust_id in(select cust_id from med_acc where med_id in(select med_id from med_det where trade_name='%s'))"""% (quantity,name_of_med))
    user_informations = cursor.fetchall()
    potential_vendor_list=[]
    for user_information in user_informations:
        # with open(str(fb_id) + "_requested_full_qty" + ".txt", "a") as f:
        #     f.write(str(user_information[1])+"\n"+str(user_information[2])+"\n"+str(user_information[3])+"\n"+str(user_information[4])+"\n"+str(user_information[5])+"\n"+str(user_information[6])+"\n")
        print(user_information)
        obj=vendor(user_information[0],user_information[1],user_information[2],user_information[3],user_information[4],user_information[5])
        potential_vendor_list.append(obj)

    cursor.execute("""SELECT u.cust_id,u.uname,u.location,u.phoneno,u.email,a.qty
                        from users u,med_acc a
                        where a.qty<'%s' and u.cust_id=a.cust_id and u.cust_id in(select cust_id from med_acc where med_id in(select med_id from med_det where trade_name='%s'))"""%(quantity, name_of_med))
    # row1=cursor.fetchone()
    # number_of_rows1=row1[0]
    # user_information_1 = cursor.fetchall()
    # for user_information in user_information_1:
    #     with open(str(fb_id) + "_requested_less_qty" + ".txt", "a") as f:
    #         f.write(str(user_information[1]) + "\n" + str(user_information[2]) + "\n" + str(
    #             user_information[3]) + "\n" + str(user_information[4]) + "\n" + str(user_information[5]) + "\n" + str(
    #             user_information[6]) + "\n")

    user_informations = cursor.fetchall()
    impotential_vendor_list = []
    for user_information in user_informations:
        obj = vendor(user_information[0], user_information[1], user_information[2], user_information[3],
                     user_information[4], user_information[5])
        impotential_vendor_list.append(obj)
    db.close()
    print(potential_vendor_list)

    return potential_vendor_list,impotential_vendor_list

def current_user(fb_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT location from users where cust_id='%s'"""%(fb_id))
    row = cursor.fetchone()
    db.close()
    print(row)
    return row[0]

if __name__ == '__main__':
    #    insert_query_drug("abc","xyz")
    #     insert_query_med_det("100","abc","zts","xyz")
    #   insert_query_users('vivek', '37.483872693672,-122.14900441942', '7406160779', 'v@gmail.com', '11')
    #   x=search_user(100)
    search_user_for_med("100","10","crocin")
