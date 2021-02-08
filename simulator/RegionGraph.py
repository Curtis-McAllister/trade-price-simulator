import sys
import heapq

from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['DND_Map']

regions = db.regions
trade_routes = db.trade_routes
terrain = db.terrain

caravan_speed = 20
sailing_speed = 100

terrain_speeds = {}

for terrain_type in terrain.find():
    terrain_speeds[terrain_type['terrain']] = terrain_type['travel_speed']


class Region:
    def __init__(self, id):
        # regional level
        self.id = id
        self.name = None
        self.prosperity = 0.0
        self.region_num = None
        self.commodities = []

        # trade route level
        self.adjacent_region = {}
        self.distance = sys.maxsize
        self.visited = False
        self.previous = False
        self.commodities = []

    def get_commodities(self):
        return self.commodities

    def add_commodity(self, commodity):
        self.commodities.append(commodity)

    def add_trade_route(self, neighbour, distance=0, route_type='land', terrain='smooth plains'):
        if route_type == 'land':
            speed = caravan_speed * terrain_speeds[terrain]
        else:
            speed = sailing_speed * terrain_speeds[terrain]

        self.adjacent_region[neighbour] = distance / speed

    def get_trade_routes(self):
        return self.adjacent_region.keys()

    def get_id(self):
        return self.id

    def get_trade_route_distance(self, neighbour):
        return self.adjacent_region[neighbour]

    def get_distance(self):
        return self.distance

    def set_distance(self, new_distance):
        self.distance = new_distance

    def set_previous(self, new_previous):
        self.previous = new_previous

    def set_visited(self):
        self.visited = True

    def __lt__(self, other):
        return (self.distance) < (other.distance)

    def __str__(self):
        return '{} adjacent: {}'.format(str(self.id), str(x.id for x in self.adjacent_region))


class TradeRoutes:
    def __init__(self):
        self.regions = {}
        self.region_count = 0

    def __iter__(self):
        return iter(self.regions.values())

    def add_region(self, region):
        self.region_count += 1
        new_region = Region(region)
        self.regions[region] = new_region
        return new_region

    def get_region(self, region_id):
        if region_id in self.regions:
            return self.regions[region_id]
        else:
            return None

    def add_trade_route(self, origin, destination, distance=0, type='land', terrain='smooth plains'):
        if origin not in self.regions:
            self.add_region(origin)
        if destination not in self.regions:
            self.add_region(destination)

        self.regions[origin].add_trade_route(self.regions[destination], distance, type, terrain)
        self.regions[destination].add_trade_route(self.regions[origin], distance, type, terrain)

    def get_regions(self):
        return self.regions.keys()

    def set_previous(self, current_region):
        self.previous = current_region

    def get_previous(self):
        return self.previous


def dijkstra(aGraph, start):
    print
    '''Dijkstra's shortest path'''
    # Set the distance for the start node to zero
    start.set_distance(0)

    # Put tuple pair into the priority queue
    unvisited_queue = [(v.get_distance(), v) for v in aGraph]
    print(unvisited_queue)
    heapq.heapify(unvisited_queue)

    while len(unvisited_queue):
        # Pops a vertex with the smallest distance
        uv = heapq.heappop(unvisited_queue)
        current = uv[1]
        current.set_visited()

        # for next in v.adjacent:
        for next in current.adjacent_region:
            # if visited, skip
            if next.visited:
                continue
            new_dist = current.get_distance() + current.get_trade_route_distance(next)

            if new_dist < next.get_distance():
                next.set_distance(new_dist)
                next.set_previous(current)
                print('updated : current = {} next = {} new_dist = {}'.format(current.get_id(), next.get_id(),
                                                                              next.get_distance()))
            else:
                print('not updated : current = {} next = {} new_dist = {}'.format(current.get_id(), next.get_id(),
                                                                                  next.get_distance()))

        # Rebuild heap
        # 1. Pop every item
        while len(unvisited_queue):
            heapq.heappop(unvisited_queue)
        # 2. Put all vertices not visited into the queue
        unvisited_queue = [(v.get_distance(), v) for v in aGraph if not v.visited]
        heapq.heapify(unvisited_queue)


def shortest(origin, path):
    if origin.previous:
        path.append(origin.previous.get_id())
        shortest(origin.previous, path)
    return


def calculate_distance(path):
    distance = 0

    for route in range(0, len(path)-1):
        distance += trade_regions.get_region(path[0]).get_trade_route_distance(trade_regions.get_region(path[1]))
        path.pop(0)

    return distance


if __name__ == '__main__':
    trade_regions = TradeRoutes()

    for region in regions.find():
        trade_regions.add_region(region['region_num'])

    for trade_route in trade_routes.find():
        trade_regions.add_trade_route(trade_route['origin'], trade_route['destination'], trade_route['distance'],
                                      trade_route['route_type'], trade_route['terrain_type'])

    dijkstra(trade_regions, trade_regions.get_region(13))

    target = trade_regions.get_region(30)
    path = [target.get_id()]
    shortest(target, path)
    shortest_path = path[::-1]

    print(shortest_path)
    print(calculate_distance(shortest_path))










