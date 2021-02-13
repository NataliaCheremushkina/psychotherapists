from django.db import models


class Therapist(models.Model):
    id = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=100)
    photo = models.ImageField()
    methods = models.TextField()

    class Meta:
        verbose_name = 'Психотерапевта'
        verbose_name_plural = 'Психотерапевты'

    def __str__(self):
        return self.name


class DBUpdate(models.Model):
    update_datetime = models.DateTimeField()
    data = models.TextField()
