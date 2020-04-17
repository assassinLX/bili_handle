import requests
import json
from lxml import etree
import ffmpeg.video
import os

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
    # 
    #listinform = str(html.xpath('//head/script[4]/text()')[0])
    listinform = str(html.xpath('//head/script[4]/text()')[0].encode('ISO-8859-1').decode('utf-8'))[25:-122]
    listjson=json.loads(listinform)
    # 
    try:
        # 2018b
        VideoURL = videojson['data']['dash']['video'][0]['baseUrl']
        AudioURl = videojson['data']['dash']['audio'][0]['baseUrl']
        flag=0
    except Exception:
        # 2018bflv
        VideoURL = videojson['data']['durl'][0]['url']
        flag=1
    # 
    dirname = str(html.xpath("//h1/@title")[0].encode('ISO-8859-1').decode('utf-8'))
    if not os.path.exists(dirname):
        # 
        # 
        os.makedirs(dirname)
        print('!')
    # 
    name=listjson['videoData']['pages'][num]['part']
    print(name)
    # 
    print(' "'+name+'" ····')
    BiliBiliDownload(homeurl=homeurl,url=VideoURL, name=os.getcwd()+'/'+dirname+'/'+name + '_Video.mp4', session=session)
    if flag==0:
        print(' "'+name+'" ····')
        BiliBiliDownload(homeurl=homeurl,url=AudioURl, name=os.getcwd()+'/'+dirname+'/'+name+ '_Audio.mp3', session=session)
        print(' "'+name+'" ····')
    # CombineVideoAudio(name + '_Video.mp4',name + '_Audio.mp3',name + '_output.mp4')
    print(' "'+name+'" ')

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

def CombineVideoAudio(videopath,audiopath,outpath):
    ffmpeg.video.combine_audio(videopath,audiopath,outpath)
    os.remove(videopath)
    os.remove(audiopath)



if __name__ == '__main__':

    # av44518113
    av = input('')
    url='https://www.bilibili.com/video/'+av
    # 
    range_start=input('')
    range_end = input('')
    if int(range_start)<=int(range_end):
        for i in range(int(range_start),int(range_end)+1):
            GetBiliVideo(url+'?p='+str(i),i-1)
    else:
        print('')