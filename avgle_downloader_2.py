import requests,os
from bs4 import BeautifulSoup
from functools import partial
import shutil
import threading
from multiprocessing.dummy import Pool
import subprocess
import time
from datetime import datetime

def download_ts_file(url,store_dir,sect):
    ts_name = str(sect)+"_"+url.split('/')[-1]
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
    split_video_num = input("enter number of video section:")
    split_video_num = int(split_video_num)
    video_urls = list(range(split_video_num))

    video_url = input("enter video url: ")
    for i in range(split_video_num):
        i_str = "-"+ str(i+1)
        if video_url.endswith(i_str):
            video_urls[i] = video_url
            break

    req = requests.get(video_url)
    soup = BeautifulSoup(req.text,'html.parser')
    a_tags = soup.find('h1',"big-title-truncate").find_all("a")[1:]
    j = 0
    for a_tag in a_tags:
        href = a_tag.get('href')
        while True:
            if type(video_urls[j]) == type(int()):
                video_urls[j] = href
                break
            else:
                j+=1
        j+=1

    DIR = ""
    ts_foler = ""
    video_name = ""
    ts_filenames = list()
    startTime = datetime.now()
    print("開始時間: ",startTime)

    for i in range(len(video_urls)):
        video_url = video_urls[i]
        page_res = requests.get(video_url)
        soup = BeautifulSoup(page_res.text,'html.parser')
        try:
            m3u8_file_url = soup.find('source').get('src')

            if i == 0 or not(bool(video_name)):
                video_name = soup.find('h1').text
                video_name = video_name.replace(":",'')
                video_name = video_name.replace(".",'-')
                video_name = video_name.replace(" ",'_')
                DIR = os.path.join('/Users/hankchen/documents/未命名/avgle',video_name)
                ts_foler = DIR
                if not os.path.isdir(DIR):
                    os.makedirs(DIR)
                os.chdir(DIR)

        except:
            print("m3u8 url not found!!!")
            close()
        m3u8_res = requests.get(m3u8_file_url)
        m3u8_str = m3u8_res.text
        m3u8 = m3u8_str.split('\n')
        count = 0

        url_list = list()
        for string in m3u8:
            if not "http" in string:
                continue
            else:
                url_list.append(string)
                ts_name = ts_name = str(i+1)+"_"+string.split('/')[-1]
                ts_filenames.append(ts_name)

        pool = Pool(30)
        lock = threading.Lock()
        pool.map(partial(download_ts_file, store_dir=DIR, sect = i+1),url_list)
        pool.close()
        pool.join()
        print("第"+str(i+1)+"段"+"串流檔下載完成")

    #開始合併串流檔
    filelist = os.listdir(DIR)
    # ts_filenames = sorted(ts_filenames,key=lambda name:int(name.split('-')[1]))
    # ts_filenames = sorted(ts_filenames)
    print(ts_filenames)
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

