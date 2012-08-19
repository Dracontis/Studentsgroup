# ~*~ coding: utf-8 ~*~
from django.contrib import admin
from django import forms
# Extensions and snippets
from tinymce.widgets import TinyMCE
from ajax_select.fields import AutoCompleteField
# Optimization file
from optimization import validate_not_spaces
# After all imports, get my own models
from models import *
from studentsgroup.admin_models.models import Group
##############################################################################################################################################
# Important:
# All styles for autocomplete in base.css file
##############################################################################################################################################
# Actions
# For Message and Book
def set_archive_true(modeladmin, request, queryset):
    queryset.update(is_archive = True)
set_archive_true.short_description = u'Поместить выбранное в архив'
def set_archive_false(modeladmin, request, queryset):
    queryset.update(is_archive = False)
set_archive_false.short_description = u'Извлечь выбранное из архива'
##############################################################################################################################################
# Define an inline admin descriptor for UserProfile model
class UserProfileAdmin(admin.ModelAdmin):
    filter_horiizontal = ('group',)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'    # fk_name = Foreign Key Name
# Define a new UserAdmin class
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username','first_name','last_name','email','is_staff','is_superuser',)
    filter_gorizontal = ('group',)
    # Add new field to common User model
    inlines = [UserProfileInline, ]
##############################################################################################################################################
# Form manager for Message model in admin
class MessageAdminForm(forms.ModelForm):
    text = forms.CharField(widget=TinyMCE(attrs={'cols': 120, 'rows': 30,'nowrap': True}))
    main_category = forms.ChoiceField(choices = [('news','Новости'),('tasks','Задания')])
    sub_category = AutoCompleteField('category', required = False, validators = [validate_not_spaces])

    class Meta:
        model = Message

    def __init__(self, *arg, **kwargs):
        super(MessageAdminForm, self).__init__(*arg, **kwargs)
        # Get class-extension for current user (save data for groups, that can edit by this user)
        user_profile = UserProfile.objects.get(user = self.current_user)
        # Set choices for 'groups' field of the message model, which approved for current user
        self.fields['groups'].choices = [(g.id,g) for g in Group.objects.all().filter(group_title__in = [group_obj.group_title for group_obj in user_profile.group.all()])]
# Message model manager in admin
class MessageAdmin(admin.ModelAdmin):
    # Specify form manager for Message model in admin
    form = MessageAdminForm
    list_display = ('title','user','date','is_archive',)
    fields = ('title','text','main_category','sub_category','groups','is_archive',)
    list_filter = ('date','is_archive',)
    actions = [set_archive_true,set_archive_false]

    # Enable autocomplete and tinyMCE
    class Media:
        css = {
		    'all': ('/static/css/styles.css',)
	    }
        js = ['/static/js/jquery-1.6.2.min.js','/static/js/tiny_mce.js','/static/js/jquery.autocomplete.js','/static/js/ajax_select.js',]

    # Function add to form new field - 'current_user - which will help to get current logged user
    def get_form(self, request, obj=None, **kwargs):
        form = super(MessageAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    # Function that helps to save current user, who posted message
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        if obj.sub_category == '':
            obj.sub_category = 'No Category'

        SubCategory.objects.get_or_create(title = form.cleaned_data['sub_category'])
        super(MessageAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        Comment.objects.filter(rel_message = obj).delete()
        super(MessageAdmin, self).delete_model(request,obj)

    # Filter, displaying all messages, which allowed to edit by user
    def queryset(self, request):
        if request.user.is_superuser:
            return Message.objects.all().distinct()
        else:
            return Message.objects.filter(user = request.user)
##############################################################################################################################################
# Class for Book's form
class BookAdminForm(forms.ModelForm):
    file_cover = forms.ImageField(required = False)
    sub_category = AutoCompleteField('category', required = False, validators = [validate_not_spaces])
    link = forms.CharField(help_text='Ссылка для скачивания книги')
    title = forms.CharField(max_length = 199)
    
    class Meta:
        model = Book

    def __init__(self, *arg, **kwargs):
        super(BookAdminForm, self).__init__(*arg, **kwargs)
        # Get class-extension for current user (save data for groups, that can edit by this user)
        user_profile = UserProfile.objects.get(user = self.current_user.id)
        # Set choices for 'groups' field of the message model, which approved for current user
        self.fields['groups'].choices = [(g.id,g) for g in Group.objects.all().filter(group_title__in = [group_obj.group_title for group_obj in user_profile.group.all()])]
# Class for displaying model Book in admin
class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm
    list_display = ('title','author','user','is_archive',)
    fields = ('title','author','sub_category','link','file_cover','description','groups','is_archive',)
    exclude = ('user',)
    list_filter = ('is_archive',)
    actions = [set_archive_true,set_archive_false]

    # Enable autocomplete
    class Media:
        css = {
		'all': ('/static/css/styles.css',)
	}
	js = ['/static/js/jquery-1.6.2.min.js','/static/js/jquery.autocomplete.js','/static/js/ajax_select.js',]

    def get_form(self, request, obj=None, **kwargs):
        form = super(BookAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def queryset(self, request):
        if request.user.is_superuser:
            return Book.objects.all().distinct()
        else:
            return Book.objects.filter(user = request.user)

    def save_model(self, request, obj, form, change):
        try:
            del_file_obj = Book.objects.get(id = obj.id)
        except:
            del_file_obj = None
        if del_file_obj is not None:
            try:
                os.remove(os.path.abspath(del_file_obj.cover_filename()))
            except:
                pass
        obj.user = request.user
        if obj.sub_category == '':
            obj.sub_category = 'No Category'
        SubCategory.objects.get_or_create(title = form.cleaned_data['sub_category'])
        super(BookAdmin, self).save_model(request, obj, form, change)

##############################################################################################################################################
# Message model with its manager
admin.site.register(Message, MessageAdmin)
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
# Books
admin.site.register(Book, BookAdmin)
# Sub categories
admin.site.register(SubCategory)
# Comments
admin.site.register(Comment)
