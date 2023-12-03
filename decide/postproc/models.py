from django.db import models
from enum import Enum


class PostprocTypeEnum(Enum):

    IDENTITY = 'IDENTITY'
    DHONDT = 'DHONDT'
    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
