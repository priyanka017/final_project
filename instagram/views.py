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
    dict={}
    if request.method == 'GET':
        signup_form = SignUpForm()
        # calling & display signup form
        template_name = 'signup.html'

    elif request.method == 'POST':
        signup_form = SignUpForm(request.POST)
        # calling & process the form data
        if signup_form.is_valid():
            # validate the form data
            username = signup_form.cleaned_data['username']
            name = signup_form.cleaned_data['name']
            email= signup_form.cleaned_data['email']
            password = signup_form.cleaned_data['password']
            while len(username) < 4:
                dict['invalid_username']="Usename must be atleast 5 characters"
                return render(request, "signup.html",dict)
            while len(password) < 5:
                dict['invalid_password']="Password must be at least 5 characters"
                return render(request, "signup.html",dict)

            new_user = UserModel(name=name, email=email, password=make_password(password), username=username)
            new_user.save()
            # save data to db
            template_name = 'success.html'
            # rendering to success.html after post req
        else:
            dict={"key":"Pleas fill the form"}
            return render(request,'signup.html',dict)
    return render(request,template_name, {'signup_form': signup_form})

def login_view(request):
    response_data = {}
    # if request.method == 'GET':
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            #validation successful
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            #read data from db
            user = UserModel.objects.filter(username=username).first()
            if user:
                #compare password
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    #if password matches session token generaed
                    token.create_token()
                    token.save()
                    response = redirect('/feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    return render(request,'login_fail.html')
            else:
                return render(request, 'login_fail.html')
        else:
            return HttpResponse("Invalid form data.")
    elif request.method == 'GET':
        form = LoginForm()
        response_data['form'] = form
    return render(request, 'login.html', response_data)


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
                client = ImgurClient('13aab932636aa80', '5d78c0178cb9258255982d328f803d536413f567')
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
