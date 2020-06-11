import random, math, itertools
import numpy as np
from pulp import *
from scipy.ndimage.measurements import label
from PIL import Image


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


# TODO: remove this function
def find_odd_empty_regions_old(grid):
    visited = set()
    region_counts = []

    empty_cells = set(zip(np.where(grid == -1)[0], np.where(grid == -1)[1]))
    if len(empty_cells) == 0:
        return False

    def dfs(grid, i, j):
        # add to visited
        visited.add((i, j))
        return sum([dfs(grid, r, c) if (r, c) in empty_cells and (r, c) not in visited else 0 for r,c in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]]) + 1

    # perform dfs until all empty cells have been visited
    while not visited == empty_cells:
        i, j = list(empty_cells - visited)[0]
        region_counts.append(dfs(grid, i, j))

    # returns True if odd empty regions exist, otherwise False
    return len(list(filter(lambda x : x%2 == 1, region_counts))) > 0



def find_odd_empty_regions(grid):
    # multiply by -1 so it finds the empty regions (where -1 means a cell is empty)
    # i.e. converts [[ -1  1 -1 ]] to [[ 1  0  1 ]]
    # because we want to find regions of -1's in the original grid
    new_grid = grid * -1
    new_grid[new_grid == -1] = 0

    labeled_grid, ncomponents = label(new_grid)
    for n in range(1, ncomponents + 1):
        if np.count_nonzero(labeled_grid == n) % 2 == 1:
            return True

    return False


def visualize_domino_grid(width, height, dominoes):
    counter = 0
    grid = np.full((height, width), -1)
    for a, b, c, d in dominoes:
        grid[a][b] = counter
        grid[c][d] = counter
        counter += 1

    print("\n rect_layout:")
    print("===================")
    print(grid)
    print("===================")

def generate_domino_graphics(imgSmall, width_in_pixels, height_in_pixels):
    rect_values = image_to_scaled_array(imgSmall)
    print("rectangle values")
    print(rect_values)
    rect_layout = random_pattern_generator(width_in_pixels, height_in_pixels)





    k = math.ceil(width_in_pixels*height_in_pixels / 2 / 55)
    rect_val_to_loc = generate_rect_val_to_loc(rect_layout, rect_values)
    num_dominos = width_in_pixels*height_in_pixels / 2
    print("SOLVING LP PROBLEM")
    solve_LP(k, rect_val_to_loc, num_dominos)
    solve_LP(k, rect_val_to_loc, num_dominos)




    # each domino image is 404 x 810
    background = Image.new('RGBA', (width_in_pixels*405, height_in_pixels*405), (255, 255, 255, 255))
    bg_w, bg_h = background.size

    for a,b,c,d in rect_layout:
        first_val = rect_values[a][b]
        second_val = rect_values[c][d]

        # get domino image and resize to dimensions that have 1:2 ratio
        domino_img = Image.open('./dominoes/' + str(first_val) + '-' + str(second_val) + '.png', 'r').resize((405, 810), Image.NEAREST)

        # if horizontal orientation, rotate image
        domino_img = domino_img.rotate(90, expand=True) if a == c else domino_img

        offset = (b*405, a*405)
        background.paste(domino_img, offset)

    background.save('out.png')
    return background






'''
An area is a set of all rectangles with identical pairs of costs in the pattern
Area j corresponds to a rectangle of cost (j_1,j_2)

k = number of sets of dominoes                                      math.ceil(width_in_pixels*height_in_pixels / 55)
capa_j = number of rectangles with identical values in area_j       len(rect_val_to_loc[area_vals[j]])
nbArea = total number of areas (nbArea ≤55)                         len(rect_val_to_loc) or len(area_vals)
'''
def solve_LP(k, rect_val_to_loc, num_dominos):
    # create list of domino values (where d_i = domino_vals[i])
    domino_vals = list(itertools.combinations_with_replacement([0,1,2,3,4,5,6,7,8,9], 2))

    # create list of area values ((a,b) = (j_1, j_2) = area_vals[j])
    area_vals = sorted(rect_val_to_loc.keys())

    # create function for computing the cost of placing domino i in rectangle j
    def cost(i, j):
        # since incoming values should be (low, high) we do not need to account for inverting the orientation because cost will be minimized as is
        cost_ij = (domino_vals[i][0]-area_vals[j][0])**2 + (domino_vals[i][1]-area_vals[j][1])**2
        # print("cost of (" + str(i) + ", " + str(j) + ") is " + str(cost_ij))
        return cost_ij

    ##################################
    #           LP Problem           #
    ##################################
    # declare problem to be a minimization LP problem
    prob = LpProblem("Domino Optimization Problem",LpMinimize)

    # define xij variables
    xij_vars = LpVariable.dicts("Xij", ((i, j) for i in range(len(domino_vals)) for j in range(len(area_vals))), lowBound=0, cat='Integer')

    # add main objective function
    prob += lpSum([cost(i,j)*xij_vars[(i,j)] for i in range(len(domino_vals)) for j in range(len(area_vals))])

    # add ﬁrst constraint of this linear program, which ensures that exactly k dominoes of each kind are assigned.
    for i in range(len(domino_vals)):
        # TODO: constraint was originally == k, but shouldn't we allow for not all dominoes of last set to be used? (i.e. k-1 is allowed too?)
        prob += lpSum([xij_vars[(i,j)] for j in range(len(area_vals))]) >= k-1
        prob += lpSum([xij_vars[(i,j)] for j in range(len(area_vals))]) <= k

    # add second constraint to ensure that no more than capa_j dominoes are placed in the same area
    for j in range(len(area_vals)):
        capa_j = len(rect_val_to_loc[area_vals[j]])
        prob += lpSum([xij_vars[(i,j)] for i in range(len(domino_vals))]) <= capa_j

    # add third constraint to ensure that sum of all x_ij values is num_dominos
    prob += lpSum([xij_vars[(i,j)] for i in range(len(domino_vals)) for j in range(len(area_vals))]) == num_dominos

    # solve the LP
    print(prob)

    prob.solve()
    print("Status:", LpStatus[prob.status])

    # print results of variable assignments
    x_ij_sum = 0
    print("(i, j)  |   variable value   |  cost(i, j)  |  len(area_vals[j])")
    for i in range(len(domino_vals)):
        for j in range(len(area_vals)):
            x_ij_sum += xij_vars[(i,j)].varValue
            if xij_vars[(i,j)].varValue > 0:
                print((i, j), '\t\t', xij_vars[(i,j)].varValue, '\t\t', cost(i, j), '\t\t', len(area_vals[j]))
    print("sum of xij values assigned", x_ij_sum)
    print(len(domino_vals)-1, len(area_vals)-1)

    print("k")
    print(k)
    print("num_dominos")
    print(num_dominos)
    print("rect_val_to_loc")
    print(rect_val_to_loc)
    print("area_vals")
    print(area_vals)


