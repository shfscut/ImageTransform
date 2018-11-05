from django.db import models

# Create your models here.
class Student(models.Model):
    name=models.CharField(max_length=10, blank=True)
    age=models.IntegerField(blank=True, null=True)

    # class Meta:
    #     app_label='imageproxy'

    def __str__(self):
        return self.name