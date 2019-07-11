from influxdb import InfluxDBClient

class ServiceInfluxDB:

    def __init__(self, db_name: str = 'MAT-FE', host: str = 'influxdb', port: str = '8086'):
        self.client = InfluxDBClient(host, port)
        self.client.create_database(db_name)
        self.client.switch_database(db_name)

    def get_last_gps(self, car):
        rs = self.client.query('SELECT * FROM "MAT-FE"."autogen"."carCoordinates" GROUP BY * ORDER BY DESC LIMIT 1')
        points = list(rs.get_points(tags={'carIndex': str(car['carIndex'])}))
        return points

    def get_mean_speed(self):
        rs_mean_speed = self.client.query('SELECT MEAN("speed") FROM "MAT-FE"."autogen"."carCoordinates" '
                                          'GROUP BY "carIndex"')
        rs_first_time = self.client.query('SELECT * FROM "MAT-FE"."autogen"."carCoordinates" '
                                          'GROUP BY * ORDER BY ASC LIMIT 1')
        rs_last_time = self.client.query('SELECT * FROM "MAT-FE"."autogen"."carCoordinates" '
                                         'GROUP BY * ORDER BY DESC LIMIT 1')
        return rs_mean_speed, rs_first_time, rs_last_time

    def get_car_positon(self, car):
        rs_race_positions = self.client.query('SELECT * FROM "MAT-FE"."autogen"."racePosition"'
                                                ' GROUP BY * ORDER BY DESC LIMIT 1')
        car_rank = list(rs_race_positions.get_points(tags={'carIndex': str(car['carIndex'])}))
        return car_rank

    def get_race_table(self, car):
        rs_current_race_table = self.client.query('SELECT * FROM "MAT-FE"."autogen"."racePosition" '
                                                  'GROUP BY * ORDER BY DESC LIMIT 1')
        current_position_list = list(rs_current_race_table.get_points(tags={'carIndex': str(car['carIndex'])}))
        current_position = current_position_list[0]['position']
        rs_previous_race_table = self.client.query('SELECT * FROM "MAT-FE"."autogen"."racePosition" '
                                               'WHERE time > now() - 10s')
        previous_position_list = list(rs_previous_race_table.get_points(tags={'carIndex': str(car['carIndex'])}))
        previous_position = previous_position_list[0]['position']
        return current_position, previous_position

    def archive_gps(self, msg, speed=None):
        measurement = [
            {
                "measurement": 'carCoordinates',
                "tags": {
                    "carIndex": msg['carIndex']
                },
                "fields": {
                    "timestamp": msg['timestamp'],
                    "lat": msg['location']['lat'],
                    "long": msg['location']['long'],
                    "speed": speed
                }
            }
        ]
        print(measurement)
        self.client.write_points(measurement)

    def archive_race_position(self, cars):
        measurement = [
            {
                "measurement": 'racePosition',
                "tags": {
                    "carIndex": cars[5][0]
                },
                "fields": {
                    "total_distance_travelled": cars[5][1],
                    "position": 1,
                }
            },
            {
                "measurement": 'racePosition',
                "tags": {
                    "carIndex": cars[4][0]
                },
                "fields": {
                    "total_distance_travelled": cars[4][1],
                    "position": 2,
                }
            },
            {
                "measurement": 'racePosition',
                "tags": {
                    "carIndex": cars[3][0]
                },
                "fields": {
                    "total_distance_travelled": cars[3][1],
                    "position": 3,
                }
            },
            {
                "measurement": 'racePosition',
                "tags": {
                    "carIndex": cars[2][0]
                },
                "fields": {
                    "total_distance_travelled": cars[2][1],
                    "position": 4,
                }
            },
            {
                "measurement": 'racePosition',
                "tags": {
                    "carIndex": cars[1][0]
                },
                "fields": {
                    "total_distance_travelled": cars[1][1],
                    "position": 5,
                }
            },
            {
                "measurement": 'racePosition',
                "tags": {
                    "carIndex": cars[0][0]
                },
                "fields": {
                    "total_distance_travelled": cars[0][1],
                    "position": 6,
                }
            }
        ]
        self.client.write_points(measurement)