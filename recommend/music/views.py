from django.shortcuts import render
from django.http import JsonResponse

from music.nn.prediction import get_music
from music.nn.prediction import get_predict_music, net_music_list, net_recommend_genre, net_predict_music

import random
import os
from django.conf import settings



def index(request):
    music_init_label, music_init_url, music_init_index = get_music()
    image = f'./static/background/background_{random.randint(0, 7)}.jpg'
    init_index = music_init_index
    init_label = music_init_label
    init_url = music_init_url.replace("/music",'')
    print(f'index: {init_url}')
    content = [{"title": f'init: {init_label}',
                "artist": "Josh Yu",
                "mp3": init_url,
                "poster": image,
                "init_index":init_index},]

    return render(request, 'index.html', {"content": content})


def josn_index(request):
    music_init_label, music_init_url, music_init_index = get_music()
    image = f'./static/background/background_{random.randint(0, 7)}.jpg'
    init_index = music_init_index
    init_index = music_init_index
    init_label = music_init_label
    init_url = music_init_url.replace("/music", '')
    print(f'index: {init_url}')
    content = [{"title": f'init: {init_label}',
                "artist": "Josh Yu",
                "mp3": init_url,
                "poster": image,
                "init_index": int(init_index)}, ]

    return JsonResponse(content, safe=False)

def predicting(request):
    get_result = request.POST
    print(request.POST)
    image = f'./static/background/background_{random.randint(0, 7)}.jpg'
    max_music_url, music_init_index, real_label_index = get_predict_music(int(get_result["init_index"]))
    max_url = max_music_url.replace("/music",'')
    content = [{"title": f'{get_result["title"]}',
                "artist": f'predict: {real_label_index}',
                "mp3": max_url,
                "oga": "http://www.jplayer.org/audio/ogg/Miaow-07-Bubble.ogg",
                "poster": image,
                "init_index":get_result["init_index"]}]
    return JsonResponse(content, safe=False)

def previous(request):
    get_result = request.POST
    content = [{"title": get_result["title"],
                "artist": "The Starting Point",
                "mp3": get_result["mp3"],
                "poster": "https://file.fishei.cn/wallhaven-g89p2.png",
                "init_index":get_result["init_index"]},
               ]
    return JsonResponse(content, safe=False)


def get_recommend_genre(request):
    music_list = net_recommend_genre()
    return JsonResponse({"musicList": music_list, "getId":5190711437}, safe=False)

def project(request):
    return render(request, 'project.html')

def get_music_list(request):
    music_list = net_music_list()
    return JsonResponse({"musicList": music_list, "getId":5177783391}, safe=False)

def get_music_recommend(request):
    get_result = request.GET.get("musicIndex", "")
    if get_result and (not get_result.isdigit() or not 0 <= int(get_result) < 10):
        return JsonResponse({"error": "musicIndex must be a genre index from 0 to 9"}, status=400)
    if len(get_result) == 0:
        get_result = random.sample(range(0, 10), 1)[0]
    print(get_result)
    music_list = net_predict_music(int(get_result))
    return JsonResponse({"musicList": music_list, "getId":5190711435}, safe=False)
