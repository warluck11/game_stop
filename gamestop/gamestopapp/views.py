from django.shortcuts import render, HttpResponse, redirect
from gamestopapp.models import Product, Cart, Orders, Review
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import get_connection, EmailMessage
from django.conf import settings
import random
import razorpay

# Create your views here.
def home(request):
    
    return render(request, 'landing.html')

def index(request):
    
    return render(request, 'index.html')


def create_product(request):
    
    if request.method == "GET":
    
        return render(request, 'createproduct.html')
    
    else:
        
        name = request.POST['name']
        description = request.POST['description']
        manufacturer = request.POST['manufacturer']
        category = request.POST['category']
        price = request.POST['price']
        image = request.FILES['image']
        
        p = Product.objects.create(name = name, description = description , manufacturer = manufacturer
                               , category = category, price = price, image = image)
        
        p.save()
        
        return redirect('/')
    
def read_product(request):
    
    if request.method == "GET":
    
        p = Product.objects.all()
        
        context = {}
        
        context['data'] = p
        
        return render(request, 'readproduct.html', context)
    
    else:
        
        name = request.POST['search']
        
        prod = Product.objects.get(name = name)
        
        return redirect(f"read_product_detail/{prod.id}")


def delete_product(request, rid):
    
    p = Product.objects.filter(id = rid)
    
    p.delete()
    
    return redirect('/read_product')


def update_product(request, rid):
    
    if request.method == "GET":
    
        p = Product.objects.filter(id = rid)

        context = {}
        
        context['data'] = p
        
        return render(request, 'update_product.html', context)
    
    else:
        
        name = request.POST['name']
        description = request.POST['description']
        manufacturer = request.POST['manufacturer']
        category = request.POST['category']
        price = request.POST['price']
        
        p = Product.objects.filter(id = rid)
        
        p.update(name = name, description = description, manufacturer = manufacturer, category = category
                 , price = price)
        
        return redirect('/read_product')
    
    
def user_register(request):
    
    if request.method == "GET":
    
        return render(request, 'register.html')
    
    else:
        
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            
            u = User.objects.create(username = username, first_name = first_name, last_name = last_name,
                                email = email)
            
            u.set_password(password)
            
            u.save()
            
            return redirect('/login')
        
        else:
            
            context = {}
            
            context['error'] = "Password and Confirm Password does not match"
            
            return render(request, 'register.html', context)
        
        
def user_login(request):
    
    if request.method == "GET":
    
        return render(request, 'login.html')
    
    else:
        
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username = username, password = password)
        
        if user is not None:
            
            login(request, user)
            
            return redirect("/")
        
        else:
            
            context = {}
            
            context['error'] = "Username and Password Incorrect"
            
            return render(request, 'login.html', context)
        
        
def user_logout(request):
    
    logout(request)
    
    return redirect("/")


@login_required(login_url= "/login")
def create_cart(request, rid):
    
    prod = Product.objects.get(id = rid)
    
    cart = Cart.objects.filter(product = prod, user = request.user).exists()
    
    if cart:
    
        return redirect("/read_cart")
    
    else:
        
        user = User.objects.get(username = request.user)
        
        total_price = prod.price
        
        c = Cart.objects.create(product = prod, user = user, quantity = 1, total_price = total_price)
        
        c.save()
        
        
        return redirect("/read_cart")


@login_required(login_url= "/login")
def read_cart(request):
    
    cart = Cart.objects.filter(user = request.user)
    
    context = {}
    
    context['data'] = cart
    
    total_quantity = 0
    total_price = 0
    
    for x in cart:
        
        total_quantity += x.quantity
        total_price += x.total_price
        
    context['total_quanity'] = total_quantity
    context['total_price'] = total_price    
    
    return render(request, 'readcart.html', context)


def delete_cart(request, rid):
    
    cart = Cart.objects.filter(id  = rid)
    
    cart.delete()
    
    return redirect("/read_cart")


def update_cart(request, rid, q):
    
    cart = Cart.objects.filter(id = rid)
    
    c = Cart.objects.get(id = rid)
    
    price = int(c.product.price) * int(q)
    
    cart.update(quantity = q, total_price = price)
    
    return redirect("/read_cart")


