import numpy as np
import random

def image_to_scaled_array(image):
    img_array = np.array(image.convert("L"))

    # interpolate pixel values to be between 0 and 9
    scaled_array = np.interp(img_array, (img_array.min(), img_array.max()), (0, 9))
    # round and convert to integers
    rounded_array = np.round(scaled_array).astype(int)

    return rounded_array


def random_pattern_generator(width, height):
    assert width * height % 2 == 0, "Cannot find pattern for image with an odd number of pixels"

    dominoes = set() # contains tuples of (row, col, row2, col2)

    grid = np.full((height, width), -1)
    i, j = 0, 0
    empty_cell_exists = True
    while empty_cell_exists:
        # place rectangle randomly at position (i,j), (i+1,j), or (i,j), (i, j+1)
        orientation = random.randint(0,1)
        if orientation == 0:
            dominoes.add((i, j, i+1, j))
            grid[i][j] = 1
            grid[i+1][j] = 1
        else:
            dominoes.add((i, j, i, j+1))
            grid[i][j] = 1
            grid[i][j+1] = 1

        # while there exists (i, j), an empty cell with three occupied orthogonal neighbours and all regions of empty connected cells are of even size
        empty_cells_list = list(zip(np.where(grid == -1)[0], np.where(grid == -1)[1]))
        while len(empty_cells_list) > 0 and len(find_empty_orthogonal_neighbors(grid, empty_cells_list[0][0], empty_cells_list[0][1])) == 1 and not find_odd_empty_regions(grid):
            i, j = empty_cells_list[0]
            adjacent_empty_cell = find_empty_orthogonal_neighbors(grid, i, j)[0]
            dominoes.add((i, j, adjacent_empty_cell[0], adjacent_empty_cell[1]))
            grid[i][j] = 1
            grid[adjacent_empty_cell[0]][adjacent_empty_cell[1]] = 1
            # update empty cells list
            empty_cells_list = list(zip(np.where(grid == -1)[0], np.where(grid == -1)[1]))

        # if there is a region of an odd number of connected empty cells in the grid then wipe out part of the grid
        if find_odd_empty_regions(grid):
            # clear out 2 prior rows
            new_dominoes = set(filter(lambda x: (x[1] < j-2) and (x[3] < j-2) , dominoes))
            for a, b, c, d in dominoes - new_dominoes:
                grid[a][b] = -1
                grid[c][d] = -1
            dominoes = new_dominoes

        # find next empty cell
        empty_cells_list = list(zip(np.where(grid == -1)[0], np.where(grid == -1)[1]))
        if len(empty_cells_list) > 0:
            i, j = empty_cells_list[0]
        else:
            empty_cell_exists = False

    visualize_domino_grid(width, height, dominoes)
    return dominoes

def find_empty_orthogonal_neighbors(grid, i, j):
    empty_neighbors = []
    for m, n in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]:
        if 0 <= m < len(grid) and 0 <= n < len(grid[0]) and grid[m][n] == -1:
            empty_neighbors.append((m, n))
    return empty_neighbors


def find_odd_empty_regions(grid):
    visited = set()
    region_counts = []

    empty_cells = set(zip(np.where(grid == -1)[0], np.where(grid == -1)[1]))
    if len(empty_cells) == 0:
        return False

    def dfs(grid, visited, i, j):
        # add to visited
        visited.add((i, j))
        return sum([dfs(grid, visited, r, c) if (r, c) in empty_cells and (r, c) not in visited else 0 for r,c in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]]) + 1

    # perform dfs until all empty cells have been visited
    while not visited == empty_cells:
        i, j = list(empty_cells - visited)[0]
        region_counts.append(dfs(grid, visited, i, j))

    # returns True if odd empty regions exist, otherwise False
    return len(list(filter(lambda x : x%2 == 1, region_counts))) > 0


def visualize_domino_grid(width, height, dominoes):
    counter = 0
    grid = np.full((height, width), -1)
    for a, b, c, d in dominoes:
        grid[a][b] = counter
        grid[c][d] = counter
        counter += 1

    print("===================")
    print(grid)
    print("===================")

if __name__ == '__main__':
    grid = np.array([[1,-1,1], [1,-1, 1], [1,1,-1]])
    # empty_cells = np.where(grid == 0)
    # print(list(zip(empty_cells[0], empty_cells[1])))

    # print(find_odd_empty_regions(np.array([[-1,  1,  -1],
    #                                        [ 1,  1,  -1],
    #                                        [ 1,  -1,  -1]])))

    # print(find_empty_orthogonal_neighbors(grid, 1, 1))

    random_pattern_generator(2,4)
