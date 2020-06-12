import random, math, itertools, time
import numpy as np
from pulp import *
from scipy.ndimage.measurements import label
from PIL import Image



def image_to_scaled_array(image):
    t0 = time.time()
    img_array = np.array(image.convert("L"))

    # interpolate pixel values to be between 0 and 9
    scaled_array = np.interp(img_array, (img_array.min(), img_array.max()), (0, 9))
    # round and convert to integers
    rounded_array = np.round(scaled_array).astype(int)
    t1 = time.time()
    print("image_to_scaled_array took", t1-t0, "seconds")
    return scaled_array # TODO: change to rounded_array for faster times (but less accuracy)


def random_pattern_generator(width, height):
    t0 = time.time()
    assert width * height % 2 == 0, "Cannot find pattern for image with an odd number of pixels"

    rectangles = set() # contains tuples of (row, col, row2, col2)

    grid = np.full((height, width), -1)
    i, j = 0, 0
    empty_cell_exists = True
    while empty_cell_exists:
        # place rectangle randomly at position (i,j), (i+1,j), or (i,j), (i, j+1)
        orientation = random.randint(0,1)
        if orientation == 0:
            rectangles.add((i, j, i+1, j))
            grid[i][j] = 1
            grid[i+1][j] = 1
        else:
            rectangles.add((i, j, i, j+1))
            grid[i][j] = 1
            grid[i][j+1] = 1

        # while there exists (i, j), an empty cell with three occupied orthogonal neighbours and all regions of empty connected cells are of even size
        empty_cells_list = list(zip(np.where(grid == -1)[0], np.where(grid == -1)[1]))
        while len(empty_cells_list) > 0 and len(find_empty_orthogonal_neighbors(grid, empty_cells_list[0][0], empty_cells_list[0][1])) == 1 and not find_odd_empty_regions(grid):
            i, j = empty_cells_list[0]
            adjacent_empty_cell = find_empty_orthogonal_neighbors(grid, i, j)[0]
            rectangles.add((i, j, adjacent_empty_cell[0], adjacent_empty_cell[1]))
            grid[i][j] = 1
            grid[adjacent_empty_cell[0]][adjacent_empty_cell[1]] = 1
            # update empty cells list
            empty_cells_list = list(zip(np.where(grid == -1)[0], np.where(grid == -1)[1]))

        # if there is a region of an odd number of connected empty cells in the grid then wipe out part of the grid
        if find_odd_empty_regions(grid):
            print("mistake, clearing last 2 rows")
            # clear out 2 prior rows
            new_rectangles = set(filter(lambda x: (x[1] < j-2) and (x[3] < j-2) , rectangles))
            for a, b, c, d in rectangles - new_rectangles:
                grid[a][b] = -1
                grid[c][d] = -1
            rectangles = new_rectangles

        # find next empty cell
        empty_cells_list = list(zip(np.where(grid == -1)[0], np.where(grid == -1)[1]))
        if len(empty_cells_list) > 0:
            i, j = empty_cells_list[0]
        else:
            empty_cell_exists = False

    # visualize_rectangle_grid(width, height, rectangles)

    t1 = time.time()
    print("random_pattern_generator took", t1-t0, "seconds")
    return rectangles

def find_empty_orthogonal_neighbors(grid, i, j):
    empty_neighbors = []
    for m, n in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]:
        if 0 <= m < len(grid) and 0 <= n < len(grid[0]) and grid[m][n] == -1:
            empty_neighbors.append((m, n))

    return empty_neighbors


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


def visualize_rectangle_grid(width, height, rectangles):
    counter = 0
    grid = np.full((height, width), -1)
    for a, b, c, d in rectangles:
        grid[a][b] = counter
        grid[c][d] = counter
        counter += 1

    print("\n rect_layout:")
    print("===================")
    print(grid)
    print("===================")

def generate_domino_graphics(imgSmall, width_in_pixels, height_in_pixels, filename):
    t0 = time.time()
    rect_values = image_to_scaled_array(imgSmall)
    rect_layout = random_pattern_generator(width_in_pixels, height_in_pixels)

    rect_val_to_loc = generate_rect_val_to_loc(rect_layout, rect_values)
    final_domino_grid = solve_LP(rect_values, rect_val_to_loc, width_in_pixels, height_in_pixels)

    t05 = time.time()
    # each domino image is 404 x 810
    background = Image.new('RGBA', (width_in_pixels*200, height_in_pixels*200), (255, 255, 255, 255))
    bg_w, bg_h = background.size

    for a,b,c,d in rect_layout:
        first_val = int(final_domino_grid[a][b])
        second_val = int(final_domino_grid[c][d])

        # get domino image and resize to dimensions that have 1:2 ratio
        domino_img = Image.open('./dominoes/' + str(min(first_val, second_val)) + '-' + str(max(first_val, second_val)) + '.png', 'r').resize((200, 400), Image.NEAREST)

        # if horizontal orientation, rotate image
        if a == c:
            domino_img = domino_img.rotate(90, expand=True)

        # if rotate image if first value is higher / second value is lower
        if min(first_val, second_val) == second_val:
            domino_img = domino_img.rotate(180, expand=True)

        offset = (b*200, a*200)
        background.paste(domino_img, offset)

    background.save('./output/' + filename + '_' + str(math.ceil(width_in_pixels*height_in_pixels / 2 / 55)) + '_domino_sets.png')

    t1 = time.time()
    print("generate_domino_graphics took", t1-t0, "seconds")
    print("actual image generation part of generate_domino_graphics took", t1-t05, "seconds")
    return background



