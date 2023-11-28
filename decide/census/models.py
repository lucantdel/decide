from django.db import models


class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()

    GENDER = [
        ("MA", "Male"),
        ("FE", "Female"),
        ("NP", "No response")
    ]
    
    born_date = models.DateField()
    gender = models.CharField(max_length=2, choices=GENDER, null=True)
    city = models.CharField(max_length=20, null=True)

    class Meta:
        unique_together = (('voting_id', 'voter_id','born_date','gender','city'),)
