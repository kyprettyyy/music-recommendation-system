"""Hybrid ranking added during the 2026 restoration."""
import math
import re

GENRES = ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']
WEIGHTS = {'collaborative': .4, 'lyrics': .3, 'audio': .3}


def tokenize(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?|[\u4e00-\u9fff]", text.lower())


def cosine(a, b):
    if not a or not b or len(a) != len(b):
        return None
    norm = math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
    return sum(x*y for x, y in zip(a, b))/norm if norm else None


def profile(history, features, key):
    pairs = [(features.get(i, {}).get(key), w) for i, w in history.items() if features.get(i, {}).get(key)]
    if not pairs:
        return []
    size = len(pairs[0][0])
    if any(len(v) != size for v, _ in pairs):
        raise ValueError('Inconsistent feature dimensions')
    return [sum(v[j]*w for v, w in pairs)/sum(w for _, w in pairs) for j in range(size)]


def recommend(tracks, histories, user, features, genre=None, limit=5, weights=None):
    weights = WEIGHTS if weights is None else weights
    if set(weights) != set(WEIGHTS) or any(not math.isfinite(w) or w < 0 for w in weights.values()) or not sum(weights.values()):
        raise ValueError('Invalid modality weights')
    if genre is not None and genre not in GENRES:
        raise ValueError('Invalid genre')
    ids = {str(t['id']) for t in tracks}
    histories = {u: {str(i): float(w) for i, w in h.items() if str(i) in ids and w > 0} for u, h in histories.items()}
    mine = histories.get(user, {})
    lyric_profile = profile(mine, features, 'lyrics')
    audio_profile = [float(g == genre) for g in GENRES] if genre else profile(mine, features, 'audio')
    neighbors = []
    norm = math.sqrt(sum(v*v for v in mine.values()))
    for other, h in histories.items():
        denom = norm*math.sqrt(sum(v*v for v in h.values()))
        similarity = sum(v*h.get(i, 0) for i, v in mine.items())/denom if denom else 0
        if other != user and similarity > 0:
            neighbors.append((similarity, h))
    popularity = {i: sum(h.get(i, 0) for h in histories.values()) for i in ids}
    maximum = max(popularity.values(), default=1) or 1
    results = []
    for t in tracks:
        i = str(t['id'])
        if i in mine:
            continue
        f = features.get(i, {})
        parts = {}
        if neighbors:
            parts['collaborative'] = sum(s*h.get(i, 0)/max(h.values()) for s, h in neighbors)/sum(s for s, _ in neighbors)
        for key, pref in [('lyrics', lyric_profile), ('audio', audio_profile)]:
            similarity = cosine(pref, f.get(key, []))
            if similarity is not None:
                parts[key] = max(0., similarity)
        total = sum(weights[k] for k in parts)
        effective = {k: weights[k]/total for k in parts} if total else {}
        score = sum(effective[k]*v for k, v in parts.items()) if total else popularity[i]/maximum
        results.append({**t, 'score': score, 'components': parts, 'weights': effective,
                        'fallback': None if total else 'popularity', 'feature_source': f.get('source', 'unavailable')})
    return sorted(results, key=lambda t: (-t['score'], str(t['id'])))[:limit]
