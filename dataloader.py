import pickle
import os
data_path = 'data/'

def load_pickle(child_path):
    data = pickle.load(open(os.path.join(data_path, child_path), 'rb'))
    return data