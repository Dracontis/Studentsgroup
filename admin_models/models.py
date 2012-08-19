# ~*~ coding: utf-8 ~*~
from django.db import models
from django.contrib.admin.models import User
from django.contrib.comments.moderation import CommentModerator, moderator

# University model
class University(models.Model):
    title = models.CharField(max_length = 100)       # Full title of the University
    abbreviation = models.CharField(max_length = 20) # Abbrevation

    class Meta:
        verbose_name_plural = 'Университеты'

    def __unicode__(self):
        return self.abbreviation

# Group model
class Group(models.Model):
    university = models.ForeignKey(University)    # Title of universiry or abbreviation
    group_title = models.CharField(max_length=50) # Title of the group
    year = models.IntegerField()                  # Year of group creation
    hidden = models.BooleanField(default = False)

    class Meta:
        verbose_name_plural = 'Учебные группы'

    def __unicode__(self):
        return '%s (%s, %d)' % (self.group_title, self.university.title, self.year)

    def list_for_select(self):
        return '%s (%s)' % (self.group_title, self.university.title)
    
# Class for registration new users
class Registration(models.Model):
    nickname = models.CharField(max_length = 32)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 100)
    phone = models.CharField(max_length = 20)
    university = models.CharField(max_length = 100)
    groups = models.CharField(max_length = 500)
    is_hidden = models.BooleanField()

    class Meta:
        verbose_name_plural = 'Регистрация'

    def __unicode__(self):
        return self.nickname

# Class for InAdmin petitions to administration
class Petition(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length = 100)
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'Связь с администрацией'

    def __unicode__(self):
        return self.title

# User registration
class UserReg(models.Model):
    # Last name + first name or full_name
    full_name = models.CharField(max_length = 150)
    vk_id = models.CharField(max_length = 50, blank = True, null = True)
    go_id = models.CharField(max_length = 50, blank = True, null = True)
    # Fields for future
    nickname = models.CharField(max_length = 100, blank = True, null = True)
    email = models.CharField(max_length = 100, blank = True, null = True)

    def __unicode__(self):
        return self.full_name

class GroupPermission(models.Model):
    user = models.ForeignKey(UserReg)
    group = models.ForeignKey(Group)
    has_perm = models.BooleanField(default = False)

    class Meta:
        verbose_name_plural = u'Доступ к разделу группы'

    def __unicode__(self):
        return u"Доступ для %s" % self.user.full_name
