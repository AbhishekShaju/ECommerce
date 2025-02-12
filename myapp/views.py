from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Category, Order



def home(request):
    categories = Category.objects.all()
    return render(request, 'home.html', {'categories': categories})

def index(request):
    return render(request, 'index.html')


def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {'product': product})

def product_list(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def contact(request):
    return render(request, 'contact.html')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Check if the product stock is sufficient
    if product.stock > cart_item.quantity:
        if not created:
            cart_item.quantity += 1
    else:
        # Optionally, you can display a message to the user that stock is insufficient
        return redirect('cart')  # Or return an error message view

    cart_item.save()
    return redirect('cart')




from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ProfileEditForm
from .models import UserProfile

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Handle profile editing
    if request.method == 'POST' and 'update_profile' in request.POST:
        form = ProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=user_profile)

    # Handle password change
    if request.method == 'POST' and 'change_password' in request.POST:
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Keep user logged in after password change
            messages.success(request, 'Your password was updated successfully!')
            return redirect('profile')
    else:
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'profile.html', {
        'form': form,
        'user_profile': user_profile,
        'password_form': password_form,  # Pass the password change form to the template
    })





@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

# Other views remain unchanged

@login_required
def update_cart(request, product_id, action):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

    if cart_item:
        product = cart_item.product
        if action == "increase":
            # Check if the quantity in cart is less than stock
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                # You can return a message about insufficient stock
                pass
        elif action == "decrease":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()  # Remove the item if quantity is reduced to 0

    return redirect('cart')


@login_required
def remove_item(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    if cart_item:
        cart_item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return redirect('cart')  # Redirect to cart page if cart doesn't exist

    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        billing_address = request.POST.get('billing_address')
        pincode = request.POST.get('pincode')
        phone_number = request.POST.get('phone_number')

        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            billing_address=billing_address,
            pincode=pincode,
            phone_number=phone_number,
            status="Pending",
        )

        # Add order items and update product stock
        for item in cart_items:
            order.items.create(
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

            # Reduce the stock of the ordered products
            item.product.stock -= item.quantity
            item.product.save()

        # Clear the cart after placing the order
        cart_items.delete()

        return redirect('order_success')  # Redirect to the order success page

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


@login_required
def order_success(request):
    return render(request, 'order_success.html')
# views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .forms import ForgotPasswordForm
import random
import string

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate a random password
                new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                # Update user's password
                user.password = make_password(new_password)
                user.save()
                # Send email
                send_mail(
                    'Password Reset Request',
                    f'Your new password is: {new_password}',
                    'your-email@gmail.com',
                    [email],
                    fail_silently=False,
                )
                return render(request, 'password_reset_done.html')
            except User.DoesNotExist:
                return render(request, 'forgot_password.html', {'form': form, 'error': 'Email not found!'})
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

def register(request):
    if request.method == 'POST':
        # Debugging: Print out POST data
        print(request.POST)
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate input fields
        try:
            # Email validation
            validate_email(email)
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered.")
                return render(request, 'register.html')

            # Username validation
            if User.objects.filter(username=name).exists():
                messages.error(request, "Username already exists.")
                return render(request, 'register.html')

            # Password validations
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'register.html')

            if len(password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return render(request, 'register.html')

            if not any(char.isdigit() for char in password):
                messages.error(request, "Password must contain at least one digit.")
                return render(request, 'register.html')

            if not any(char.isalpha() for char in password):
                messages.error(request, "Password must contain at least one letter.")
                return render(request, 'register.html')

            # If all validations pass, create the user
            user = User.objects.create_user(username=name, email=email, password=password)
            user.save()
            messages.success(request, "Registration successful.")
            return redirect('login')

        except ValidationError:
            messages.error(request, "Invalid email address.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Both fields are required.")
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')



# views.py

# views.py

from django.shortcuts import render
from .models import Order, OrderItem

def order_list(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)  # Get all orders for the logged-in user
        orders_with_items = []

        for order in orders:
            items = OrderItem.objects.filter(order=order)  # Get items for this order
            orders_with_items.append({'order': order, 'items': items})
        
        return render(request, 'orders.html', {'orders_with_items': orders_with_items})
    else:
        return redirect('login')  # Redirect to login if the user is not authenticated