'''
An area is a set of all rectangles with identical pairs of costs in the pattern
Area j corresponds to a rectangle of cost (j_1,j_2)

capa_j = number of rectangles with identical values in area_j       len(rect_val_to_loc[area_vals[j]])
nbArea = total number of areas (nbArea ≤55)                         len(rect_val_to_loc) or len(area_vals)
'''
def solve_LP(rect_values, rect_val_to_loc, width_in_pixels, height_in_pixels):
    t0 = time.time()
    # k is total number of sets of dominoes
    k = math.ceil(width_in_pixels*height_in_pixels / 2 / 55)

    # num_rects is the total number of rectangles we need to assign dominoes to
    num_rects = width_in_pixels*height_in_pixels / 2

    # create list of domino values (where d_i = domino_vals[i])
    domino_vals = list(itertools.combinations_with_replacement([0,1,2,3,4,5,6,7,8,9], 2))

    # create list of area values ((a,b) = (j_1, j_2) = area_vals[j])
    area_vals = sorted(rect_val_to_loc.keys())

    # create function for computing the cost of placing domino i in rectangle j
    def cost(i, j):
        # since incoming values should be (low, high) we do not need to account for inverting the orientation because cost will be minimized as is
        cost_ij = (domino_vals[i][0]-area_vals[j][0])**2 + (domino_vals[i][1]-area_vals[j][1])**2
        return cost_ij

    ##################################
    #           LP Problem           #
    ##################################
    # declare problem to be a minimization LP problem
    prob = LpProblem("domino_optimization_problem",LpMinimize)

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

    # add third constraint to ensure that sum of all x_ij values is num_rects
    prob += lpSum([xij_vars[(i,j)] for i in range(len(domino_vals)) for j in range(len(area_vals))]) == num_rects

    # solve the LP
    prob.solve()

    # create final_domino_grid array that is just a grid of the final value assignments
    final_domino_grid = np.empty([height_in_pixels, width_in_pixels])

    for i in range(len(domino_vals)):
        for j in range(len(area_vals)):
            xij = int(xij_vars[(i,j)].varValue)
            # remove dominoes from rect_val_to_loc[area_vals[j]] and assign those the domino i with orientation determined by trying to minimize cost
            rects_to_be_assigned_dominoes = rect_val_to_loc[area_vals[j]][::-1][:xij] # i.e. [(1,1,2,1), ...]
            rect_val_to_loc[area_vals[j]] = rect_val_to_loc[area_vals[j]][::-1][xij:]

            for a,b,c,d in rects_to_be_assigned_dominoes:
                # figure out if domino needs to be flipped to minimize cost & update final_domino_grid 2D array
                if (domino_vals[i][0]-rect_values[a][b])**2 + (domino_vals[i][1]-rect_values[c][d])**2 > (domino_vals[i][0]-rect_values[c][d])**2 + (domino_vals[i][1]-rect_values[a][b])**2:
                    # we need to flip the domino order when we assign it
                    final_domino_grid[a][b] = domino_vals[i][1]
                    final_domino_grid[c][d] = domino_vals[i][0]
                else:
                    # assign as is
                    final_domino_grid[a][b] = domino_vals[i][0]
                    final_domino_grid[c][d] = domino_vals[i][1]


    # return final_domino_grid and then generate_domino_graphics should use final_domino_grid instead of rect_values
    t1 = time.time()
    print("solve_LP took", t1-t0, "seconds")
    return final_domino_grid


def generate_rect_val_to_loc(rect_layout, rect_values):
    t0 = time.time()
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

    t1 = time.time()
    print("generate_rect_val_to_loc took", t1-t0, "seconds")
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
    #           TEST random_pattern_generator            #
    ######################################################

    print(random_pattern_generator(50,50))

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

    # im = Image.open("./images/paddington.png").convert("RGBA")
    # imgSmall = im.resize((6, 6), resample=Image.BILINEAR)
    # imgSmall.convert('L').save('example.png')
    # generate_domino_graphics(imgSmall, 6, 6)

    ######################################################
    #                  TEST solve_LP                     #
    ######################################################

    # '''
    # -----------------
    # | 2 | 4 | 3 | 1 |
    # -----------------
    # | 8 | 9 | 9 | 7 |
    # -----------------
    # | 1 | 3 | 4 | 2 |
    # -----------------
    # '''

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
