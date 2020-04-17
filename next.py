import requests
import json
from lxml import etree
import ffmpeg.video
import ffmpeg
import os
from moviepy.editor import VideoFileClip
import math
import subprocess



requests.packages.urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
    'Referer': 'https://www.bilibili.com/'
}


def GetBiliVideo(homeurl,num,session=requests.session()):
    res = session.get(url=homeurl, headers=headers, verify=False)
    html = etree.HTML(res.content)
    videoinforms = str(html.xpath('//head/script[3]/text()')[0])[20:]
    videojson = json.loads(videoinforms)
    # 获取详情信息列表
    listinform = str(html.xpath('//head/script[4]/text()')[0])[25:-122]
    # listinform = str(html.xpath('//head/script[4]/text()')[0].encode('ISO-8859-1').decode('utf-8'))[25:-122]
    listjson=json.loads(listinform)
    # 获取视频链接和音频链接
    try:
        # 2018年以后的b站视频，音频和视频分离
        VideoURL = videojson['data']['dash']['video'][0]['baseUrl']
        AudioURl = videojson['data']['dash']['audio'][0]['baseUrl']
        flag=0
    except Exception:
        # 2018年以前的b站视频，格式为flv
        VideoURL = videojson['data']['durl'][0]['url']
        flag=1
    # 获取文件夹的名称
    # dirname = str(html.xpath("//h1/@title")[0].encode('ISO-8859-1').decode('utf-8'))
    # dirname = str(html.xpath("//h1/@title")[0])
    dirname = bv
    if not os.path.exists(dirname):
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(dirname)
        print('目录文件创建成功!' + dirname)
    # 获取每一集的名称
    # name=listjson['videoData']['pages'][num]['part']
    name = bv
    print(name)
    # 下载视频和音频
    print('正在下载 "'+name+'" 的视频····')
    BiliBiliDownload(homeurl=homeurl,url=VideoURL, name=os.getcwd()+'/'+dirname+'/'+name + '_Video.mp4', session=session)
    if flag==0:
        print('正在下载 "'+name+'" 的音频····')
        BiliBiliDownload(homeurl=homeurl,url=AudioURl, name=os.getcwd()+'/'+dirname+'/'+name+ '_Audio.mp3', session=session)
    
    
    print('正在组合 "'+ name +'" 的视频和音频····')
    CombineVideoAudio(name + '_Video.mp4',name + '_Audio.mp3', name + '_output.mp4',dirname)
    print(' "'+name+'" 下载完成！')

def BiliBiliDownload(homeurl,url, name, session=requests.session()):
    headers.update({'Referer': homeurl})
    session.options(url=url, headers=headers,verify=False)
    # 每次下载1M的数据
    begin = 0
    end = 512*512-1
    flag=0
    while True:
        headers.update({'Range': 'bytes='+str(begin) + '-' + str(end)})
        res = session.get(url=url, headers=headers,verify=False)
        if res.status_code != 416:
            begin = end + 1
            end = end + (512*512 - 1)
        else:
            headers.update({'Range': str(end + 1) + '-'})
            res = session.get(url=url, headers=headers,verify=False)
            flag=1
        with open(name, 'ab') as fp:
            fp.write(res.content)
            fp.flush()

        # data=data+res.content
        if flag==1:
            fp.close()
            break

def CombineVideoAudio(videopath,audiopath,outpath,dirname):
    currnet_path = os.getcwd() + "\\" + dirname + "\\"
    current_video_path = currnet_path + videopath
    current_audio_path = currnet_path + audiopath
    current_out_path = currnet_path + outpath

    video_time = math.floor(VideoFileClip(current_video_path).duration)
    stand_time = get_time_out(video_time)
 
    #将视频、音频剪辑标准时间
    stand_video_name = 'stand_video.mp4'
    stand_video_path = currnet_path + stand_video_name
    cut_video_cmd = 'ffmpeg -ss 00:00:00 -i '+ current_video_path +' -acodec copy -vcodec copy -t ' + stand_time + ' ' + stand_video_path
    subprocess.call(cut_video_cmd, shell=True)
 
    stand_audio_name = "stand_audio.mp3"
    stand_audio_path = currnet_path + stand_audio_name
    cut_audio_cmd = 'ffmpeg  -i ' + current_audio_path + ' -vn -qscale 0 -ss 00:00:00 -t ' + stand_time + ' ' + stand_audio_path
    subprocess.call(cut_audio_cmd, shell=True)
 
    combine_cmd = 'ffmpeg.exe -i ' + stand_video_path + ' -i ' + stand_audio_path +  ' -c:v copy -c:a aac -strict experimental ' + current_out_path
    subprocess.call(combine_cmd, shell=True)
 
    os.remove(current_video_path)
    os.remove(current_audio_path)
    os.remove(stand_audio_path)
    os.remove(stand_video_path)


def get_time_out(video_time):
    video_time_stand_str = ""
    if video_time < 60:
        video_time_stand_str = "00:00:%s" % get_current_num(video_time)
    elif video_time >= 60 and  video_time < 3600:
        video_time_M = math.floor(video_time / 60)
        video_time_S = video_time % 60
        video_time_stand_str = "00:%s:%s" % (get_current_num(video_time_M),get_current_num(video_time_S))
    elif video_time >= 3600:
        video_time_H = math.floor(video_time / 3600)
        video_time_M = math.floor(video_time % 3600 / 60)
        video_time_S = math.floor(video_time % 3600 % 60)
        video_time_stand_str = "%s:%s:%s" % (get_current_num(video_time_H),get_current_num(video_time_M),get_current_num(video_time_S))
    return video_time_stand_str

def get_current_num(time):
    result_str = ""
    if time > 10:
        result_str = str(time)
    else:
        result_str = "0%d" % time
    return result_str

# def dec(x):
# 	r=0
# 	for i in range(6):
# 		r+=tr[x[s[i]]]*58**i
# 	return (r-add)^xor

# def enc(x):
# 	x=(x^xor)+add
# 	r=list('BV1  4 1 7  ')
# 	for i in range(6):
# 		r[s[i]]=table[x//58**i%58]
# 	return ''.join(r)

    # table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    # tr={}
    # for i in range(58):
    #     tr[table[i]]=i
    # s=[11,10,3,8,4,6]
    # xor=177451812
    # add=8728348608


if __name__ == '__main__':
    bv =  "BV1e5411t7bD"
    print(bv)
    url='https://www.bilibili.com/video/'+bv
    GetBiliVideo(url,0)

    # # 视频选集
    # range_start=input('从第几集开始？')
    # range_end = input('到第几集结束？')
    # if int(range_start)<=int(range_end):
    #     for i in range(int(range_start),int(range_end)+1):
    #         GetBiliVideo(url+'?p='+str(i),i-1)

    # else:
    #     print('选集不合法！')





