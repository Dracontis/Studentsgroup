# ~*~ coding:utf-8 ~*~
from studentsgroup.engine_models.models import SubCategory
from django.db.models import Q

class CategoryLookup(object):
    def get_query(self,q,request):
        """ return a query set.  you also have access to request.user if needed """
        return SubCategory.objects.filter(Q(title__istartswith=q) | Q(title__icontains=q))
    
    def format_result(self,contact):
        """ the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  """
        return u"%s" % (contact.title)

    def format_item(self,contact):
        """ the display of a currently selected object in the area below the search box. html is OK """
        return unicode(contact)

    def get_objects(self,ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return SubCategory.objects.filter(pk__in = ids).order_by('title')
