# ~*~ coding: utf-8 ~*~
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
# Python modules
import json
from urllib2 import urlopen
# My models and forms
from forms import CommentForm, RegistrationForm
from studentsgroup.engine_models.models import Message, Book, Comment
from studentsgroup.admin_models.models import Registration, UserReg, GroupPermission, Group
from studentsgroup.decorators import has_permission
import studentsgroup.settings as settings
# Pagination function
def PaginatorResult(request,obj):
    paginator = Paginator(obj,10)
    # Get GET page data
    page = request.GET.get('page',1)
    # Try to get page
    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        messages = paginator.page(1)
    # There is empty GET parameter
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)
    # Unknown exception
    except:
        raise Http404
    return messages
# Sort categories
def get_categories(objects):
    categories = []
    for obj in objects:
        if not obj.sub_category in categories:
            categories.append(obj.sub_category)
    return categories

@has_permission
def NewsAndTasks(request,group_id,pagename = 'news'):
##################################################################################################################
# General Block
# ################################################################################################################
    # Try to get Group object
    try:
        group_obj = Group.objects.get(pk = int(group_id))
    except:
        raise Http404
    # Set title and menu
    group_name = group_obj.group_title
    menu_obj = settings.MENU_ITEMS
    # Get sub category if any
    category = request.GET.get('category',None)
    if category == 'None':
        category = None

    if pagename == 'news' or pagename == 'tasks':
        messages = Message.objects.filter(Q(groups = group_obj) & Q(main_category__exact = pagename) & Q(is_archive = False)).order_by('-date')
        if category:
            messages = messages.filter(sub_category = category)
        messages = PaginatorResult(request, messages)

        # Render 'news' page
        if pagename == 'news':
            return render_to_response('base_news.html', locals())
        # Render 'tasks' page
        elif pagename == 'tasks':
            # get categories for messages
            categories = []
            message_obj = Message.objects.filter(Q(groups = group_obj) & Q(main_category__exact = pagename) & Q(is_archive = False))
            categories = get_categories(message_obj)
            return render_to_response('base_tasks.html', locals())
    else:
        raise Http404

@has_permission
def archive(request, group_id):
    pagename = "archive"
    # Get group by ID
    try:
        group_obj = Group.objects.get(pk = int(group_id))
    except:
        raise Http404
    # Set website title and generate menu
    group_name = group_obj.group_title
    menu_obj = settings.MENU_ITEMS
    # Get main and sub categories
    main_category = request.GET.get('main_category', 'news')
    category = request.GET.get('category',None)
    # TODO: create validator that None is reserved word for sub_category
    if category == 'None':
        category = None

    categories = []
    if main_category == 'news' or main_category == 'tasks':
        archive_objects = Message.objects.filter(Q(groups=group_obj) & Q(main_category=main_category) & Q(is_archive=True)).order_by('-date')
        if category:
            archive_objects = archive_objects.filter(sub_category=category)
        category_obj = Message.objects.filter(Q(groups=group_obj) & Q(main_category=main_category) & Q(is_archive=True))
    elif main_category == 'books':
        archive_objects = Book.objects.filter(Q(groups=group_obj) & Q(is_archive=True)).distinct()
        if category:
            archive_objects = archive_objects.filter(sub_category=category)
        category_obj = Book.objects.filter(Q(groups=group_obj) & Q(is_archive=True))
    else:
        raise Http404

    messages = PaginatorResult(request, archive_objects)
    categories = get_categories(category_obj)
    return render_to_response('base_archive.html', locals())

@has_permission
def books(request, group_id):
    pagename = "books"
    # Get group by ID
    try:
        group_obj = Group.objects.get(pk=int(group_id))
    except:
        raise Http404
        # Set website title and generate menu
    group_name = group_obj.group_title
    menu_obj = settings.MENU_ITEMS
    # Get main and sub categories
    main_category = request.GET.get('main_category', 'news')
    category = request.GET.get('category', None)
    # TODO: create validator that None is reserved word for sub_category
    if category == 'None':
        category = None

    categories = []
    # Same as in previous block. Except search.
    books = Book.objects.filter(Q(groups=group_obj) & Q(is_archive=False)).distinct()
    categories = get_categories(books)
    if request.method == 'POST':
        search = request.POST.get('search', '')
        books = books.filter((Q(title__icontains=search) | Q(author__icontains=search)))
    if category is not None:
        print "huh?"
        books = books.filter(sub_category=category)
    messages = PaginatorResult(request, books)
    return render_to_response('base_books.html', locals())