def create_orders(request, rid):
    
    
    
    cart = Cart.objects.get(id = rid)
    
    order = Orders.objects.create(product = cart.product, user = request.user, quantity = cart.quantity, 
                          total_price = cart.total_price)
    
    
   
    
    client = razorpay.Client(auth=(settings.KEY_ID, settings.KEY_SECRET))
    
    data = { 'amount' : cart.total_price*100, 'currency' : 'INR', 'id' : 'order_OZIpjtTtChACtS' }
    
    payment = client.order.create(data = data)
    
    context = {}
    
    context['payment'] = payment
    
    order.save()
    
    cart.delete()
    

    
    return render(request, 'payment.html', context)

def read_orders(request):
    
    order = Orders.objects.filter(user = request.user)
    
    context = {}
    
    context['data'] = order
    
    return render(request, 'readorder.html', context)

def create_review(request, rid):
    
    prod = Product.objects.get(id = rid)
    
    rev = Review.objects.filter(user = request.user, product = prod).exists()
    
    
    if rev:
        
        return HttpResponse("Review Already Added")
    
    else:
        
        if request.method == "GET":
    
            return render(request, 'createreview.html')
    
        else:
            
            title = request.POST['title']
            content = request.POST['content']
            rating = request.POST['rate']
            image = request.FILES['image']
            
            product = Product.objects.get(id = rid)
            
            review = Review.objects.create(product = product, user = request.user, title = title, 
                                        content = content, rating = rating, image = image)
            
            review.save()
            
            return redirect("/")
        
        
        
def read_product_detail(request, rid):
    
    prod = Product.objects.filter(id = rid)
    
    p = Product.objects.get(id = rid)
    
    n = Review.objects.filter(product = p).count()

    rev = Review.objects.filter(product = p)
    
    sum = 0
    
    for x in rev:
        
        sum += x.rating
   
    try:
             
        avg_r = sum/n 
        avg = int(sum/n)
        
    except: 
        print("No review")
        
    context = {}
    
    context['data'] = prod
    
    if n == 0:
        
        context['avg'] = "No Review"
        
    else:
    
        context['avg_rating'] = avg
        context['avg'] = avg_r
        
    return render(request, 'readproductdetail.html', context)


def forgot_password(request):
    
    if request.method == "GET":
    
        return render(request, 'forgotpassword.html')
    
    else:
        
        email = request.POST['email']
        
        request.session['email'] = email
        
        user = User.objects.filter(email = email).exists()
        
        if user:
            
            otp = random.randint(1000, 9999)
        
            request.session['otp'] = otp
            
            with get_connection(
                
                host = settings.EMAIL_HOST,
                port = settings.EMAIL_PORT,
                username = settings.EMAIL_HOST_USER,
                password = settings.EMAIL_HOST_PASSWORD,
                use_tls = settings.EMAIL_USE_TLS
                
            ) as connection : 
                
                subject = "OTP Verification"
                email_from = settings.EMAIL_HOST_USER
                reciption_list = [ email ]
                message = f"OTP is {otp}"
                
                EmailMessage(subject, message, email_from, reciption_list, 
                            connection = connection).send()
            
                return redirect('/otp_verification')
            
        else:
            
            context = {}
            
            context['error'] = "User does not exist"
            
            return render(request, 'forgotpassword.html', context)
        
def otp_verification(request):
    
    if request.method == "GET":
    
        return render(request, 'otp.html')
    
    else:
        
        otp = int(request.POST['otp'])
        
        email_otp = int(request.session['otp'])
        
        if otp == email_otp:
            
            return redirect("/new_password")
        
        else:
            
            return HttpResponse("Not Ok")
        
        
def new_password(request):
    
    if request.method == "GET":
    
        return render(request, 'newpassword.html')
    
    else:
        
        email = request.session['email']
        
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        user = User.objects.get(email = email)
        
        if password == confirm_password:
            
            user.set_password(password)
            
            user.save()
            
            return redirect("/login")
        
        else:
            
            context = {}
            
            context['error'] = "Password and Confrim Password does not match"
            
            return render(request, 'newpassword.html', context)
        
        
def search_product(request):
    
    if request.method == "GET":
    
        return render(request, 'searchprod.html')
    
    else:
        
        search = request.POST['search']
        
        prod = Product.objects.filter(name = search)
        
        context = {}
        
        context['data'] = prod
        
        product = Product.objects.all()
        
        context['products'] = product 
        
        return render(request, 'searchprod.html', context)