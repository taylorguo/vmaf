#!/usr/bin/env python
# coding: UTF-8

import csv
# import requests
import datetime

import shutil

import platform, subprocess, json, os

# 获取视频的基本信息, 包括分辨率
def getBaseInfo(localvideo):
    baseinfo = { }
    if (os.path.isfile(localvideo)!=True):
        return None
    filesize = os.path.getsize(localvideo)
    if (filesize<=0):
        return None

    if (platform.system()=='Windows'):
        command = ["ffprobe","-loglevel","quiet","-print_format","json","-show_format","-show_streams","-i",localvideo]
    else:
        command = "ffprobe -loglevel quiet -print_format json -show_format -show_streams -i " +  localvideo

    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = result.stdout.read()

    # print(str(out))
    # print(json.loads(out.decode('utf-8')))

    streams = json.loads(out.decode("utf-8"))["streams"]
    for stream in streams:
        if (stream['codec_type']=="video"):
            videoinfo = { }
            videoinfo['width'] = stream['width']
            videoinfo['height'] = stream['height']
            videoinfo['codec_name'] = stream['codec_name']
            videoinfo['duration'] = stream['duration']
            videoinfo['bit_rate'] = stream['bit_rate']
            videoinfo['frame_number'] = stream['nb_frames']
            fr = stream['r_frame_rate']
            fr_list = str(fr).split('/')
            if (len(fr_list) == 2):
                videoinfo['frame_rate'] = float(fr_list[0]) / float(fr_list[1])
            else:
                videoinfo['frame_rate'] = float(fr_list[0])
            baseinfo['video'] = videoinfo
        if (stream['codec_type']=="audio"):
            audioinfo = { }
            audioinfo['duration'] = stream['duration']
            audioinfo['codec_name'] = stream['codec_name']
            audioinfo['bit_rate'] = stream['bit_rate']
            audioinfo['sample_rate'] = stream['sample_rate']
            audioinfo['channels'] = stream['channels']
            baseinfo['audio'] = audioinfo

    return baseinfo

# 从单列csv文件读取视频文件URL地址
# csv_reader = csv.reader(open("all.csv"))
# for row in csv_reader:
#     print(row)

    # 从URL下载读取后的视频
    # for url in row:
    #     f = requests.get(url)
        
    #     name = "quduobai_{:%Y%m%dT%H%M%S}.mp4".format(datetime.datetime.now())

    #     with open(name, "wb") as code:
    #         code.write(f.content)

# 从双列CSV文件读取视频文件URL地址
# with open("dedup_20180712.csv") as csv_reader:
#     for row in csv_reader:
#         print(row)
#         # print(row[1])

# 获取指定目录下所有文件
def get_files_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        return files
# 获取指定目录下所有目录
def get_dirs_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        return dirs

# 更改当前路径下某一目录下所有文件的名字;  本程序没有用该函数
# 输入当前路径下的某一目录名称，文件的新名称(含文件类型后缀)
def change_file_name(path, newname): 
    for (path,dirs,files) in os.walk(path):
        for filename in files:
            os.rename(os.path.join(os.path.dirname(os.path.realpath(__file__)),"s", filename) , 
                      os.path.join(os.path.dirname(os.path.realpath(__file__)),"s", newname))

if __name__ == "__main__":

    # 归档视频文件
    project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    print(project_path)
    current_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'QTT','test_20181024'+'/')
    file_list = get_files_name(current_path)

    for f in file_list:
        # 获取视频文件信息
        if f[-3:] == "mp4":            
            base_information = getBaseInfo(current_path+f)
            print(f)
            w = base_information['video']['width']
            h = base_information['video']['height']
            # 用分辨率对视频文件按目录分类, 并重新命名视频文件
            new_folder_name = str(w) + '_' + str(h)
            new_file_name = "qdp_{}_{:%Y%m%dT%H%M%S}.mp4".format(new_folder_name, datetime.datetime.now())
            # 如果目录不存在, 就新建
            if not os.path.exists(new_folder_name):
                try:
                    os.makedirs('QTT/test_20181024' + '/'+ new_folder_name)
                except OSError:
                    pass
            # 按分辨率目录归档视频文件, 以方便后面操作
            shutil.move('QTT/test_20181024/'+f, os.path.join(os.path.dirname(os.path.realpath(__file__)),"QTT/test_20181024", new_folder_name))
            os.rename(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'QTT', 'test_20181024', new_folder_name, f) , 
                        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'QTT', 'test_20181024', new_folder_name, new_file_name))
    
    print(" ****** 归档完毕！")

    dir_list = get_dirs_name(current_path)

    for d in dir_list:
        print(d)
        v_res = d.split('_', 1)
        # print(v_res[0])

        v_res_file_list = get_files_name(os.path.join(current_path, d))
        # print(v_res_file_list)
        
        i = 1
        while len(v_res_file_list) >= 2 and i <= len(v_res_file_list) - 1:
            r_video = os.path.join(current_path , d , v_res_file_list[0])
            t_video = os.path.join(current_path , d , v_res_file_list[i])

            i = i + 1
            # print(r_video, t_video)
    
            arguments = {"w":v_res[0], "h":v_res[1], "r_path":r_video, "t_path":t_video}
            command = "./ffmpeg2vmaf {w} {h} {r_path} {t_path}  --out-fmt json".format(**arguments)
            print(command)
            vs_result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            vs_out = vs_result.stdout.read()

            print(vs_out)
