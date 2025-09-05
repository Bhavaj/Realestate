from django.contrib import admin
from .models import Agent, Customer, Payment, Gift, AgentGift, Project
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html


class AgentGiftInline(admin.TabularInline):
    model = AgentGift
    extra = 0
    readonly_fields = ('agent', 'gift', 'date_earned', 'date_delivered')
    fields = ('agent', 'gift', 'status', 'date_earned', 'date_delivered')
    
    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding gifts manually


@admin.register(Agent)
class AgentAdmin(UserAdmin):
    model = Agent
    list_display = ('username', 'email', 'total_points', 'star_level', 'next_milestone_display')
    readonly_fields = ('total_points', 'star_level')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Rewards Info', {'fields': ('total_points', 'star_level')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rewards Info', {'fields': ('total_points', 'star_level')}),
    )

    inlines = [AgentGiftInline]

    def next_milestone_display(self, obj):
        next_points = obj.next_milestone()
        if next_points == 0:
            return "Max Level Reached! 🎉"
        return f"{next_points} points to next level"
    next_milestone_display.short_description = "Next Milestone"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "agent")
    search_fields = ("name", "email", "agent__username")
    list_filter = ("agent",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("customer", "agent", "project", "amount", "points", "receipt_number", "date")
    readonly_fields = ("points", "date")
    search_fields = ("customer__name", "agent__username", "receipt_number", "project__name")
    list_filter = ("date", "agent", "project__project_type")


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ("name", "required_star_level", "description")
    search_fields = ("name", "description")
    list_filter = ("required_star_level",)


@admin.register(AgentGift)
class AgentGiftAdmin(admin.ModelAdmin):
    list_display = ("agent", "gift", "star_level", "status", "date_earned", "date_delivered")
    list_filter = ("status", "gift__required_star_level", "date_earned")
    search_fields = ("agent__username", "gift__name")
    readonly_fields = ("agent", "gift", "date_earned")
    actions = ['mark_as_delivered']
    
    def star_level(self, obj):
        return obj.gift.required_star_level
    star_level.short_description = "Star Level"
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='delivered', date_delivered=timezone.now())
        self.message_user(request, f'{updated} gift(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark selected gifts as delivered"



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "project_type", "created_at")
    list_filter = ("project_type",)
    search_fields = ("name",)



