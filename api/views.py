from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework import status

# Create your views here.

@api_view(['GET'])
def hello(request):
    return Response({"message": "Hello from Django!"})

@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=400)
    user = User.objects.create_user(username=username, password=password)
    return Response({'message': 'User registered successfully'}, status=201)