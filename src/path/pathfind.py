from collections import deque


# Function to create graph from the chosen coordinates, representing as an adjacency list
def create_graph(coords, scale_factor, dist_threshold):
    scaled_coords = [
        tuple(int(element / scale_factor) for element in coord) for coord in coords
    ]
    graph = {point: [] for point in scaled_coords}

    num_points = len(scaled_coords)
    for i in range(num_points):
        for j in range(i + 1, num_points):
            p1 = (scaled_coords[i][0], scaled_coords[i][1])
            p2 = (scaled_coords[j][0], scaled_coords[j][1])

            # Check if points are within threshold on x or y axes
            if (abs(p1[0] - p2[0]) <= dist_threshold and p1[1] == p2[1]) or (
                abs(p1[1] - p2[1]) <= dist_threshold and p1[0] == p2[0]
            ):
                graph[p1].append(p2)
                graph[p2].append(p1)

    return graph, scaled_coords


# Function to create flow field starting at goal coordinate using breadth first search
def create_flow_field(graph, all_points, goal_coordinate):
    # Integration field stores shortest distance from each point to the goal
    integration_field = {point: float("inf") for point in all_points}
    integration_field[goal_coordinate] = 0

    queue = deque([goal_coordinate])

    while queue:
        current_node = queue.popleft()
        current_distance = integration_field[current_node]

        for neighbor in graph[current_node]:
            # If a shorter path to a neighbor is found, update it and add to queue
            if integration_field[neighbor] > current_distance + 1:
                integration_field[neighbor] = current_distance + 1
                queue.append(neighbor)

    # Generate flow field vectors by finding neighbor with lowest distance for each point
    flow_field = {}
    for point in all_points:
        if point == goal_coordinate:
            flow_field[point] = (0, 0)
            continue

        min_distance = float("inf")
        best_neighbor = None

        # Find neighbor with minimum distance to the goal
        for neighbor in graph[point]:
            if integration_field[neighbor] < min_distance:
                min_distance = integration_field[neighbor]
                best_neighbor = neighbor

        # If a path exists, set the vector
        if best_neighbor:
            x_dir = best_neighbor[0] - point[0]
            x_dir = 1 if x_dir > 0 else (-1 if x_dir < 0 else 0)
            y_dir = best_neighbor[1] - point[1]
            y_dir = 1 if y_dir > 0 else (-1 if y_dir < 0 else 0)
            flow_field[point] = (x_dir, y_dir)
        else:
            flow_field[point] = None  # Unreachable point

    return flow_field
