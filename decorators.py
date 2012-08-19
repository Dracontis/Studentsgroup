from django.shortcuts import redirect
from django.http import Http404
from django.db.models import Q
import studentsgroup.settings as settings
from studentsgroup.engine_models.models import Group
from studentsgroup.admin_models.models import GroupPermission

def has_permission(function_to_decorate) :
    def wrapper(request, group_id,**kwargs):
        try:
            group_id = int(group_id)
            group_obj = Group.objects.get(pk = group_id)
        except:
            raise Http404

        # Check user
        if group_obj.hidden:
            redirect_to = '/'+str(group_id)+'/groupauth'
            user_id = request.session.get('c_uid')
            if user_id is None:
                return redirect(redirect_to)
            try:
                permission = GroupPermission.objects.get(Q(user = user_id) & Q(group = group_obj))
            except GroupPermission.DoesNotExist:
                return redirect(redirect_to)
            if permission.has_perm is False:
                return redirect(redirect_to)
        return function_to_decorate(request, group_id, **kwargs)
    return wrapper