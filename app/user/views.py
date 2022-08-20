"""
Views for User API
"""

from rest_framework import generics # akin to generic views for APIs
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import authentication, permissions
from user.serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer # Set serializer for generic API View

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES # Shows the user interface for token

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    # Retrieve = HTTP GET, Update = HTTP PUT or PATCH

    serializer_class = UserSerializer

    ## Show Type of Authentication used in the system
    authentication_classes = [authentication.TokenAuthentication]

    ## Users who use this API must be authenticated
    permission_classes = [permissions.IsAuthenticated]

    ## Override get_object to get the specific user for the request.
    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user






