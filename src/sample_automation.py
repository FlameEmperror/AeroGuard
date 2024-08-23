from heapq import heappush, heappop
import math
import time
import requests
import dronekit
import cv2
import numpy as np

coordinates = [(lat1, long1), (lat2, long2), (lat3, long3), ...]

def dijkstra(start, graph):
    distances = {vertex: math.inf for vertex in graph}
    distances[start] = 0
    queue = [(0, start)]
    while queue:
        current_distance, current_vertex = heappop(queue)
        if current_distance > distances[current_vertex]:
            continue
        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heappush(queue, (distance, neighbor))
    return distances
graph = {}
for i in range(len(coordinates)):
    graph[i] = {}
    for j in range(i+1, len(coordinates)):
        distance = math.sqrt((coordinates[i][0] - coordinates[j][0])*2 + (coordinates[i][1] - coordinates[j][1])*2)
        graph[i][j] = distance
        graph[j][i] = distance
distances = dijkstra(0, graph)
order = sorted(range(len(distances)), key=lambda k: distances[k])
order = [x+1 for x in order] # convert to 1-indexed


def fly_to_coordinates():
    drone.takeoff()
    time.sleep(5)
    for i in order:
        print("Going to coordinate", i)
        latitude, longitude = coordinates[i-1]
        drone.goto(latitude, longitude, 10) # move to the next coordinate
        time.sleep(5)
    # Take a picture and upload it
    picture = take_picture()
    upload_picture(picture, latitude, longitude)
    upload_gps_coordinates()
    time.sleep(3)
    drone.go_home()
    time.sleep(5)
    drone.land()

# Function to detect and upload drone's GPS coordinates
def upload_gps_coordinates():
    # Connect to drone using telemetry radio
    vehicle = dronekit.connect('/dev/serial0', baud=57600, wait_ready=True)

    # Wait for GPS fix
    while not vehicle.gps_0.fix_type:
        time.sleep(1)

    # Get drone's GPS coordinates
    lat = vehicle.location.global_frame.lat
    lon = vehicle.location.global_frame.lon

    # Upload GPS coordinates to server
    url = "https://example.com/upload_gps_coordinates"
    payload = {'lat': lat, 'lon': lon}
    response = requests.post(url, data=payload)

    # Close telemetry radio connection
    vehicle.close()

def take_picture(drone):
    # Get the frame from the drone camera
    frame = drone.get_frame()
    
    # Convert the frame to a format compatible with OpenCV
    img_array = np.frombuffer(frame.image, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    

# Save the image to a file
    cv2.imwrite("drone_picture.jpg", img)
    
    # Return the image as a numpy array
    return img

def upload_picture_to_server(picture, server_url):
    with open(take_picture(drone), 'rb') as picture_file:
        response = requests.post(https://example.com/upload_picture, files={'picture': picture_file})