def generate_rect_val_to_loc(rect_layout, rect_values):
    # (val_lower, val_higher) => (a, b, c, d) indices
    rect_val_to_loc = {}

    for a,b,c,d in rect_layout:
        val1 = rect_values[a][b]
        val2 = rect_values[c][d]

        # update rect_val_to_loc
        if (min(val1, val2), max(val1, val2)) in rect_val_to_loc:
            rect_val_to_loc[(min(val1, val2), max(val1, val2))].append((a,b,c,d))
        else:
            rect_val_to_loc[(min(val1, val2), max(val1, val2))] = [(a,b,c,d)]

    return rect_val_to_loc




if __name__ == '__main__':
    pass
    # grid = np.array([[1,-1,1], [1,-1, 1], [1,1,-1]])
    # empty_cells = np.where(grid == 0)
    # print(list(zip(empty_cells[0], empty_cells[1])))

    # print(find_odd_empty_regions(np.array([[-1, -1,  -1],
    #                                        [ 1,  1,  -1],
    #                                        [ 1,  1,   1]])))

    # print(find_empty_orthogonal_neighbors(grid, 1, 1))

    # random_pattern_generator(6,5)


    ######################################################
    #           TEST generate_domino_graphics            #
    ######################################################
    # im = Image.open("./images/paddington.png").convert("RGBA")
    # value = 0.1
    # width_in_pixels = max(1, round(im.size[0]*value))
    # height_in_pixels = max(1, round(im.size[1]*value))
    # print(width_in_pixels, height_in_pixels)
    # imgSmall = im.resize((width_in_pixels, height_in_pixels), resample=Image.BILINEAR)
    #
    # generate_domino_graphics(imgSmall, width_in_pixels, height_in_pixels)



    ######################################################
    #                  TEST solve_LP                     #
    ######################################################
    '''
    -----------------
    | 2 | 4 | 3 | 1 |
    -----------------
    | 8 | 9 | 9 | 7 |
    -----------------
    | 1 | 3 | 4 | 2 |
    -----------------
    '''

    # rect_val_to_loc = {
    #                     (2, 4): [(0, 0, 0, 1), (2, 2, 2, 3)],
    #                     (1, 3): [(0, 3, 0, 2), (2, 2, 0, 1)],
    #                     (8, 9): [(1, 0, 1, 1)],
    #                     (7, 9): [(1, 2, 1, 3)]
    #                   }
    # k = 1
    # num_dominos = 6

    # rect_val_to_loc = {
    #                     (0, 3): [(4, 9, 5, 9)],
    #                     (3, 3): [(0, 9, 1, 9), (5, 7, 5, 8), (3, 8, 4, 8)],
    #                     (3, 4): [(4, 6, 5, 6)],
    #                     (3, 5): [(3, 7, 4, 7), (3, 0, 4, 0)],
    #                     (3, 6): [(0, 7, 1, 7), (3, 3, 4, 3), (0, 8, 1, 8)],
    #                     (4, 4): [(4, 4, 4, 5), (2, 9, 3, 9), (4, 1, 4, 2), (5, 2, 5, 3)],
    #                     (4, 5): [(5, 0, 5, 1)],
    #                     (4, 6): [(1, 0, 2, 0)],
    #                     (5, 5): [(5, 4, 5, 5), (2, 7, 2, 8)],
    #                     (5, 6): [(3, 5, 3, 6), (0, 6, 1, 6), (3, 1, 3, 2)],
    #                     (5, 7): [(1, 1, 2, 1)],
    #                     (5, 8): [(2, 4, 3, 4)],
    #                     (6, 7): [(0, 2, 1, 2)],
    #                     (6, 8): [(0, 0, 0, 1), (2, 5, 2, 6)],
    #                     (7, 8): [(0, 5, 1, 5), (2, 2, 2, 3)],
    #                     (8, 9): [(0, 3, 1, 3), (0, 4, 1, 4)],
    #                   }
    # k = 1
    # num_dominos = 30

    # solve_LP(k, rect_val_to_loc, num_dominos)
