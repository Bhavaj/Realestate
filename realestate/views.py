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
    # Optionally, update next_milestone_points in session for admin dashboard refresh
    request.session['agent_next_milestone_points'] = agent.next_milestone()
    messages.success(request, "Payment deleted and agent points, star level, and next milestone updated.")
    return redirect('admin-dashboard')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Q
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
    
    agents = Agent.objects.all().order_by('-id')[:4]  # Latest 4 agents
    customers = Customer.objects.all().order_by('-id')[:4]  # Latest 4 customers
    projects = Project.objects.all().order_by('-id')[:4]  # Latest 4 projects
    payments = Payment.objects.select_related('project', 'customer', 'agent').all().order_by('-date')[:4]  # Latest 4 payments
    pending_gifts = AgentGift.objects.filter(status='pending').select_related('agent', 'gift').order_by('-date_earned')[:4]  # Latest 4 gifts
    
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
        "show_more_agents": total_agents > 4,
        "show_more_customers": total_customers > 4,
        "show_more_projects": total_projects > 4,
        "show_more_payments": total_payments > 4,
        "show_more_gifts": AgentGift.objects.filter(status='pending').count() > 4,
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


# View All Pages
@login_required(login_url='admin-login')
def all_agents(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    star_level_filter = request.GET.get('star_level', '')
    sort_by = request.GET.get('sort', '-id')
    
    # Start with all agents
    agents = Agent.objects.all()
    
    # Apply search filter
    if search_query:
        agents = agents.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply star level filter
    if star_level_filter and star_level_filter.isdigit():
        agents = agents.filter(star_level=int(star_level_filter))
    
    # Apply sorting
    valid_sorts = {
        'name': 'username',
        '-name': '-username',
        'email': 'email',
        '-email': '-email',
        'points': 'total_points',
        '-points': '-total_points',
        'star': 'star_level',
        '-star': '-star_level',
        'id': 'id',
        '-id': '-id'
    }
    sort_field = valid_sorts.get(sort_by, '-id')
    agents = agents.order_by(sort_field)
    
    total_agents = agents.count()
    
    # Get unique star levels for filter dropdown
    star_levels = Agent.objects.values_list('star_level', flat=True).distinct().order_by('star_level')
    
    context = {
        "agents": agents,
        "total_agents": total_agents,
        "search_query": search_query,
        "star_level_filter": star_level_filter,
        "sort_by": sort_by,
        "star_levels": star_levels,
    }
    return render(request, "all_agents.html", context)


@login_required(login_url='admin-login')
def all_customers(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    agent_filter = request.GET.get('agent', '')
    sort_by = request.GET.get('sort', '-id')
    
    # Start with all customers
    customers = Customer.objects.select_related('agent').all()
    
    # Apply search filter
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Apply agent filter
    if agent_filter and agent_filter.isdigit():
        customers = customers.filter(agent_id=int(agent_filter))
    
    # Apply sorting
    valid_sorts = {
        'name': 'name',
        '-name': '-name',
        'email': 'email',
        '-email': '-email',
        'agent': 'agent__username',
        '-agent': '-agent__username',
        'id': 'id',
        '-id': '-id'
    }
    sort_field = valid_sorts.get(sort_by, '-id')
    customers = customers.order_by(sort_field)
    
    total_customers = customers.count()
    
    # Get all agents for filter dropdown
    agents = Agent.objects.all().order_by('username')
    
    context = {
        "customers": customers,
        "total_customers": total_customers,
        "search_query": search_query,
        "agent_filter": agent_filter,
        "sort_by": sort_by,
        "agents": agents,
    }
    return render(request, "all_customers.html", context)


@login_required(login_url='admin-login')
def all_projects(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    project_type_filter = request.GET.get('project_type', '')
    sort_by = request.GET.get('sort', '-id')
    
    # Start with all projects
    projects = Project.objects.all()
    
    # Apply search filter
    if search_query:
        projects = projects.filter(name__icontains=search_query)
    
    # Apply project type filter
    if project_type_filter:
        projects = projects.filter(project_type=project_type_filter)
    
    # Apply sorting
    valid_sorts = {
        'name': 'name',
        '-name': '-name',
        'type': 'project_type',
        '-type': '-project_type',
        'created': 'created_at',
        '-created': '-created_at',
        'id': 'id',
        '-id': '-id'
    }
    sort_field = valid_sorts.get(sort_by, '-id')
    projects = projects.order_by(sort_field)
    
    total_projects = projects.count()
    
    # Get unique project types for filter dropdown
    project_types = Project.PROJECT_TYPES
    
    context = {
        "projects": projects,
        "total_projects": total_projects,
        "search_query": search_query,
        "project_type_filter": project_type_filter,
        "sort_by": sort_by,
        "project_types": project_types,
    }
    return render(request, "all_projects.html", context)


@login_required(login_url='admin-login')
def all_payments(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('admin-login')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    agent_filter = request.GET.get('agent', '')
    project_filter = request.GET.get('project', '')
    sort_by = request.GET.get('sort', '-date')
    
    # Start with all payments
    payments = Payment.objects.select_related('project', 'customer', 'agent').all()
    
    # Apply search filter
    if search_query:
        payments = payments.filter(
            Q(customer__name__icontains=search_query) |
            Q(agent__username__icontains=search_query) |
            Q(receipt_number__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )
    
    # Apply agent filter
    if agent_filter and agent_filter.isdigit():
        payments = payments.filter(agent_id=int(agent_filter))
    
    # Apply project filter
    if project_filter and project_filter.isdigit():
        payments = payments.filter(project_id=int(project_filter))
    
    # Apply sorting
    valid_sorts = {
        'customer': 'customer__name',
        '-customer': '-customer__name',
        'agent': 'agent__username',
        '-agent': '-agent__username',
        'amount': 'amount',
        '-amount': '-amount',
        'points': 'points',
        '-points': '-points',
        'project': 'project__name',
        '-project': '-project__name',
        'date': 'date',
        '-date': '-date',
        'id': 'id',
        '-id': '-id'
    }
    sort_field = valid_sorts.get(sort_by, '-date')
    payments = payments.order_by(sort_field)
    
    total_payments = payments.count()
    
    # Get all agents and projects for filter dropdowns
    agents = Agent.objects.all().order_by('username')
    projects = Project.objects.all().order_by('name')
    
    context = {
        "payments": payments,
        "total_payments": total_payments,
        "search_query": search_query,
        "agent_filter": agent_filter,
        "project_filter": project_filter,
        "sort_by": sort_by,
        "agents": agents,
        "projects": projects,
    }
    return render(request, "all_payments.html", context)


