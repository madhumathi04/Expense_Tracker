from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import Expense

def index(request):
    return render(request, 'demo.html')

@csrf_exempt
def register(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return JsonResponse({'success': False, 'message': "Passwords do not match."})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': "Email already exists."})

        User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'success': True, 'message': "Registration successful. You can now log in."})

    return JsonResponse({'success': False, 'message': "Invalid request."})

@csrf_exempt
def login(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Get the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Invalid email or password."})

        # Authenticate using the username (which is a required field in User model)
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            auth_login(request, user)
            return JsonResponse({'success': True, 'message': "Login successful."})
        else:
            return JsonResponse({'success': False, 'message': "Invalid email or password."})

    return JsonResponse({'success': False, 'message': "Invalid request."})

def logout(request):
    auth_logout(request)
    return redirect('login')

def homepage(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        date = request.POST.get('date')

        Expense.objects.create(user=request.user, name=name, amount=amount, category=category, date=date)
        return JsonResponse({'success': True})

    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'homepage.html', {'expenses': expenses})

@csrf_exempt
def delete_expense(request, expense_id):
    if request.method == 'POST':
        try:
            expense = Expense.objects.get(id=expense_id, user=request.user)
            expense.delete()
            return JsonResponse({'success': True})
        except Expense.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Expense not found."})
    return JsonResponse({'success': False, 'message': "Invalid request."})