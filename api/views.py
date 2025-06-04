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
        data = json.loads(request.body)
        user_message = data.get('message')
        session_id = data.get('session_id') or str(uuid.uuid4())

        # Save user's message
        Conversation.objects.create(
            session_id=session_id,
            sender='user',
            message=user_message
        )
        ChatMessage.objects.create(sender='user', message=user_message, session_id=session_id)

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
            result = response.json()
            bot_reply = result['choices'][0]['message']['content']

            # Save bot response
            Conversation.objects.create(
                session_id=session_id,
                sender='rizal',
                message=bot_reply
            )
            ChatMessage.objects.create(sender='rizal', message=bot_reply, session_id=session_id)

            return JsonResponse({'response': bot_reply, 'session_id': session_id})

        except Exception as e:
            print("OpenRouter Error:", e)
            fallback = "Sorry, I could not fetch a response."

            # Save fallback response
            Conversation.objects.create(
                session_id=session_id,
                sender='rizal',
                message=fallback
            )
            ChatMessage.objects.create(sender='rizal', message=fallback, session_id=session_id)

            return JsonResponse({'response': fallback, 'session_id': session_id})

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@csrf_exempt
def get_conversation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')

        messages = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
        message_list = [
            {'sender': msg.sender, 'text': msg.message} for msg in messages
        ]
        return JsonResponse({'messages': message_list})