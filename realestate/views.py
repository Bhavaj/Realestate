from django.views.decorators.http import require_POST

# ...existing code...

@require_POST
def delete_payment(request, payment_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    payment = get_object_or_404(Payment, id=payment_id)
    agent = payment.agent
    payment.delete()
    # Recalculate agent's total points from all remaining payments
    total_points = Payment.objects.filter(agent=agent).aggregate(total=Sum('points'))['total'] or 0
    agent.total_points = total_points
    agent.update_star_level()
    agent.save()
    messages.success(request, "Payment deleted and agent points updated.")
    return redirect('admin-dashboard')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from .models import Agent, Customer, Payment, Gift, AgentGift, Project


def home(request):
    return render(request, "home.html")


def agent_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('agent_dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "agent_login.html")


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin-dashboard')
        else:
            messages.error(request, "Invalid admin credentials")
    return render(request, "admin_login.html")


def customer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            customer = Customer.objects.get(email=email)
            return redirect('customer_dashboard', customer_id=customer.id)
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found with this email")
    return render(request, "customer_login.html")


@login_required(login_url='admin-login')
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    agents = Agent.objects.all().order_by('-id')[:5]  # Latest 5 agents
    customers = Customer.objects.all().order_by('-id')[:5]  # Latest 5 customers
    projects = Project.objects.all().order_by('-id')[:5]  # Latest 5 projects
    payments = Payment.objects.select_related('project', 'customer', 'agent').all().order_by('-date')[:5]  # Latest 5 payments
    pending_gifts = AgentGift.objects.filter(status='pending').select_related('agent', 'gift').order_by('-date_earned')[:5]  # Latest 5 gifts
    
    total_payment_amount = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_points_awarded = Payment.objects.aggregate(total=Sum('points'))['total'] or 0
    
    # Get total counts for stats
    total_agents = Agent.objects.count()
    total_customers = Customer.objects.count()
    total_projects = Project.objects.count()
    total_payments = Payment.objects.count()
    
    context = {
        "total_agents": total_agents,
        "total_customers": total_customers,
        "total_projects": total_projects,
        "total_payments": total_payments,
        "agents": agents,
        "customers": customers,
        "projects": projects,
        "payments": payments,
        "pending_gifts": pending_gifts,
        "total_payment_amount": total_payment_amount,
        "total_points_awarded": total_points_awarded,
        "show_more_agents": total_agents > 5,
        "show_more_customers": total_customers > 5,
        "show_more_projects": total_projects > 5,
        "show_more_payments": total_payments > 5,
        "show_more_gifts": AgentGift.objects.filter(status='pending').count() > 5,
    }
    return render(request, "admin_dashboard.html", context)


@login_required(login_url='agent_login')
def agent_dashboard(request):
    agent = request.user
    customers = agent.customers.all()
    payments = agent.payments.all().order_by('-date')[:10]
    agent_gifts = agent.agent_gifts.all().order_by('-date_earned')
    
    total_payment_amount = agent.payments.aggregate(total=Sum('amount'))['total'] or 0
    next_milestone_points = agent.next_milestone()
    
    context = {
        "agent": agent,
        "customers": customers,
        "payments": payments,
        "agent_gifts": agent_gifts,
        "total_customers": customers.count(),
        "total_payments": payments.count(),
        "total_payment_amount": total_payment_amount,
        "next_milestone_points": next_milestone_points,
    }
    return render(request, "agent_dashboard.html", context)


def customer_dashboard(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    payments = customer.payments.all().order_by('-date')
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        "customer": customer,
        "payments": payments,
        "total_payments": payments.count(),
        "total_amount": total_amount,
    }
    return render(request, "customer_dashboard.html", context)


@login_required(login_url='admin-login')
def add_customer(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        agent_id = request.POST.get("agent")
        
        try:
            agent = Agent.objects.get(id=agent_id)
            Customer.objects.create(name=name, email=email, agent=agent)
            messages.success(request, f"Customer {name} added successfully!")
            return redirect('admin-dashboard')
        except Agent.DoesNotExist:
            messages.error(request, "Selected agent not found")
        except Exception as e:
            messages.error(request, f"Error adding customer: {str(e)}")
    
    agents = Agent.objects.all()
    context = {"agents": agents}
    return render(request, "add_customer.html", context)


@login_required(login_url='admin-login')
def add_agent(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        
        try:
            # Check if username or email already exists
            if Agent.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            elif Agent.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
            else:
                agent = Agent.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                messages.success(request, f"Agent {username} added successfully!")
                return redirect('admin-dashboard')
        except Exception as e:
            messages.error(request, f"Error adding agent: {str(e)}")
    
    return render(request, "add_agent.html")


@login_required(login_url='admin-login')
def add_payment(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    if request.method == "POST":
        customer_id = request.POST.get("customer")
        amount = request.POST.get("amount")
        project_id = request.POST.get("project")
        receipt_number = request.POST.get("receipt_number")
        
        try:
            customer = Customer.objects.get(id=customer_id)
            project = Project.objects.get(id=project_id)
            # Convert amount string to decimal
            from decimal import Decimal
            amount_decimal = Decimal(amount)
            
            Payment.objects.create(
                customer=customer,
                agent=customer.agent,
                project=project,
                amount=amount_decimal,
                receipt_number=receipt_number
            )
            messages.success(request, f"Payment of ₹{amount} added successfully!")
            return redirect('admin-dashboard')
        except Customer.DoesNotExist:
            messages.error(request, "Selected customer not found")
        except Project.DoesNotExist:
            messages.error(request, "Selected project not found")
        except ValueError:
            messages.error(request, "Invalid amount format. Please enter a valid number.")
        except Exception as e:
            messages.error(request, f"Error adding payment: {str(e)}")
    
    customers = Customer.objects.all()
    projects = Project.objects.all().order_by('name')
    context = {"customers": customers, "projects": projects}
    return render(request, "add_payment.html", context)


@login_required(login_url='admin-login')
def add_project(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')

    if request.method == "POST":
        name = request.POST.get("name")
        project_type = request.POST.get("project_type")
        try:
            if project_type not in dict(Project.TYPE_CHOICES):
                messages.error(request, "Invalid project type")
            else:
                Project.objects.create(name=name, project_type=project_type)
                messages.success(request, f"Project '{name}' added successfully!")
                return redirect('admin-dashboard')
        except Exception as e:
            messages.error(request, f"Error adding project: {str(e)}")

    return render(request, "add_project.html")


@login_required(login_url='admin-login')
def delete_agent(request, agent_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    if request.method == "POST":
        try:
            agent = Agent.objects.get(id=agent_id)
            agent_name = agent.username
            agent.delete()
            messages.success(request, f"Agent '{agent_name}' deleted successfully!")
        except Agent.DoesNotExist:
            messages.error(request, "Agent not found")
        except Exception as e:
            messages.error(request, f"Error deleting agent: {str(e)}")
    return redirect('admin-dashboard')


@login_required(login_url='admin-login')
def delete_customer(request, customer_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    if request.method == "POST":
        try:
            customer = Customer.objects.get(id=customer_id)
            customer_name = customer.name
            customer.delete()
            messages.success(request, f"Customer '{customer_name}' deleted successfully!")
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found")
        except Exception as e:
            messages.error(request, f"Error deleting customer: {str(e)}")
    return redirect('admin-dashboard')


@login_required(login_url='admin-login')
def delete_project(request, project_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    if request.method == "POST":
        try:
            project = Project.objects.get(id=project_id)
            project_name = project.name
            project.delete()
            messages.success(request, f"Project '{project_name}' deleted successfully!")
        except Project.DoesNotExist:
            messages.error(request, "Project not found")
        except Exception as e:
            messages.error(request, f"Error deleting project: {str(e)}")
    return redirect('admin-dashboard')


@login_required(login_url='admin-login')
def update_gift_status(request, gift_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    if request.method == "POST":
        gift = get_object_or_404(AgentGift, id=gift_id)
        new_status = request.POST.get("status")
        if new_status in ['pending', 'delivered']:
            gift.status = new_status
            if new_status == 'delivered':
                from django.utils import timezone
                gift.date_delivered = timezone.now()
            gift.save()
            messages.success(request, f"Gift status updated to {new_status}")
        else:
            messages.error(request, "Invalid status")
    return redirect('admin-dashboard')


def admin_logout(request):
    logout(request)
    return redirect('home')


def agent_logout(request):
    logout(request)
    return redirect('home')


