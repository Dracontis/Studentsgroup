# ~*~ coding: utf-8 ~*~
import os, time, studentsgroup.settings
from django.db import models
from django.contrib.admin.models import User
from studentsgroup.admin_models.models import Group

#===============================================================================================================
# Categories for Messages and Books
class SubCategory(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = u'Категории заметок'
        
    def __unicode__(self):
        return self.title

# Extended User model
class UserProfile(models.Model):
    phone_number = models.CharField(max_length = 50,blank = True, null = True)
    group = models.ManyToManyField(Group)
    user = models.ForeignKey(User, unique = True)

# Blog messages
class Message(models.Model):
    title = models.CharField(max_length = 100)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    main_category = models.CharField(max_length = 50)
    sub_category = models.CharField(max_length = 100, null = True, blank = True)
    groups = models.ManyToManyField(Group)
    is_archive = models.BooleanField()
    user = models.ForeignKey(User, null = True, blank = True)
    comments = models.IntegerField(default = 0)

    class Meta:
        verbose_name_plural = u'Сообщения'
        ordering = ('date',)

    def __unicode__(self):
        return self.title

# Comments
class Comment(models.Model):
    nickname = models.CharField(max_length = 200)
    text = models.TextField()
    rel_message = models.ForeignKey(Message)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = u'Комментарии'
        ordering = ('-date',)

# Books
def content_file_name(instance, filename):
    split_filename = filename.split('.')
    return '/'.join(['covers', str(int(time.time()))+'.'+split_filename[-1]])

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length = 100, null = True, blank = True)
    sub_category = models.CharField(max_length = 100, null = True, blank = True)
    groups = models.ManyToManyField(Group)
    link = models.CharField(max_length = 1000)
    file_cover = models.ImageField(upload_to=content_file_name, blank = True, null = True, verbose_name='Cover')
    description = models.TextField()
    is_archive = models.BooleanField()
    user = models.ForeignKey(User, null = True, blank = True)

    class Meta:
        verbose_name_plural = u'Книги'
        ordering = ('author','title',)

    def __unicode__(self):
        return '%s (%s)' % (self.title,self.author)

    def cover_filename(self):
        return 'media/covers/' + os.path.basename(self.file_cover.name)

#===============================================================================================================
