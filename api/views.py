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

from .models import Conversation, ChatMessage
import uuid

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
MODEL = 'mistralai/mistral-7b-instruct'
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
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        user_message = data.get('message')
        session_id = data.get('session_id') or str(uuid.uuid4())
        user = request.user if request.user.is_authenticated else None

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Save user message
        ChatMessage.objects.create(
            user=user,
            session_id=session_id,
            sender='user',
            message=user_message
        )

        try:
            headers = {
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
            }
            payload = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Dr. Jose Rizal, a Filipino national hero. Respond with thoughtfulness and nationalistic insight."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    },
                ],
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()  # Raise an exception for HTTP errors

            result = response.json()
            bot_reply = result['choices'][0]['message']['content']

        except Exception as e:
            print("OpenRouter Error:", e)
            bot_reply = "Sorry, I could not fetch a response."

        # Save bot response
        ChatMessage.objects.create(
            user=user,
            session_id=session_id,
            sender='rizal',
            message=bot_reply
        )

        return JsonResponse({'response': bot_reply, 'session_id': session_id})

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)



@csrf_exempt
def get_conversation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')

        user = request.user if request.user.is_authenticated else None

        if user:
            messages = ChatMessage.objects.filter(user=user).order_by('timestamp')
        else:
            messages = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')

        message_list = [
            {'sender': msg.sender, 'text': msg.message} for msg in messages
        ]
        return JsonResponse({'messages': message_list})
