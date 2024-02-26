import requests
import os
from PIL import Image
from random import uniform


# Мой апи ключ geocoder'a
api_key = '42838384-31ec-40af-b8a9-354fb89aa371'

# Лицейский апи ключ geocoder'a
# api_key = '40d1649f-0493-4b70-98ba-98533de7710b'

# Дополнительный апи ключ geocoder'a
# api_key = 'ea7ddb7a-83f0-4e59-84d9-e3ee28a40303'

# Мой api ключ для поиска организаций
# business_api ='1c4198a5-89b5-4f5e-8d5a-6e8dd37b960c'

# Лицейский апи ключ для поиска организаций
business_api = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'


def get_coordinates(place: str, format: str="json"):
    """
    Функция возвращает координаты обьекта на карте по его названию
    """
    link = f'http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={place}&format={format}'
    response = requests.get(link)
    if response:
        data = response.json()
        object = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coords = object["Point"]["pos"]
        return list(map(float, coords.split()))
    

def get_map(center: tuple[int], size: tuple[int]=[600, 450], way: tuple[int]=False, spn: str="0.005", map_format: str="map", pt: str=None):
    """
    Функция для создания изображения карты по переданным аргументам

    Параметр map_format может принимать следующие значения:
        map - карта схема местности
        sat - снимок спутника
        trf - карта автодорог
        skl - географические объекты
    """
    # Преобразуем параметры для удобства пользования
    x, y = map(str, center)
    width, height = map(str, size)

    map_link = f"https://static-maps.yandex.ru/1.x/?l={map_format}&ll={x},{y}&size={width},{height}&spn={spn},{spn}"
    # Если передан дополнительный маршрут
    if way:
        map_link += f"&pl={','.join(list(map(str, way)))}"
    if pt is not None:
        map_link += f"&{pt}"
    
    content = requests.get(map_link).content
    map_file = f"{x}-{y}.png"
    with open(map_file, 'wb') as map_1:
        map_1.write(content)
    return map_file 


def del_map(map: str):
    """
    Функция удаления изображения файла из файловой системы
    """
    os.remove(map)


def show_map(map: str):
    """
    Функция для просмотра получившейся карты
    """
    with Image.open(map) as img:
        img.show()


def random_spn(start: float, stop: float):
    """
    Функция генерирует случайный коэфициент масштабирования карты 
    исходя из заданных пределов
    """
    return uniform(start, stop)


def get_place(coord: tuple[int], type_place: str="house"):
    """
    Функция распознавания района по переданным координатам
    Исходя из параметра type_place можно получить следующие данные:
        house — дом;
        street — улица;
        metro — станция метро;
        district — район города;
        locality — населенный пункт (город/поселок/деревня/село)
    """
    x, y = list(map(str, coord))
    link = f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={x},{y}&kind={type_place}&format=json"
    response = requests.get(link)
    if response:
        data = response.json()
        object = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        dist = object["metaDataProperty"]["GeocoderMetaData"]["text"]
        return dist
    

def search_business(coord: list[int], type_business: str, count: int=10):
    """
    Функция нахождения объектов инфраструктуры города
    Параметр type_business принимает тип искомого объкта,
    будь это банк или аптека
    """
    search_api_server = "https://search-maps.yandex.ru/v1/"
    search_params = {
        "apikey": business_api,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": ",".join(list(map(str, coord))),
        "type": "biz"
    }
    response = requests.get(search_api_server, params=search_params)
    if response:
        list_points = []
        data = response.json()
        for index, business in enumerate(data["features"]):
            point = f'{business["geometry"]["coordinates"][0]},{business["geometry"]["coordinates"][1]},pm2'
            try:
                time_work = business["properties"]["CompanyMetaData"]["Hours"]["text"]
                if 'круглосуточно' in time_work:
                    point += "gnm"
                else:
                    point += "blm"
            except Exception:
                point += "grm"
            list_points.append(point)
        return f"pt={'~'.join(list_points)}"