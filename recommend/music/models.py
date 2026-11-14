from django.db import models

class Track(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200, blank=True)
    genre = models.CharField(max_length=30)
    audio_url = models.CharField(max_length=500, blank=True)
    lyrics = models.TextField(blank=True)
    is_demo = models.BooleanField(default=False)


class Interaction(models.Model):
    actor = models.CharField(max_length=80, db_index=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    play_count = models.PositiveIntegerField(default=0)
    liked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['actor', 'track'], name='unique_actor_track')]
