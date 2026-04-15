import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from user.manager import UserManager

# Create your models here.


class UserModel(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    score = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: UserManager = UserManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(score__gte=1) & Q(score__lte=1000),
                name="score_between_1_and_1000",
            )
        ]

    def __str__(self):
        return f"{self.email}, score: {self.score}"

    def save(self, *args, **kwargs):
        if not self.score or self.score < 1:
            self.score = random.randint(1, 1000)
        super().save(*args, **kwargs)
