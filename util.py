import os
import pickle

SUFFIX= "_context.txt"
contexts_path="contexts/"


def create_context(fb_id,status,obj):
    if fb_id in os.listdir(contexts_path):
        os.remove(contexts_path+ fb_id + SUFFIX)
        with open(fb_id + SUFFIX, "w") as f:
            f.write(status)
        with open(fb_id+".pickle","w") as f:
            pickle.dump(obj,f,pickle.HIGHEST_PROTOCOL)

def get_context(fb_id):
    if fb_id in os.listdir(contexts_path):
       with open(fb_id+SUFFIX,"r") as f:
           data=f.readline()
       return data
    else:
        return None

def get_context_data(fb_id):
    with open(fb_id + ".pickle", "w") as f:
        tuple=pickle.load(f)
    return tuple

def remove_context(fb_id):
    if fb_id in os.listdir(contexts_path):
        os.remove(contexts_path+ fb_id + SUFFIX)