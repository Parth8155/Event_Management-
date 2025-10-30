from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Event, RSVP, Review, Invitation

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'bio', 'location', 'profile_picture']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'organizer', 'location', 'start_time', 'end_time', 'is_public', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class RSVPSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'event', 'user', 'status']
        read_only_fields = ['id', 'event', 'user']

class UpdateRSVPSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RSVP.STATUS_CHOICES, help_text="RSVP status")

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']

class AddReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        extra_kwargs = {
            'rating': {'help_text': 'Rating from 1 to 5'},
            'comment': {'help_text': 'Review comment'}
        }

class InvitationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'event', 'user', 'invited_at']
        read_only_fields = ['invited_at']

class InviteUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="ID of the user to invite")

class RemoveInvitationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(help_text="ID of the user whose invitation to remove")