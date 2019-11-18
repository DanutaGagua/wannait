from django.db import models


class ProductManager(models.Manager):
    """ Inspired by Django documentation """
    def for_registered_user(self, user_id):
        # TODO: change this dump baseline to real connection
        backend_answer = [
            self.model(
                id=index, name='name for registered',
                image_url='none')
            for index in range(50)
        ]
        return backend_answer

    def for_anonymous_user(self):
        # TODO: change this dump baseline to real connection
        backend_answer = [
            self.model(
                id=index, name='name for anonymous',
                image_url='none')
            for index in range(50)
        ]
        return backend_answer

    def for_owner(self, user_id):
        # TODO: change this dump baseline to real connection
        backend_answer = [
            self.model(
                id=index, name='name for owner',
                image_url='none')
            for index in range(50)
        ]
        return backend_answer


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=1000)
    image_url = models.URLField(max_length=1000)
    objects = ProductManager()

    def __str__(self):
        return self.name