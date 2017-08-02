from django.shortcuts import render, redirect
from forms import SignUpForm,LoginForm,PostForm,LikeForm,CommentForm
from models import UserModel, SessionToken ,PostModel, LikeModel, CommentModel
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password
from datetime import timedelta
from django.utils import timezone
from mysite.settings import BASE_DIR
from imgurpython import ImgurClient

#imgur client id n client secret
client_id= '13aab932636aa80'
Client_secret= '5d78c0178cb9258255982d328f803d536413f567'







# Create your views here.

def signup_view(request):
    if request.method == 'GET':
        # display signup form
        signup_form = SignUpForm()
        template_name = 'signup.html'
    elif request.method == 'POST':
        # process the form data
        signup_form = SignUpForm(request.POST)
        # validate the form data
        if signup_form.is_valid():
            # validation successful
            username = signup_form.cleaned_data['username']
            name = signup_form.cleaned_data['name']
            email = signup_form.cleaned_data['email']
            password = signup_form.cleaned_data['password']
           # new password= signup_form.cleaned_data['password']
            # save data to db
            new_user = UserModel(name=name, email=email, password=make_password(password), username=username)
            new_user.save()
            template_name = 'success.html'

    return render(request, template_name, {'signup_form': signup_form})


def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed.html/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)

def feed_view(request):
    return render(request, 'feed.html')

#For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
           return session.user
    else:
        return None


def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + post.image.url)

                client = ImgurClient(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)
                post.image_url = client.upload_from_path(path,anon=True)['link']
                post.save()

                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form' : form})
    else:
        return redirect('/login/')

    def feed_view(request):
        user = check_validation(request)
        if user and request.method == 'GET' :

            posts = PostModel.objects.all().order_by('-created_on')

            for post in posts:
                existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
                if existing_like:
                    post.has_liked = True

            return render(request, 'feed.html', {'posts': posts})
        else:

            return redirect('/login/')


    def like_view(request):
        user = check_validation(request)
        if user and request.method == 'POST':
            form = LikeForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
                if not existing_like:
                    LikeModel.objects.create(post_id=post_id, user=user)
                else:
                    existing_like.delete()
                return redirect('/feed/')
        else:
            return redirect('/login/')

    def comment_view(request):
        user = check_validation(request)
        if user and request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                comment_text = form.cleaned_data.get('comment_text')
                comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
                comment.save()
                return redirect('/feed/')
            else:
                return redirect('/feed/')
        else:
            return redirect('/login')

    # For validating the session
    def check_validation(request):
        if request.COOKIES.get('session_token'):
            session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
            if session:
                time_to_live = session.created_on + timedelta(days=1)
                if time_to_live > timezone.now():
                    return session.user
        else:
            return None




# Create your views here.

def signup_view(request):
    if request.method == 'GET':
        # display signup form
        signup_form = SignUpForm()
        template_name = 'signup.html'
    elif request.method == 'POST':
        # process the form data
        signup_form = SignUpForm(request.POST)
        # validate the form data
        if signup_form.is_valid():
            # validation successful
            username = signup_form.cleaned_data['username']
            name = signup_form.cleaned_data['name']
            email = signup_form.cleaned_data['email']
            password = signup_form.cleaned_data['password']
           # new password= signup_form.cleaned_data['password']
            # save data to db
            new_user = UserModel(name=name, email=email, password=make_password(password), username=username)
            new_user.save()
            template_name = 'success.html'

    return render(request, template_name, {'signup_form': signup_form})


def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed.html/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)

def feed_view(request):
    return render(request, 'feed.html')

#For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
           return session.user
    else:
        return None

    def post_view(request):
        user = check_validation(request)
        if user == None:
            return redirect('/login/')
        elif request.method == 'GET':
            post_form = PostForm()
            return render(request, 'post.html', {'post_form': post_form})
        elif request.method == "POST":
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()
                #imgur client id n client secret
                client = ImgurClient('13aab932636aa80','5d78c0178cb9258255982d328f803d536413f567')
                path = str(BASE_DIR + "\\" + post.image.url)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()
                return redirect("/feed/")
            else:
                return HttpResponse("Form data is not valid.")
        else:
            return HttpResponse("Invalid request.")


















    def feed_view(request):
        user = check_validation(request)
        if user:

            posts = PostModel.objects.all().order_by('created_on')

            for post in posts:
                existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
                if existing_like:
                    post.has_liked = True

            return render(request, 'feed.html', {'posts': posts})
        else:

            return redirect('/login/')

    def like_view(request):
        user = check_validation(request)
        if user and request.method == 'POST':
            form = LikeForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
                if not existing_like:
                    LikeModel.objects.create(post_id=post_id, user=user)
                else:
                    existing_like.delete()
                return redirect('/feed/')
            else:
                HttpResponse("form data is not valid")
        else:
            return redirect('/login/')

    def comment_view(request):
        user = check_validation(request)
        if user and request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                comment_text = form.cleaned_data.get('comment_text')
                current_post = PostModel.objects.filter(id=post_id).first()
                comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
                comment.save()
                return redirect('/feed/')
            else:
                return redirect('/feed/')
        else:
            return redirect('/login')

    # For validating the session
    def check_validation(request):
        if request.COOKIES.get('session_token'):
            session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
            if session:
                time_to_live = session.created_on + timedelta(days=1)
                if time_to_live > timezone.now():
                    return session.user
        else:
            return None