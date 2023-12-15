from django.db import models

class CustomUser(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = [username,password,email]

    def __str__(self):
        return self.username
    
    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
