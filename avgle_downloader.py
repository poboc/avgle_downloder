import requests,os
from bs4 import BeautifulSoup
from functools import partial
import shutil
import threading
from multiprocessing.dummy import Pool
import subprocess
import time
from datetime import datetime

def download_ts_file(url,store_dir):
    ts_name = url.split('/')[-1]
    ts_dir = os.path.join(store_dir,ts_name)
    index = int(ts_name.split('-')[1])
    try:
        ts_res = requests.get(url)
    except:
        time.sleep(3)
        try:
            ts_res = requests.get(url)
        except:
            print("第",index,"個串流檔下載失敗ＱＱＱＱＱＱＱＱＱＱＱＱ")
            return
    f = open(ts_dir,'wb')
    f.write(ts_res.content)
    f.close
    print("第",index,"個串流檔下載完成")

if __name__ == '__main__':
    video_url = input("enter video url: ")
    startTime = datetime.now()
    print("開始時間: ",startTime)
    page_res = requests.get(video_url)
    soup = BeautifulSoup(page_res.text,'html.parser')
    try:
        m3u8_file_url = soup.find('source').get('src')
        video_name = soup.find('h1').text
        video_name = video_name.replace(":",'')
        video_name = video_name.replace(".",'-')
        video_name = video_name.replace(" ",'_')
    except:
        print("m3u8 url not found!!!")
        close()
    m3u8_res = requests.get(m3u8_file_url)
    m3u8_str = m3u8_res.text
    m3u8 = m3u8_str.split('\n')
    count = 0
    DIR = os.path.join('/Users/hankchen/documents/未命名/avgle',video_name)
    ts_foler = DIR
    if not os.path.isdir(DIR):
        os.makedirs(DIR)
    os.chdir(DIR)
    url_list = list()
    for string in m3u8:
        if not "http" in string:
            continue
        else:
            url_list.append(string)
    pool = Pool(30)
    lock = threading.Lock()
    pool.map(partial(download_ts_file, store_dir=DIR),url_list)
    pool.close()
    pool.join()
    print("所有串流檔下載完成")

    #開始合併串流檔
    filelist = os.listdir(DIR)
    ts_filenames = list()
    for name in filelist:
        if '.ts' in name:
            ts_filenames.append(name)
    del filelist
    ts_filenames = sorted(ts_filenames,key=lambda name:int(name.split('-')[1]))
    files_str = "concat:"
    for ts_filename in ts_filenames:
        files_str += ts_filename+'|'
    files_str.rstrip('|')
    merged_mp4 = video_name+'.mp4'
    subprocess.run(['ffmpeg', '-i', files_str, '-c','copy','-bsf:a', 'aac_adtstoasc',merged_mp4])
    print("檔案合併完成")
    #刪除ts檔
    mp4_fullpath = os.path.abspath(merged_mp4)
    time.sleep(2)
    video_folder = os.path.dirname(DIR)
    mp4_newpath = os.path.join(video_folder,merged_mp4)
    shutil.move(mp4_fullpath,mp4_newpath)
    shutil.rmtree(ts_foler)
    endTime = datetime.now()
    print("結束時間: ",endTime)
    print("共花費: ",endTime-startTime)

