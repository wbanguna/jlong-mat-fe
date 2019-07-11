from archiver.tsdb import ServiceInfluxDB
from haversine import Unit, haversine
import json
import datetime
import time


def calc_dist(now, past):
    curr_loc = (now['lat'], now['long'])
    past_loc = (past['lat'], past['long'])
    distance = haversine(curr_loc, past_loc, unit=Unit.MILES)
    return distance


def calc_time_diff(time1, time2):
    t1_s = time1 / 1000
    t2_s = time2 / 1000
    t1 = datetime.datetime.fromtimestamp(t1_s).strftime('%Y-%m-%d %H:%M:%S.%f')
    t2 = datetime.datetime.fromtimestamp(t2_s).strftime('%Y-%m-%d %H:%M:%S.%f')
    start_time = datetime.datetime.strptime(t1, '%Y-%m-%d %H:%M:%S.%f')
    end_time = datetime.datetime.strptime(t2, '%Y-%m-%d %H:%M:%S.%f')
    time_diff = (start_time - end_time)
    time_diff_seconds = datetime.timedelta.total_seconds(time_diff)
    return time_diff_seconds


def race_events(car):
    race_table_positions = ServiceInfluxDB().get_race_table(car)
    current_position = race_table_positions[0]
    previous_position = race_table_positions[1]
    if current_position < previous_position:
        race_event = "Racing Car " + str(car['carIndex']) + \
                     " has raced into position " + str(current_position) + " at Silverstone"
        event = json.dumps({"timestamp": int(time.time() * 1000.0), "text": race_event})
        return event
    elif current_position > previous_position:
        race_event = "Racing Car " + str(car['carIndex']) + \
                     " has dropped down from position " + str(previous_position) + \
                     " to position " + str(current_position)
        event = json.dumps({"timestamp": int(time.time() * 1000.0), "text": race_event})
        return event
    elif (current_position == 1) and (current_position < previous_position):
        race_event = "This is the British Grand Prix and Racing Car " + str(car['carIndex']) + \
                     " has taken the lead at Silverstone! It must be a Mclaren!!"
        event = json.dumps({"timestamp": int(time.time() * 1000.0), "text": race_event})
        return event
    elif (current_position == 6) and (current_position > previous_position):
        race_event = "Not an afternoon to remember so far for Racing Car " + str(car['carIndex']) + \
                     "as they fall to the back of the race"
        event = json.dumps({"timestamp": int(time.time() * 1000.0), "text": race_event})
        return event
    else:
        pass


def car_position(car):
    car_rank = ServiceInfluxDB().get_car_positon(car)
    position = car_rank[0]['position']
    race_position = json.dumps(
        {"timestamp": car['timestamp'], "carIndex": car['carIndex'], "type": "POSITION", "value": position})
    return race_position


def race_positions():
    measurements = ServiceInfluxDB().get_mean_speed()
    points = list(measurements[0].get_points())
    cars_total_distance_travelled = {}
    index = -1

    for car in points:
        index += 1
        start_time = list(measurements[1].get_points(tags={'carIndex': str(index)}))
        latest_time = list(measurements[2].get_points(tags={'carIndex': str(index)}))
        time_diff_seconds = calc_time_diff(latest_time[0]['timestamp'], start_time[0]['timestamp'])
        total_distance_travelled = (time_diff_seconds / 3600) * car['mean']
        cars_total_distance_travelled[str(index)] = total_distance_travelled

    sorted_cars = sorted(cars_total_distance_travelled.items(), key=lambda x: x[1])
    ServiceInfluxDB().archive_race_position(sorted_cars)


def car_status_speed(car):
    measurement = ServiceInfluxDB().get_last_gps(car)
    if len(measurement):
        distance = calc_dist(car['location'], measurement[0])
        time_diff_seconds = calc_time_diff(car['timestamp'], measurement[0]['timestamp'])
        speed = distance / time_diff_seconds * 3600
        data_speed = json.dumps(
            {"timestamp": car['timestamp'], "carIndex": car['carIndex'], "type": "SPEED", "value": speed})
        ServiceInfluxDB().archive_gps(car, speed)
        return data_speed
    else:
        ServiceInfluxDB().archive_gps(car)
