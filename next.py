import requests
import json
from lxml import etree
import ffmpeg.video
import ffmpeg
import os
from moviepy.editor import VideoFileClip
import math
import subprocess
import re
import threading


requests.packages.urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36',
    'Referer': 'https://www.bilibili.com/'
}



def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True



def GetBiliVideo(User_Mid,bv,homeurl,num,session=requests.session()):
    res = session.get(url=homeurl, headers=headers, verify=False)
    html = etree.HTML(res.content)
    videoinforms = str(html.xpath('//head/script[3]/text()')[0])[20:]

    if is_json(videoinforms):
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
        dirname = str(User_Mid) + '\\' + str(bv) 
        if not os.path.exists(dirname):
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(dirname)
            print('目录文件创建成功!' + dirname)
        # 获取每一集的名称
        # name=listjson['videoData']['pages'][num]['part']
        name = bv
        # 下载视频和音频
        print('正在下载 "'+name+'" 的视频····')
        BiliBiliDownload(homeurl=homeurl,url=VideoURL, name=os.getcwd()+'/'+dirname+'/'+name + '_Video.mp4', session=session)
        if flag==0:
            print('正在下载 "'+name+'" 的音频····')
            BiliBiliDownload(homeurl=homeurl,url=AudioURl, name=os.getcwd()+'/'+dirname+'/'+name+ '_Audio.mp3', session=session)
        print('正在组合 "'+ name +'" 的视频和音频····')
        real_name = str(html.xpath("//h1/@title")[0])
        CombineVideoAudio(name + '_Video.mp4',name + '_Audio.mp3', name + '_output.mp4',dirname,real_name)
    else:
        print(bv+'下载失败！！！！！！！！！！！！！！！')

def BiliBiliDownload(homeurl,url, name, session=requests.session()):
    headers.update({'Referer': homeurl})
    session.options(url=url, headers=headers,verify=False)
    # 1M
    begin = 0
    end = 1024*512-1
    flag=0
    while True:
        headers.update({'Range': 'bytes='+str(begin) + '-' + str(end)})
        res = session.get(url=url, headers=headers,verify=False)
        if res.status_code != 416:
            begin = end + 1
            end = end + 1024*512
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

def CombineVideoAudio(videopath,audiopath,outpath,dirname,real_name):
    currnet_path = os.getcwd() + "\\" + dirname + "\\"
    current_video_path = currnet_path + videopath
    current_audio_path = currnet_path + audiopath
    current_out_path = currnet_path + outpath

    video_file_clip = VideoFileClip(current_video_path)
    video_time = math.floor(video_file_clip.duration)
    video_file_clip.close()
    stand_time = get_time_out(video_time)
 
    #将视频、音频剪辑标准时间
    stand_video_name = 'stand_video.mp4'
    stand_video_path = currnet_path + stand_video_name
    cut_video_cmd = 'ffmpeg -ss 00:00:00 -i '+ current_video_path +' -acodec copy -vcodec copy -t ' + stand_time + ' ' + stand_video_path
    s_v_p = subprocess.Popen(cut_video_cmd, shell=True)
    s_v_p.wait()

    stand_audio_name = "stand_audio.mp3"
    stand_audio_path = currnet_path + stand_audio_name
    cut_audio_cmd = 'ffmpeg  -i ' + current_audio_path + ' -vn -qscale 0 -ss 00:00:00 -t ' + stand_time + ' ' + stand_audio_path
    s_a_p = subprocess.Popen(cut_audio_cmd, shell=True)
    s_a_p.wait()

    combine_cmd = 'ffmpeg.exe -i ' + stand_video_path + ' -i ' + stand_audio_path +  ' -c:v copy -c:a aac -strict experimental ' + current_out_path
    p = subprocess.Popen(combine_cmd, shell=True)
    p.wait()

    if p.returncode == 0 and s_v_p.returncode == 0 and s_a_p.returncode == 0:
        os.remove(stand_audio_path)
        os.remove(stand_video_path)
        os.remove(current_audio_path)
        os.remove(current_video_path)
        print('\n\n\n')
        dir_new_name = currnet_path + find_chinese(real_name) + '.mp4'
        print('\n\n\n')
        os.rename(current_out_path,dir_new_name)
        print(find_chinese(real_name)+"下载成功！！")

def find_chinese(file):
    pattern = re.compile(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])")
    chinese = re.sub(pattern, '', file)
    return chinese

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
    if time >= 10:
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


def setting_and_down(bv_id):
    url='https://www.bilibili.com/video/'+ bv_id
    GetBiliVideo('other',bv_id,url,0)

def setting_and_down_by_av(User_Mid,av):
    url='https://www.bilibili.com/video/av'+ av
    name = "av" + av
    GetBiliVideo(User_Mid,name,url,0)

# 从主页拿视频列表的函数
def get_Mainpage_Video(User_Mid):

    headers = {
    'Host': 'space.bilibili.com',
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Referer': 'https://space.bilibili.com/' + str(User_Mid)+ '/',    # 这里是Mid
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    
    url = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid='+ str(User_Mid)+'&pagesize=100&tid=0&page=1&keyword=&order=pubdate'
    # 请求 Url 前面要加上   主机地址！  在这里就是space.xxxxxx   
    # 注意从浏览器里抓包可以看到完整的地址，而从Fiddler
    #最大的请求size是100
    
    content = requests.get(url, headers = headers, verify = False).json()
    i = content['data']['count'] # 视频个数
    if i>=100:
        i = 100
        video_List=[]
        for num in range(i):
            aid =  content['data']['vlist'][num]['aid']
            title = content['data']['vlist'][num]['title']
            author = content['data']['vlist'][num]['author']
            tmp = {"aid":aid,"title":title,"author":author}
            video_List.append(tmp)
        return video_List
    else:
        video_List=[]
        for num in range(i):
            aid =  content['data']['vlist'][num]['aid']
            title = content['data']['vlist'][num]['title']
            author = content['data']['vlist'][num]['author']
            tmp = {"aid":aid,"title":title,"author":author}
            video_List.append(tmp)
        return video_List


def setting_and_down_list(User_Mid):
    video_list = get_Mainpage_Video(User_Mid)  # 拿到视频列表
    if not os.path.exists(str(User_Mid)):
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(str(User_Mid))
        print('目录文件创建成功!' + str(User_Mid))
    json_path = str(User_Mid) + '\\' + str(User_Mid) + '.txt'
    with open(json_path,"w+") as f:
        for cfg in video_list:
            f.write(str(cfg)+'\n')
        f.close()
    for cfg in video_list:
        print(cfg['aid'])
        print('\n')
        current_av_id = cfg['aid']
        setting_and_down_by_av(User_Mid,str(current_av_id))


if __name__ == '__main__':

    setting_and_down('BV1jb411s7Sn')

    # User_Mid = 402900234  # 在这里改你的Up主编号
    # setting_and_down_list(User_Mid)




