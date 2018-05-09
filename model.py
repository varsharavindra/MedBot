from flask import render_template, request
from flask import Flask
from flaskext.mysql import MySQL
import logging

import os.path
from uitemplates import button_template,text_template,quick_reply_type,quick_reply_template_class
import json
from nlp import apiai_query
import util

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger('stack')

app=Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1ks14cs119'
app.config['MYSQL_DATABASE_DB'] = 'medicine'
app.config['MYSQL_DATABASE_HOST'] = 'medicine.c9llzcxnfscl.us-east-1.rds.amazonaws.com'

# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
# app.config['MYSQL_DATABASE_DB'] = 'medicine'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'


def search_user(fb_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT * from users where cust_id='%s'""" % (fb_id))
    row = cursor.fetchone()
    db.close()
    print(row)
    if row is None:
        return False
    else:
        return True


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


def insert_query_users(uname, location, phoneno, email, cust_id,typeofuser):
    mysql = med()
    db = mysql.connect()
    cursor=db.cursor()
    print("""insert into users values( '%s','%s','%s','%s','%s')"""%(uname,location,phoneno,email,cust_id))
    cursor.execute("""insert into users values('%s','%s','%s','%s','%s',%d)""" % (uname,location,phoneno,email,cust_id,typeofuser))
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
    logger.info("User info "+str(user_informations))
    potential_vendor_list=[]
    for user_information in user_informations:
        # with open(str(fb_id) + "_requested_full_qty" + ".txt", "a") as f:
        #     f.write(str(user_information[1])+"\n"+str(user_information[2])+"\n"+str(user_information[3])+"\n"+str(user_information[4])+"\n"+str(user_information[5])+"\n"+str(user_information[6])+"\n")

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
    logger.info("Potential vendor list "+str(potential_vendor_list))

    potential_vendor_list.extend(impotential_vendor_list)
    return potential_vendor_list

def current_user(fb_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT location from users where cust_id='%s'"""%(fb_id))
    row = cursor.fetchone()
    db.close()
    logger.info("row "+str(row))
    return row[0]


def search_by_phone(phone_number):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT cust_id from users where phoneno = '%s'"""%(phone_number))
    print("""SELECT cust_id from users where phoneno = '%s'"""%(phone_number))
    row = cursor.fetchone()
    db.close()
    if row is not None:
        return row[0]
    else:
        return "new_user"



def search_trade_for_drug(fb_id, drug):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute(""" select trade_name from med_det where drug_name= "%s" and med_id in(select
                med_id from med_acc where cust_id="%s")"""%(drug,fb_id))
    row=cursor.fetchone()
    db.close()
    return row[0]

def get_med_info(batch_id,cust_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("select l.mfg_date, l.exp_date,l.cost from med_list as l where l.med_id in\
 (select d.med_id from med_det d where d.med_id in(select a.med_id from med_acc a where cust_id='%s' and batch_id='%s'))"% (cust_id,batch_id))
    data=cursor.fetchone()
    logger.info("data "+str(data))
    return data

def get_med_data(batch_id,med_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT mfg_date,exp_date,cost from med_list where batch_id='%s' and med_id='%s'"""%(batch_id,med_id))
    data=cursor.fetchone()
    logger.info("data "+str(data))
    db.close()
    return data

def get_drug_trade(med_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT drug_name,trade_name from med_det where med_id='%s'"""%(med_id))
    data = cursor.fetchone()
    db.close()
    logger.info("This is an info log"+str(data))
    return data

def get_email(phone_number):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT email from users where phoneno='%s'"""%(phone_number))
    data = cursor.fetchone()
    db.close()
    logger.info("This is an info log" + str(data))
    return data

def get_med_for_user(fb_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""SELECT trade_name from med_det  where med_id in(select med_id from med_acc  where cust_id='%s')"""%fb_id)
    data = cursor.fetchone()
    db.close()
    logger.info("This is an info log" + str(data))
    return data

def update_quantity(fb_id,tradename,qty):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""update med_acc set qty=%d where cust_id='%s' and med_id in(select med_id from med_det 
                        where trade_name='%s')"""%(int(qty), fb_id, tradename))
    db.commit()
    db.close()
    logger.info("This is an info log")

def get_qty_of_uploader(fb_id, medname):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""select qty from med_acc where cust_id='%s' and med_id in(select med_id from med_det where trade_name='%s')"""%(fb_id, medname))
    data = cursor.fetchone()
    db.close()
    logger.info("This is an info log" + str(data))
    if data is None:
        return False
    else:
        return data[0]

def check_med_for_cust(fb_id, medname):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute(
        """select * from med_acc where cust_id='%s' and med_id in
        (select med_id from med_det where trade_name='%s')""" % (
        fb_id, medname))
    data = cursor.fetchone()
    db.close()
    logger.info("This is an info log" + str(data))
    if data is None:
        return False
    else:
        return True


def compare_qty(fb_id, qty, medname):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute(
        """select qty from med_acc where cust_id='%s' and med_id in
        (select med_id from med_det where trade_name='%s')""" % (
            fb_id, medname))
    data = cursor.fetchone()
    db.close()
    logger.info("This is an info log" + str(data))
    if data is None:
        return False
    else:
        logger.info("qty check",data[0])
        if int(qty) <= int(data[0]):
            return True
        else:
            return False

def check_drug(trade_name):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute(
        """select * from drug where trade_name='%s'"""%(trade_name))
    data = cursor.fetchone()
    db.close()
    logger.info("This is an info log" + str(data))
    if data is None:
        return False
    else:
        return True

def get_qty_for_user(fb_id):
    mysql = med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""select qty from med_acc where cust_id='%s')"""%(fb_id))
    data = cursor.fetchone()
    db.close()
    logger.info("This is an info log" + str(data))
    return data



if __name__ == '__main__':

    #     insert_query_med_det("100","abc","zts","xyz")
    #   insert_query_users('vivek', '37.483872693672,-122.14900441942', '7406160779', 'v@gmail.com', '11')
    #   x=search_user(100)
     #search_user_for_med("100","7","crocin")
    # get_med_data("c300","200")
    # get_drug_trade("200")
    # get_email("9986427925")
    # get_med_for_user("100")
    #update_quantity("100","crocin",7)
    get_qty_of_uploader('1824444647629972','cifro')