@has_permission
def EntryPage(request,group_id,pagename,message_id):
    # Set default variables
    logged = False
    nickname = ''
    try:
        group_id = int(group_id)
        group_obj = Group.objects.get(pk = group_id)
    except:
        raise Http404
    group_name = group_obj.group_title
    menu_obj = settings.MENU_ITEMS

    # Try to get message for this link
    try:
        message = Message.objects.get(Q(pk = message_id) & Q(groups = group_obj))
    except Message.DoesNotExist:
        raise Http404

    # Try to get session cookies
    session_id = request.session.get('c_uid')
    if session_id is not None:
        try:
            user = UserReg.objects.get(id = int(session_id))
            nickname = user.full_name
            logged = True
        except UserReg.DoesNotExist,UserReg.MultipleObjectsReturned: # Can be KeyError or DatabaseError
            pass

    # Get comments
    comments = Comment.objects.all().filter(rel_message = message_id)

    if request.method == 'POST':
        comment = Comment()
        comment_form = CommentForm(request.POST,instance = comment)
        if comment_form.is_valid():
            comment = comment_form.save(commit = False)
            msg_obj = Message.objects.get(id = int(comment_form.cleaned_data['rel_message']))
            comment.rel_message = msg_obj
            msg_obj.comments += 1
            msg_obj.save()
            comment.save()
            return HttpResponseRedirect(request.path+'#comments')
    else:
        comment_form = CommentForm(initial = {'nickname': nickname,'rel_message': message_id})

    return render_to_response('base_message.html', locals(),context_instance = RequestContext(request))
# Log in
@csrf_exempt
def Login(request):
    data_changed = False
    # Get data from Loginza and try to decode it
    token = request.POST.get('token',None)
    redirect_to = request.GET.get('next','/')
    try:
        url = urlopen('http://loginza.ru/api/authinfo?token=%s' % token)
        result = url.read()
        url.close()
    except:
        return redirect(redirect_to)
    data = json.loads(result)

    # OpenID provider
    if 'provider' in data:
        provider = data['provider']
    else:
        return redirect(redirect_to)
    if 'name' in data:
        name = data['name']
        if 'full_name' in name:
            full_name = name['full_name']
        elif 'first_name' in name and 'last_name' in name:
            full_name = name['first_name'] +" "+ name['last_name']
        else:
            return redirect(redirect_to)
    else:
        return redirect(redirect_to)
    # Get registered user or create new one
    # data_changed = save user if user was created or something was changed
    try:
        user = UserReg.objects.get(full_name = full_name)
    except UserReg.DoesNotExist:
        data_changed = True
        user = UserReg()
        user.full_name = full_name

    # Get user id
    try:
        provider.index('vkontakte')
        if user.vk_id is None and 'uid' in data:
            data_changed = True
            user.vk_id = data['uid']
    except ValueError:
        try:
            provider.index('google')
            if user.go_id is None and 'uid' in data:
                data_changed = True
                user.go_id = data['uid']
        except ValueError:
            return redirect(redirect_to)

    if data_changed:
        user.save()

    request.session['c_uid'] = user.id
    return redirect(redirect_to)
# Log out
def Logout(request):
    # Get page for redirect
    redirect_to = request.GET.get('next', '/')

    try:
        del request.session['uid']
    except KeyError:
        pass
    
    return HttpResponseRedirect(redirect_to)
# About
@csrf_exempt
def About(request):
    if request.method == 'POST':
        reg = Registration()
        reg_form = RegistrationForm(request.POST,instance = reg)
        if reg_form.is_valid():
            reg = reg_form.save()
            return HttpResponseRedirect(request.path)
    else:
        reg_form = RegistrationForm()
    return render_to_response('base_about.html',locals())
def GroupAuth(request,group_id):
    logged = True
    menu_obj = settings.MENU_ITEMS
    try:
        group_id = int(group_id)
        group_obj = Group.objects.get(pk = group_id)
    except:
        raise Http404
    # Set title
    group_name = group_obj.group_title

    uid = request.session.get('c_uid')
    if uid is None:
        logged = False
        render_to_response('base_nopermission.html',locals())
    if request.method == 'POST':
        result = GroupPermission.objects.get_or_create(user = UserReg.objects.get(id = int(uid)), group = group_obj)
        if False in result:
            error_message = u"Ваша заявка уже была размещена. Обратитесь к администрации группы."
        if True in result:
            error_message = u"Ваша заявка успешно размещена."
        return render_to_response('base_nopermission.html',locals())
    else:
        return render_to_response('base_nopermission.html',locals())
