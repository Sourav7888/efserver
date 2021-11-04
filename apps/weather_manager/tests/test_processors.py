from apps.weather_manager.processors import calculate_closest_station
import pandas as pd


class TestProcessors:
    def in_calculate_closest_station(self):
        return pd.DataFrame(
            [
                {
                    "pk_id": 1,
                    "climate_id": "1017099",
                    "station_name": "SATURNA CAPMON CS",
                    "province": "BC",
                    "latitude": 48.77502,
                    "longitude": -123.128075,
                },
                {
                    "pk_id": 2,
                    "climate_id": "1018598",
                    "station_name": "VICTORIA UNIVERSITY CS",
                    "province": "BC",
                    "latitude": 48.457,
                    "longitude": -123.30461,
                },
                {
                    "pk_id": 3,
                    "climate_id": "1018611",
                    "station_name": "VICTORIA GONZALES CS",
                    "province": "BC",
                    "latitude": 48.413303,
                    "longitude": -123.324776,
                },
            ]
        )

    def out_calculate_closest_station(self):
        return {
            "pk_id": 3,
            "climate_id": "1018611",
            "station_name": "VICTORIA GONZALES CS",
            "province": "BC",
            "latitude": 48.413303,
            "longitude": -123.324776,
            "point_lat": 0.8377580409572782,
            "point_long": -2.1467549799530254,
            "distance": 14703.70883283135,
        }

    def test_calculate_closest_station(
        self, in_calculate_closest_station, out_calculate_closest_station
    ):
        station = calculate_closest_station(
            self.in_calculate_closest_station(), lat=48, long=-123
        )

        self.assertEqual(station, self.out_calculate_closest_station())
