import json
import tempfile
from pathlib import Path
from django.test import TestCase, SimpleTestCase, Client, override_settings
from .engine import recommend, GENRES
from .models import Track, Interaction


class RankingTests(SimpleTestCase):
    tracks = [{'id': str(i)} for i in range(1, 5)]

    def test_neighbor_preference_and_consumed_exclusion(self):
        h = {'me': {'1': 1}, 'neighbor': {'1': 1, '3': 1}, 'unrelated': {'2': 1, '4': 1}}
        r = recommend(self.tracks, h, 'me', {})
        self.assertEqual(r[0]['id'], '3')
        self.assertNotIn('1', [t['id'] for t in r])
        self.assertEqual(r[0]['weights'], {'collaborative': 1.})

    def test_lyric_similarity_changes_order(self):
        f = {'1': {'lyrics': [1, 0]}, '2': {'lyrics': [0, 1]}, '3': {'lyrics': [1, 0]}}
        r = recommend(self.tracks, {'me': {'1': 1}}, 'me', f)
        self.assertEqual(r[0]['id'], '3')
        self.assertEqual(r[0]['weights'], {'lyrics': 1.})

    def test_cold_start_and_unknown_item(self):
        r = recommend(self.tracks, {'other': {'2': 1, '999': 100}}, 'new', {})
        self.assertEqual(r[0]['id'], '2')
        self.assertEqual(r[0]['fallback'], 'popularity')
        self.assertEqual(r[0]['score'], 1.)

    def test_explicit_genre_and_invalid_weights(self):
        f = {'2': {'audio': [1.]+[0.]*9}, '3': {'audio': [0., 1.]+[0.]*8}}
        self.assertEqual(recommend(self.tracks, {}, 'new', f, 'classical')[0]['id'], '3')
        with self.assertRaises(ValueError):
            recommend(self.tracks, {}, 'new', {}, weights={'audio': -1})


class ApiTests(TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        isolated = override_settings(MUSIC_FEATURE_PATH=str(Path(folder.name)/'features.json'))
        isolated.enable()
        self.addCleanup(isolated.disable)
        for i in range(1, 8):
            Track.objects.create(id=i, title=f'Track {i}', genre=GENRES[i], is_demo=True)
        self.client.get('/')

    def post(self, client, i, event):
        return client.post('/api/interactions', json.dumps({'track_id': i, 'event': event}), content_type='application/json')

    def test_favorite_persists_and_is_private(self):
        self.assertEqual(self.post(self.client, 1, 'like').status_code, 200)
        self.assertEqual(len(self.client.get('/api/tracks?favorites=1').json()['tracks']), 1)
        self.assertEqual(Client().get('/api/tracks?favorites=1').json()['tracks'], [])
        self.post(self.client, 1, 'unlike')
        self.assertEqual(self.client.get('/api/tracks?favorites=1').json()['tracks'], [])

    def test_play_count_and_recommendation_exclusion(self):
        self.post(self.client, 1, 'play')
        self.post(self.client, 1, 'play')
        self.assertEqual(Interaction.objects.get(track_id=1).play_count, 2)
        result = self.client.get('/api/recommendations').json()['tracks']
        self.assertEqual(len(result), 5)
        self.assertNotIn('1', [t['id'] for t in result])

    def test_validation_and_csrf(self):
        self.assertEqual(self.post(self.client, 999, 'like').status_code, 400)
        self.assertEqual(self.client.post('/api/interactions', '[]', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.get('/api/recommendations?genre=invalid').status_code, 400)
        self.assertEqual(Client(enforce_csrf_checks=True).post('/api/interactions', '{}', content_type='application/json').status_code, 403)

    def test_search_and_corrupt_index(self):
        self.assertEqual(len(self.client.get('/api/tracks?q=Track%203').json()['tracks']), 1)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'bad.json'
            p.write_text('{')
            with override_settings(MUSIC_FEATURE_PATH=str(p)):
                self.assertEqual(self.client.get('/api/recommendations').status_code, 503)

    def test_account_favorites_follow_login(self):
        from django.contrib.auth.models import User
        User.objects.create_user(username='listener', password='a-test-password')
        self.client.login(username='listener', password='a-test-password')
        self.post(self.client, 2, 'like')
        another = Client()
        another.login(username='listener', password='a-test-password')
        self.assertEqual(another.get('/api/tracks?favorites=1').json()['tracks'][0]['id'], '2')

    def test_feature_index_cannot_silently_match_another_catalog(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'wrong.json'
            p.write_text(json.dumps({'1': {'title': 'Different song', 'audio': [1.]*10}}))
            with override_settings(MUSIC_FEATURE_PATH=str(p)):
                self.assertEqual(self.client.get('/api/recommendations').status_code, 503)
if __name__ == "__main__":
    list_1 = [{"id":1, "name": "qa"},{"id":0, "name": "qas"},{"id":5, "name": "qaf"}]
    r = sorted(list_1, key=lambda x: x.get("id"))

    print(r[0:2])
    # print(net_music_list())
