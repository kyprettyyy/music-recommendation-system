import json
import uuid
import math
from pathlib import Path
from django.conf import settings
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from .engine import GENRES, recommend
from .models import Interaction, Track
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


def actor(request):
    if request.user.is_authenticated:
        return 'user:' + str(request.user.pk)
    if 'music_actor' not in request.session:
        request.session['music_actor'] = 'session:' + uuid.uuid4().hex
    return request.session['music_actor']


def serialize(t):
    return {'id': str(t.pk), 'title': t.title, 'artist': t.artist, 'genre': t.genre,
            'audio_url': t.audio_url, 'is_demo': t.is_demo}


@ensure_csrf_cookie
def home(request):
    return render(request, 'hybrid.html', {'genres': GENRES})


def signup(request):
    form = UserCreationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        from django.shortcuts import redirect
        return redirect('/')
    return render(request, 'registration/signup.html', {'form': form})


@require_GET
def catalog(request):
    q = request.GET.get('q', '')[:200]
    tracks = Track.objects.filter(Q(title__icontains=q) | Q(artist__icontains=q) | Q(genre__icontains=q))
    liked = set(Interaction.objects.filter(actor=actor(request), liked=True).values_list('track_id', flat=True))
    if request.GET.get('favorites') == '1':
        tracks = tracks.filter(pk__in=liked)
    return JsonResponse({'tracks': [{**serialize(t), 'liked': t.pk in liked} for t in tracks.order_by('pk')[:1000]]})


@require_POST
def interaction(request):
    try:
        body = json.loads(request.body)
        if not isinstance(body, dict):
            raise ValueError()
        track = Track.objects.get(pk=int(body['track_id']))
        event = body['event']
        if event not in ('play', 'like', 'unlike'):
            raise ValueError()
    except (ValueError, TypeError, KeyError, Track.DoesNotExist):
        return JsonResponse({'error': 'Supply a valid track_id and play/like/unlike event'}, status=400)
    row, _ = Interaction.objects.get_or_create(actor=actor(request), track=track)
    if event == 'play':
        Interaction.objects.filter(pk=row.pk).update(play_count=F('play_count') + 1)
    else:
        Interaction.objects.filter(pk=row.pk).update(liked=event == 'like')
    return JsonResponse({'ok': True})


@require_GET
def recommendations(request):
    genre = request.GET.get('genre') or None
    if genre is not None and genre not in GENRES:
        return JsonResponse({'error': 'Unknown genre'}, status=400)
    histories = {}
    for row in Interaction.objects.all().iterator():
        strength = min(row.play_count, 10) + 3*row.liked
        if strength:
            histories.setdefault(row.actor, {})[str(row.track_id)] = strength
    path = Path(settings.MUSIC_FEATURE_PATH)
    try:
        features = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        if not isinstance(features, dict):
            raise ValueError()
        tracks = [serialize(t) for t in Track.objects.all()]
        for t in tracks:
            f = features.get(t['id'])
            if f is None:
                continue
            if not isinstance(f, dict) or f.get('title') != t['title']:
                raise ValueError('Feature index belongs to another catalog')
            for key, size in [('audio', 10), ('lyrics', 32)]:
                vector = f.get(key, [])
                if not isinstance(vector, list) or (vector and len(vector) != size):
                    raise ValueError('Invalid vector dimensions')
                if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in vector):
                    raise ValueError('Invalid vector values')
        ranked = recommend(tracks, histories, actor(request), features, genre)
    except (ValueError, TypeError, OSError):
        return JsonResponse({'error': 'Invalid feature index; rebuild features'}, status=503)
    return JsonResponse({'tracks': ranked, 'notice': 'Demo tracks and seeded users are synthetic; scores are not quality metrics.'})
