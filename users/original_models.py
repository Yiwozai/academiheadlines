# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Papers(models.Model):
    id = models.IntegerField(primary_key=True)
    dissertation = models.CharField(max_length=100)
    doi = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    journal = models.CharField(max_length=20)
    journal_date = models.CharField(max_length=10)
    keywords = models.CharField(max_length=90)
    dissertation_en = models.CharField(max_length=150)
    abstract = models.CharField(max_length=1000)
    author_unit = models.CharField(max_length=255)
    author_contact = models.CharField(max_length=100)
    classification = models.CharField(max_length=20)
    keywords_en = models.CharField(max_length=800)
    fund_project = models.CharField(max_length=255)
    abstract_en = models.CharField(max_length=2000)
    author_en = models.CharField(max_length=100)
    journal_en = models.CharField(max_length=100)
    url_id = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'papers'
