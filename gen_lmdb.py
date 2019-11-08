import time
import threading
import os

import numpy as np
import cv2
import lmdb

LMDB_DIR = './lmdb_dir'
POS_IMG_PATH = './pos'
NEG_IMG_PATH = './neg'
THREAD_NUM = 2
BATCH_SIZE = 3 * THREAD_NUM


def gen_lmdb(img_path_list):
    global txn, lock, counter, s_t
    for img_file in img_path_list:
        if os.path.isfile(img_file) and os.path.getsize(img_file) > 0:
            with open(img_file, 'rb') as f:
                image_bin = f.read()
            with lock:
                txn.put(img_file.encode(), image_bin)
                """read img from lmdb
                env_db = lmdb,open(LMDB_DIR)
                txn = env.begin()
                # specify a image name in the database
                value = txn.read(IMG_NAME.encode())
                img_buff = np,frombuffer(value, dtype=np.uint8)
                img = cv2.imdecode(img_buff, cv2.IMREAD_COLOR)
                """
                counter += 1
                if counter % 5000 == 0:
                    print(" {} images processed, cost {:.1f} s for lastest 5000 patches".format(counter, time.time()-s_t))
                    s_t = time.time()


if not os.path.exists(LMDB_DIR):
    os.makedirs(LMDB_DIR)
pos_img_name_list = os.listdir(POS_IMG_PATH)
neg_img_name_list = os.listdir(NEG_IMG_PATH)
pos_img_list = []
neg_img_list = []
for i in pos_img_name_list:
    pos_img_list.append(os.path.join(POS_IMG_PATH, i))
for i in neg_img_name_list:
    neg_img_list.append(os.path.join(NEG_IMG_PATH, i))
whole_img_list = pos_img_list + neg_img_list
total_num = len(whole_img_list)
counter = 0
s_t = time.time()
lock = threading.Lock()

for ith_batch in range(total_num // BATCH_SIZE + 1):
    img_list = whole_img_list[ith_batch*BATCH_SIZE: (ith_batch+1)*BATCH_SIZE]
    if len(img_list) == 0:
        break;
    threads = []
    env = lmdb.open(LMDB_DIR, map_size=4096000000000)
    txn = env.begin(write=True)
    for i in range(THREAD_NUM):
        t = threading.Thread(target=gen_lmdb, args=(img_list[i*(BATCH_SIZE//THREAD_NUM): (i+1)*(BATCH_SIZE//THREAD_NUM)], ))
        t.daemon = True
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    txn.commit()
    env.close()

print("Finish generating lmdb, cost {:.1f}s".format(time.time()-s_t))




