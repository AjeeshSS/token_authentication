from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter

from .serializers import UserRegisterSerializer, UserDataSerializer

from django.http import Http404
from django.contrib.auth import get_user_model
User = get_user_model()   
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class register(APIView):
    """View for registering new user."""
    
    def post (self, request, format=None):
        serializer =  UserRegisterSerializer(data=request.data)
        data={}
        if serializer.is_valid():
            account=serializer.save()
            data['response']='registered'
            data['username']=account.username
            data['email']=account.email
            token, create=Token.objects.get_or_create(user=account)
            data['token']=token.key
        else:
            data=serializer.errors
        return Response(data)
    
class getuser(APIView):
    """get a username and id from the token"""
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if cache.get('cacheContent'):
            print('data from cache.')
            content = cache.get('cacheContent')
        else:
            content={'user':str(request.user), 'userid':str(request.user.id)}
            print('data from db.')
            cache.set('cacheContent', content)
        return Response(content)
    
class userDetails(APIView):
    """get user details and update view"""
    
    def get_object(self, pk):
        """function to get user details"""
        try:
            if cache.get('userCache'):
                print('data from cache.')
                user = cache.get('userCache')
            else:
                user = User.objects.get(pk=pk)
                print('data from db.')
                cache.set('userCache', user)
            return user
        except:
            raise Http404
            
    def get(self, request, pk, format=None):
        """view for getting user details."""
        userData = self.get_object(pk)
        serializer=UserDataSerializer(userData)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        """view for updating user details."""
        userData = self.get_object(pk)
        serializer=UserDataSerializer(userData, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'message':'error', 'error':serializer.errors})
    
    def delete(self, request, pk, format=None):
        """view to delete a user."""
        userData = self.get_object(pk)
        userData.delete()
        return Response({'message':'user deleted!!'})
    
class setPagination(PageNumberPagination):
    """set how many data shown in a page."""
    page_size = 2
    
class paginationAPI(ListAPIView):
    """View for pagination."""
    queryset=User.objects.all()
    serializer_class = UserDataSerializer
    pagination_class=setPagination
    filter_backends=(SearchFilter,)
    search_fields = ('username', 'email', 'first_name','last_name')




