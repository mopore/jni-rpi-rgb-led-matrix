import math
from scipy.interpolate import griddata
import numpy as np
import json

VALUE_RANGE = 100
MINTEMP = 20.0  # low range of the sensor (this will be blue on the screen)
MAXTEMP = 32.0  # high range of the sensor (this will be red on the screen)


def map_value(x, out_min, out_max):
    if x < MINTEMP:
        x = MINTEMP
    if x > MAXTEMP:
        x = MAXTEMP
    return (x - MINTEMP) * (out_max - out_min) / (MAXTEMP - MINTEMP) + out_min


def level_and_interpolate(orig_data: list[list[float]]) -> np.ndarray:
    pixels = []
    for row in orig_data:
        pixels = pixels + row
    pixels = [map_value(p, 0, VALUE_RANGE - 1) for p in pixels]

    # pylint: disable=invalid-slice-index
    points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
    grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
    # pylint: enable=invalid-slice-index

    # perform interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")
    return bicubic


def as_sensor_data(dict) -> list[list[float]]:
    data_array = dict["sensor_data"]
    return data_array


def json_to_interpolated_array(json_string: str | None) -> np.ndarray | None:
    data32x32: np.ndarray | None = None
    if json_string is not None:
        orig_data: list[list[float]] = json.loads(
            json_string, object_hook=as_sensor_data
        )
        data32x32 = level_and_interpolate(orig_data)      
    return data32x32
