import os
import pickle
import model
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger('stack')

def create_context(fb_id,status,obj):
    mysql = model.med()
    db = mysql.connect()
    cursor = db.cursor()
    data=obj
    cursor.execute("SELECT context from context where fb_id='%s'"%(fb_id))
    row = cursor.fetchone()
    if row is None:
        status=cursor.execute("""insert into context values('%s','%s','%s')""" % (fb_id,status,data))
    else:
        status = cursor.execute("""update context set context='%s' where fb_id='%s'"""%(status,fb_id))
    db.commit()
    logger.info("status context created " + str(status))
    db.close()
    
def get_context(fb_id):

    mysql = model.med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""select context from context where fb_id='%s'""" %(fb_id))
    data=cursor.fetchone()
    db.close()

    if data is None:
        return None
    elif data[0] == "None":
        return None
    logger.info("data" + str(data))
    return data[0]

def get_context_data(fb_id):
    mysql = model.med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""select data from context where fb_id='%s'""" % (fb_id))
    data = cursor.fetchone()
    db.close()
    logger.info("data " + str(data))
    if data == None:
        return None
    else:
        return data[0]


def remove_context(fb_id):
    mysql = model.med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""update context set context="None" where fb_id='%s'""" % (fb_id))
    db.commit()
    db.close()


if __name__ == '__main__':
    # create_context("dsds","set_state",None)
    print(get_context("dsds"))
    # remove_context("dsds")
