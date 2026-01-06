from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class Agent(AbstractUser):
    agent_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    total_points = models.IntegerField(default=0)
    # Star levels: 0 (no star) to 7. 1-star unlocked at 2,500 PV
    star_level = models.IntegerField(default=0)

    def update_star_level(self):
        """Update star level based on total PV (points)."""
        # New thresholds (PV):
        # 1★: 2,500; 2★: 7,500; 3★: 20,000; 4★: 50,000; 5★: 100,000; 6★: 250,000; 7★: 500,000
        if self.total_points >= 500000:
            self.star_level = 7
        elif self.total_points >= 250000:
            self.star_level = 6
        elif self.total_points >= 100000:
            self.star_level = 5
        elif self.total_points >= 50000:
            self.star_level = 4
        elif self.total_points >= 20000:
            self.star_level = 3
        elif self.total_points >= 7500:
            self.star_level = 2
        elif self.total_points >= 2500:
            self.star_level = 1
        else:
            self.star_level = 0

    def next_milestone(self):
        """Points needed for next star level based on thresholds."""
        thresholds = {
            0: 2500,
            1: 7500,
            2: 20000,
            3: 50000,
            4: 100000,
            5: 250000,
            6: 500000,
        }
        if self.star_level >= 7:
            return 0
        target = thresholds.get(self.star_level, 2500)
        return max(0, target - self.total_points)

    def next_milestone_display(self):
        """Display-friendly next milestone text"""
        next_points = self.next_milestone()
        if next_points == 0:
            return "🎉 Max Level!"
        return f"{next_points} PV to Level {min(self.star_level + 1, 7)}"

    def save(self,*args,**kwargs):
        is_new = self.pk is None
        super().save(*args,**kwargs)
        if is_new and not self.agent_number:
            self.agent_number=f'AG{self.id:06d}'
            super().save(update_fields=['agent_number'])


    def __str__(self):
        return self.username


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="customers")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    TYPE_LAYOUT = 'layout'
    TYPE_CONSTRUCTION = 'construction'
    TYPE_CHOICES = [
        (TYPE_LAYOUT, 'Layout'),
        (TYPE_CONSTRUCTION, 'Construction'),
    ]

    name = models.CharField(max_length=200, unique=True)
    project_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_project_type_display()})"

class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="payments")
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="payments")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="payments", null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    points = models.IntegerField(default=0)
    receipt_number = models.CharField(max_length=100, unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure amount is a decimal for calculation
        if isinstance(self.amount, str):
            from decimal import Decimal
            self.amount = Decimal(self.amount)

        # PV calculation based on project type
        if self.project.project_type == Project.TYPE_LAYOUT:
            divisor = 1000
        else:
            divisor = 3000
        self.points = int(self.amount / divisor)

        super().save(*args, **kwargs)
        self.agent.total_points += self.points
        self.agent.update_star_level()
        self.agent.save()
        self.check_and_create_gifts()

    def check_and_create_gifts(self):
        """Check if agent qualifies for new gifts and create them"""
        agent = self.agent
        current_star_level = agent.star_level
        
        # Create gifts for current star level (including 1-star)
        if current_star_level >= 1:
            available_gifts = Gift.objects.filter(required_star_level=current_star_level)
            for gift in available_gifts:
                AgentGift.objects.get_or_create(
                    agent=agent,
                    gift=gift,
                    defaults={'status': 'pending'}
                )

    def __str__(self):
        return f"{self.customer.name} - ₹{self.amount}"


class Gift(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    required_star_level = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @classmethod
    def create_default_gifts(cls):
        """Create default gifts for star levels 1 through 7."""
        default_gifts = [
            # 1-star
            { 'name': 'Executive bag', 'description': None, 'required_star_level': 1 },
            { 'name': 'Personal kit', 'description': None, 'required_star_level': 1 },
            { 'name': 'General insurance', 'description': None, 'required_star_level': 1 },
            # 2-star
            { 'name': 'Medical kit', 'description': None, 'required_star_level': 2 },
            { 'name': 'Motivation programme', 'description': None, 'required_star_level': 2 },
            { 'name': 'Health insurance', 'description': None, 'required_star_level': 2 },
            # 3-star
            { 'name': 'Children education loan fund ₹10,000 (10 years)', 'description': None, 'required_star_level': 3 },
            { 'name': 'Loan eligibility ₹2,00,000', 'description': None, 'required_star_level': 3 },
            { 'name': 'Term insurance policy ₹50,00,000', 'description': None, 'required_star_level': 3 },
            # 4-star
            { 'name': 'Children education loan fund ₹50,000', 'description': None, 'required_star_level': 4 },
            { 'name': 'Tourism fund ₹50,000', 'description': None, 'required_star_level': 4 },
            { 'name': 'Loan eligibility ₹5,00,000', 'description': None, 'required_star_level': 4 },
            # 5-star
            { 'name': 'TVS Jupiter', 'description': None, 'required_star_level': 5 },
            { 'name': 'Honda Shine bike', 'description': None, 'required_star_level': 5 },
            { 'name': 'Loan eligibility ₹10,00,000', 'description': None, 'required_star_level': 5 },
            # 6-star
            { 'name': '302 sq yards plot (Narayanakhed)', 'description': None, 'required_star_level': 6 },
            { 'name': 'Shares value ₹5,00,000', 'description': None, 'required_star_level': 6 },
            { 'name': 'Car down payment ₹5,00,000', 'description': None, 'required_star_level': 6 },
            # 7-star
            { 'name': '10% royalty on company profit for 10 years', 'description': None, 'required_star_level': 7 },
            { 'name': 'Flat in Hyderabad (2BHK)', 'description': None, 'required_star_level': 7 },
            { 'name': "Children's marriage fund ₹10,00,000", 'description': None, 'required_star_level': 7 },
        ]

        for gift_data in default_gifts:
            cls.objects.get_or_create(
                name=gift_data['name'],
                defaults=gift_data
            )

    def __str__(self):
        return f"{self.name} (Level {self.required_star_level})"


class AgentGift(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
    ]
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="agent_gifts")
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name="agent_gifts")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date_earned = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_delivered = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['agent', 'gift']

    def __str__(self):
        return f"{self.agent.username} - {self.gift.name}"


# Signal to create gifts when a new agent is created
@receiver(post_save, sender=Agent)
def create_initial_gifts(sender, instance, created, **kwargs):
    if created:
        # The gift creation is now handled in the Payment.save() method
        pass
