from tkinter import messagebox
import heapq
from db_utils import get_object_type_name

# Функция для построения графа городов
def build_graph(conn):
    cursor = conn.cursor()
    query = "SELECT FromCityID, ToCityID, DistanceKm FROM Routes"
    cursor.execute(query)
    graph = {}
    for from_city, to_city, distance in cursor.fetchall():
        if from_city not in graph:
            graph[from_city] = []
        graph[from_city].append((to_city, distance))
        # Двусторонний маршрут
        if to_city not in graph:
            graph[to_city] = []
        graph[to_city].append((from_city, distance))
    return graph


# Алгоритм поиска кратчайшего пути
def find_shortest_path(graph, start, end):
    distances = {node: float('inf') for node in graph}
    previous_nodes = {node: None for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end:
            break

        for neighbor, weight in graph.get(current_node, []):
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Восстановление пути
    path, current = [], end
    while previous_nodes[current] is not None:
        path.append(current)
        current = previous_nodes[current]
    path.append(start)
    path.reverse()

    return path, distances[end]

# Функция для получения объектов инфраструктуры на маршруте
def get_infrastructure_on_route(conn, route_id):
    cursor = conn.cursor()
    query = """
        SELECT ObjectType, ObjectName, DistanceFromCity
        FROM InfrastructureObjects
        WHERE OnRouteID = ?
    """
    cursor.execute(query, (route_id,))
    results = cursor.fetchall()
    infrastructure = []
    for obj_type, obj_name, distance_from_city in results:
        obj_type_name = get_object_type_name(conn, obj_type)  # из db_utils
        infrastructure.append((obj_type_name, obj_name, distance_from_city))
    return infrastructure


# Основная логика маршрута с расчётами
def calculate_route(conn, city_from, city_to, avg_speed, fuel_consumption, fuel_tank_capacity):
    # Проверка наличия городов в базе данных
    from db_utils import check_city_exists, get_city_name  # Импорт функций для db_utils в локальный scope
    from_city = check_city_exists(conn, city_from)
    to_city = check_city_exists(conn, city_to)

    if not from_city or not to_city:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните оба поля.")
        return

    from_city_id = from_city[0]
    to_city_id = to_city[0]

    # Построение графа и поиск кратчайшего пути
    graph = build_graph(conn)
    shortest_path, total_distance = find_shortest_path(graph, from_city_id, to_city_id)

    # Расчёты
    total_time = total_distance / avg_speed  # Время в пути (часы)
    fuel_range = fuel_tank_capacity / fuel_consumption * 100  # Запас хода на полном баке (км)
    stops_for_fuel = []
    stops_for_sleep = []
    current_distance = 0
    driving_time = 0

    all_infrastructure = []
    city_names = [get_city_name(conn, city_id) for city_id in shortest_path]

    for i in range(len(shortest_path) - 1):
        cursor = conn.cursor()
        query = """
            SELECT RouteID, DistanceKm FROM Routes
            WHERE (FromCityID = ? AND ToCityID = ?) OR (FromCityID = ? AND ToCityID = ?)
        """
        cursor.execute(query, (shortest_path[i], shortest_path[i + 1], shortest_path[i + 1], shortest_path[i]))
        route = cursor.fetchone()
        if route:
            route_id, segment_distance = route
            current_distance += segment_distance
            driving_time += segment_distance / avg_speed

            infrastructure = get_infrastructure_on_route(conn, route_id)
            all_infrastructure.extend(
                [(obj[0], obj[1], obj[2], f"{city_names[i]} -> {city_names[i + 1]}") for obj in infrastructure])

            if current_distance > fuel_range:
                fuel_stations = [obj for obj in infrastructure if obj[0] == "АЗС"]
                if fuel_stations:
                    stops_for_fuel.append((fuel_stations[0][1], fuel_stations[0][2]))  # Название и адрес первой АЗС
                    current_distance = 0

            if driving_time > 8:  # Максимум 9 часов за рулём
                hotels = [obj for obj in infrastructure if obj[0] == "Отель"]
                if hotels:
                    stops_for_sleep.append((hotels[0][1], hotels[0][2]))  # Название и адрес отеля
                    driving_time = 0

    overnight_stays = total_time // 8  # Остановки на ночлег

    return (city_names, total_distance, total_time, stops_for_fuel, stops_for_sleep, all_infrastructure)