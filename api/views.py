from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework import status

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import requests
import os

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
MODEL = 'openrouter/gpt-3.5-turbo'
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


@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')

        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are Jose Rizal, a national hero and intellectual. Respond with wisdom from your writings and ideals."},
                {"role": "user", "content": user_message},
            ],
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )

            result = response.json()
            bot_reply = result['choices'][0]['message']['content']

            return JsonResponse({'response': bot_reply})

        except Exception as e:
            print('OpenRouter error:', e)
            return JsonResponse({'response': 'Sorry, something went wrong contacting OpenRouter.'}, status=500)