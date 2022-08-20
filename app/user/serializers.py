"""
Serializes for the User API View.
"""

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta():
        model = get_user_model()
        fields = ['email', 'password', 'name']

        ## Tells any definitions that the API will set
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return user with encrypted password"""
        ## Override serializer behavior
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""

        # pop used to remove the value (default = None)
        password = validated_data.pop('password', None)

        ## Instance defines the model being updated
        user = super().update(instance, validated_data)

        ## If Password is specified, then set the new password
        if password:
            user.set_password(password)
            user.save()

        ## Return User due to that being the default
        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for User Auth TOken"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style = {'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and Authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request = self.context.get('request'),
            username = email,
            password = password
        )

        if not user:
            msg = _('Unable to Authenticate with Provided Credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user

        return attrs

