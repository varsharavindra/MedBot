import os
import pickle
import model


def create_context(fb_id,status,obj):
    mysql = model.med()
    db = mysql.connect()
    cursor = db.cursor()
    data=obj
    status=cursor.execute("""insert into context values('%s','%s','%s')""" % (fb_id,status,data))
    db.commit()
    print("status context created"+str(status))
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
    return data[0]

def get_context_data(fb_id):
    mysql = model.med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""select data from context where fb_id='%s'""" % (fb_id))
    data = cursor.fetchone()
    db.close()

    if data == None:
        return None
    else:
        return data[0]


def remove_context(fb_id):
    mysql = model.med()
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("""delete from context where fb_id='%s'""" % (fb_id))
    db.commit()
    db.close()


if __name__ == '__main__':
    # create_context("dsds","set_state",None)
    print(get_context("dsds"))
    # remove_context("dsds")
