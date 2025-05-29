# detection/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
import base64
import cv2
import numpy as np
from .ml_model import detect_and_draw,detect_and_estimate_depth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

@api_view(['POST'])
def process_image_api(request):
    
    # Expect JSON with one base64 image string under 'image'
    b64_img = request.data.get("image")
    if not b64_img:
        return Response({"error": "No image provided"}, status=400)
    
    # Decode base64 image to OpenCV format
    img_data = base64.b64decode(b64_img.split(",")[-1])  # handle data URI if present
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    copy_img = img.copy()
    
    # Run detection and get annotated image
    depth_map, processed_img = detect_and_estimate_depth(img)
    
    # depth_map = cv2.resize(depth_map, (copy_img.shape[1], copy_img.shape[0]))
    _, buffer_depth = cv2.imencode('.jpg', depth_map)
    depth_b64 = base64.b64encode(buffer_depth).decode('utf-8')
   
    # Encode images back to base64 to send back:
    _, buffer_orig = cv2.imencode('.jpg', copy_img)
    orig_b64 = base64.b64encode(buffer_orig).decode('utf-8')

    _, buffer_proc = cv2.imencode('.jpg', processed_img)
    proc_b64 = base64.b64encode(buffer_proc).decode('utf-8')
    
    return Response({
        "original_image": f"data:image/jpeg;base64,{orig_b64}",
        "processed_image": f"data:image/jpeg;base64,{proc_b64}",
        "depth_map": f"data:image/jpeg;base64,{depth_b64}"  
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('client')
        else:
            return render(request, 'detection/login.html', {'error': 'Invalid credentials'})
    return render(request, 'detection/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return render(request, 'detection/register.html', {'error': "Passwords don't match"})

        if User.objects.filter(username=username).exists():
            return render(request, 'detection/register.html', {'error': "Username already taken"})

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect('login')  # Change this to your post-login page

    return render(request, 'detection/register.html')



import requests
from django.shortcuts import render
from django.http import JsonResponse

AZURE_MAPS_KEY = 'Enter your Azure Maps key here'  # Replace with your actual key

def routing_page(request):
    # Render the routing form page
    return render(request, 'detection/routes.html')

def get_route(request):
    if request.method == 'POST':
        start = request.POST.get('source')
        end = request.POST.get('destination')

        if not start or not end:
            return JsonResponse({'error': 'Please provide both start and end locations.'}, status=400)

        # Helper function to get coordinates from Azure Maps Search API
        def get_coords(location):
            url = "https://atlas.microsoft.com/search/address/json"
            params = {
                'subscription-key': AZURE_MAPS_KEY,
                'api-version': '1.0',
                'query': location,
                'limit': 1
            }
            response = requests.get(url, params=params)
            data = response.json()
            if data.get('results'):
                position = data['results'][0]['position']
                return position['lon'], position['lat']
            return None, None

        start_lon, start_lat = get_coords(start)
        end_lon, end_lat = get_coords(end)

        if None in [start_lon, start_lat, end_lon, end_lat]:
            return JsonResponse({'error': 'Could not find coordinates for one or both locations.'}, status=400)

        # Get route directions from Azure Maps Route API
        route_url = (
            f"https://atlas.microsoft.com/route/directions/json"
            f"?subscription-key={AZURE_MAPS_KEY}"
            f"&api-version=1.0"
            f"&query={start_lat},{start_lon}:{end_lat},{end_lon}"
            f"&routeRepresentation=summaryOnly"
            f"&instructionsType=text"
        )
        route_response = requests.get(route_url)
        route_data = route_response.json()

        if 'routes' not in route_data or len(route_data['routes']) == 0:
            return JsonResponse({'error': 'No route found.'}, status=400)

        # Extract instructions from guidance.instructions
        guidance = route_data['routes'][0].get('guidance', {})
        instructions = []
        for step in guidance.get('instructions', []):
            instructions.append({
                'instruction': step.get('message', ''),
                'distance_meters': step.get('routeOffsetInMeters', 0)
            })

        return render(request, 'detection/routes.html', {
        'start': start,
        'end': end,
        'instructions': instructions,
        'start_lon': start_lon,
        'start_lat': start_lat,
        'end_lon': end_lon,
        'end_lat': end_lat,
        'AZURE_MAPS_KEY': AZURE_MAPS_KEY  # Pass your key safely
    })

