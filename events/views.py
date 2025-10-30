from django.contrib.auth.models import User
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db import models
from .models import Event, RSVP, Review, Invitation
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer, UserSerializer, InvitationSerializer, InviteUserSerializer, RemoveInvitationSerializer, UpdateRSVPSerializer, AddReviewSerializer
from .permissions import IsOrganizerOrPublicReadOnly, IsOrganizer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrPublicReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['location', 'organizer']
    search_fields = ['title', 'location', 'organizer__username']

    def get_queryset(self):
        queryset = Event.objects.all()
        if self.action == 'list':
            # For list, show public events, user's own events, or events where user is invited
            queryset = queryset.filter(
                models.Q(is_public=True) | 
                models.Q(organizer=self.request.user) | 
                models.Q(invitations__user=self.request.user)
            ).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], serializer_class=RSVPSerializer)
    def rsvp(self, request, pk=None):
        event = self.get_object()
        user = request.user
        rsvp, created = RSVP.objects.get_or_create(event=event, user=user, defaults={'status': 'Going'})
        serializer = RSVPSerializer(rsvp, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], serializer_class=UpdateRSVPSerializer)
    def update_rsvp(self, request, pk=None):
        event = self.get_object()
        try:
            rsvp = RSVP.objects.get(event=event, user=request.user)
            serializer = UpdateRSVPSerializer(data=request.data)
            if serializer.is_valid():
                rsvp.status = serializer.validated_data['status']
                rsvp.save()
                rsvp_serializer = RSVPSerializer(rsvp)
                return Response(rsvp_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RSVP.DoesNotExist:
            return Response({'error': 'RSVP not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def reviews(self, request, pk=None):
        event = self.get_object()
        reviews = Review.objects.filter(event=event)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], serializer_class=AddReviewSerializer)
    def add_review(self, request, pk=None):
        event = self.get_object()
        user = request.user
        
        # Check if user already reviewed this event
        existing_review = Review.objects.filter(event=event, user=user).first()
        
        serializer = AddReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if existing_review:
            # Update existing review
            existing_review.rating = serializer.validated_data['rating']
            existing_review.comment = serializer.validated_data['comment']
            existing_review.save()
            review_serializer = ReviewSerializer(existing_review)
            return Response(review_serializer.data, status=status.HTTP_200_OK)
        else:
            # Create new review
            review = serializer.save(event=event, user=user)
            review_serializer = ReviewSerializer(review)
            return Response(review_serializer.data, status=status.HTTP_201_CREATED)
    def invite(self, request, pk=None):
        event = self.get_object()
        # Additional check (though IsOrganizer permission should handle this)
        if event.organizer != request.user:
            return Response({'error': 'Only organizer can send invitations'}, status=status.HTTP_403_FORBIDDEN)
        if event.is_public:
            return Response({'error': 'Cannot invite to public events'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = InviteUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = serializer.validated_data['user_id']
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        invitation, created = Invitation.objects.get_or_create(event=event, user=user)
        if created:
            invitation_serializer = InvitationSerializer(invitation)
            return Response(invitation_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'User already invited'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsOrganizer])
    def invitations(self, request, pk=None):
        event = self.get_object()
        # Additional check (though IsOrganizer permission should handle this)
        if event.organizer != request.user:
            return Response({'error': 'Only organizer can view invitations'}, status=status.HTTP_403_FORBIDDEN)
        
        invitations = Invitation.objects.filter(event=event)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizer], serializer_class=RemoveInvitationSerializer)
    def remove_invitation(self, request, pk=None):
        event = self.get_object()
        # Additional check (though IsOrganizer permission should handle this)
        if event.organizer != request.user:
            return Response({'error': 'Only organizer can remove invitations'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RemoveInvitationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = serializer.validated_data['user_id']
        
        try:
            # Find the user
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Find and remove the invitation for this user and event
            invitation = Invitation.objects.get(event=event, user=user)
            invitation.delete()
            return Response({'message': f'Invitation for {user.username} removed'}, status=status.HTTP_204_NO_CONTENT)
        except Invitation.DoesNotExist:
            return Response({'error': f'No invitation found for user {user.username} in this event'}, status=status.HTTP_404_NOT_FOUND)
