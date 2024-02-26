from yandex_map.yandex_map import (
    search_business, 
    get_coordinates,
    show_map,
    get_map,
    del_map
)


coords = get_coordinates(input())
image = get_map(coords, spn="0.05", pt=search_business(coords, "аптека"))
show_map(image)
del_map(image)