# ~*~ coding: utf-8 ~*~
from django.contrib import admin
from models import *
from studentsgroup.engine_models.models import *

##############################################################################################################################################
# Actions
# For GroupPermission
def set_perm_true(modeladmin, request, queryset):
    queryset.update(has_perm = True)
set_perm_true.short_description = u'Открыть доступ выбранным пользователям'
def set_perm_false(modeladmin, request, queryset):
    queryset.update(has_perm = False)
set_perm_false.short_description = u'Закрыть доступ выбранным пользователям'
##############################################################################################################################################
# Registration
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('nickname','email','phone','first_name','last_name','university','groups','is_hidden',)
# Group (display)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('university','group_title','hidden')
##############################################################################################################################################
# Petition
class PetitionAdmin(admin.ModelAdmin):
    list_display =  ('title','description','user',)

    def queryset(self, request):
        if request.user.is_superuser:
            return Petition.objects.all().distinct()
        else:
            return Petition.objects.filter(user = request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(PetitionAdmin, self).save_model(request, obj, form, change)

##############################################################################################################################################
# Models for permissions
class GroupPermissionAdmin(admin.ModelAdmin):
    readonly_fields = ['user','group']
    list_display = ('user','group','has_perm',)
    actions = [set_perm_true,set_perm_false]

    def queryset(self, request):
        if request.user.is_superuser:
            return GroupPermission.objects.all().distinct()
        else:
            user_profile = UserProfile.objects.get(user = request.user)
            return GroupPermission.objects.filter(group__in = [obj for obj in user_profile.group.all()]).distinct()
##############################################################################################################################################
# Registration
admin.site.register(Registration, RegistrationAdmin)
# Petitions
admin.site.register(Petition, PetitionAdmin)
# Permission
admin.site.register(GroupPermission, GroupPermissionAdmin)
# Register portal management
admin.site.register(University)
admin.site.register(Group, GroupAdmin)