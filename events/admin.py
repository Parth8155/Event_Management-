from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review, Invitation

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'location']
    search_fields = ['user__username', 'full_name']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'location', 'start_time', 'is_public']
    list_filter = ['is_public', 'start_time', 'location']
    search_fields = ['title', 'description', 'organizer__username']
    date_hierarchy = 'start_time'

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status']
    list_filter = ['status']
    search_fields = ['user__username', 'event__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'event__title', 'comment']

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'invited_at']
    search_fields = ['user__username', 'event__title']
