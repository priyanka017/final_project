from django.shortcuts import render, redirect
from forms import SignUpForm ,LoginForm ,PostForm
from models import UserModel, SessionToken ,PostModel
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password
from datetime import timedelta
from django.utils import timezone
from mysite.settings import BASE_DIR
from imgurpython import ImgurClient


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
                    response = redirect('feed/')
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
                post.image_url = client.upload_from_path(path,anon=True)['https://imgur.com/gallery/hmhRG']
                post.save()

                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form' : form})
    else:
        return redirect('/login/')