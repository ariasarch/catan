### Catan Board Randomizer ###
###     By Ari Asarch      ###

# Import Necessary Packages
import math # Math library for mathematical functions
import random # Library for generating random numbers and choices
import tkinter as tk # GUI library for creating graphical interfaces
from PIL import Image, ImageDraw, ImageTk
from tkinter import Canvas, Radiobutton, StringVar, Label # Imports Specific Widgets like Windows and Buttons

# Initialize Variables
reg_or_exp = "Regular" # Default to a regular Catan board layout
root = tk.Tk() # Create the main window instance
root.title("Catan Board Randomizer") # Set the title of the window

# Set up the drawing canvas within the main window
canvas = Canvas(root, width=1000, height=700, bg='white')

# Assuming the canvas is already created, you set its position with grid.
canvas.grid(row=2, column=0, columnspan=2, sticky="nsew")

# Configure the grid rows and columns to allocate space for the canvas.
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Set Hex Size
hex_size = 50 

# Function to create a hexagonal mask
def create_hexagonal_mask(image_size, hex_size):
    """
    Creates a hexagonal mask for an image.

    This function generates a hexagonal mask to be applied to an image for creating a hexagonal crop. 
    It first initializes a mask with the same dimensions as the target image but filled with zeros (transparent).
    Then, it calculates the vertices of a hexagon based on the specified hexagon size and the center of the image. 
    Using these vertices, the function draws a filled hexagon on the mask with white color (255), 
    which represents the area to keep when the mask is applied to an image.

    Parameters:
    - image_size (tuple of int): The dimensions (width, height) of the image for which the mask is created.
    - hex_size (int): The radius of the hexagon, defined from the center to any vertex.

    Returns:
    - hex_mask (Image): An image object representing the mask with a white hexagon on a transparent background.

    """

    # Calculate the center of the image
    w, h = image_size
    x_center, y_center = w / 2, h / 2

    hex_mask = Image.new('L', image_size, 0)
    hex_draw = ImageDraw.Draw(hex_mask)

    points = []
    # Calculate the vertices of the hexagon
    for i in range(6):
        angle_deg = (60 * i) + 30 # Calculate the angle for each vertex in degrees
        angle_rad = math.pi / 180 * angle_deg  # Converts the degree to radians
        x = x_center + hex_size * math.cos(angle_rad)  # Calculate the x-coordinate of the vertex
        y = y_center + hex_size * math.sin(angle_rad)  # Calculate the y-coordinate of the vertex
        points.append((x, y))

    # Draw the hexagon on the mask
    hex_draw.polygon(points, fill=255, outline=0)
    return hex_mask

# Function to apply the hexagonal mask to an image
def apply_hex_mask(image, mask):

    """
    Applies a hexagonal mask to an image.

    This function overlays a hexagonal mask onto an image to create a hexagonal crop effect. 
    The mask determines which parts of the original image are visible in the final result, 
    with the rest becoming transparent. The function uses the `Image.composite` method to apply this mask, 
    which combines the original image with a fully transparent image (same size as the mask), 
    using the mask to control the blending.

    Parameters:
    - image (Image): The original image to which the hexagonal mask will be applied.
    - mask (Image): The hexagonal mask image, where the white area represents the portion of the original image to retain.

    Returns:
    - Image: A new image with the hexagonal mask applied, where the area outside the hexagon is transparent.
    """

    return Image.composite(image, Image.new('RGBA', mask.size, (0, 0, 0, 0)), mask)

# The dictionary to hold the PhotoImage objects
photo_images = {}

# Paths to  image files
image_paths = {
    'desert': 'desert.png',
    'wheat': 'wheat.png',
    'wood': 'wood.png',
    'sheep': 'sheep.png',
    'brick': 'brick.png',
    'ore': 'ore.png',
}

# Set Image Size, should be much larger than the mask
required_width = 4 * hex_size
required_height = 2 * (int(math.sqrt(3) * hex_size))

# Define the global variable at the top level of your script
show_ports = False  # This assumes ports are not shown by default

# Load images, resize them, apply hexagonal mask, and convert them to a format Tkinter canvas can use
for resource, path in image_paths.items():
    # Open the image using PIL
    original_image = Image.open(path)
    
    # Resize the image using PIL's resize method
    resized_image = original_image.resize((required_width, required_height), Image.Resampling.LANCZOS)
    
    # Create hexagonal mask with the same size as the resized image
    hex_mask = create_hexagonal_mask(resized_image.size, hex_size)
    
    # Apply the hexagonal mask
    hex_image = apply_hex_mask(resized_image, hex_mask)
    
    # Convert the PIL image to a PhotoImage and store it in the dictionary
    photo_images[resource] = ImageTk.PhotoImage(hex_image)

def is_valid_board(board):
    """
    Validates the board configuration for a game which follows the rule that tiles numbered '6' or '8' 
    must not be adjacent to each other on a hexagonal grid. This function iterates through each tile in a 2D list 
    representing the game board and checks the six surrounding tiles for any '6' or '8' tiles, 
    considering the offset nature of the hexagonal grid rows.

    Parameters:
    - board (list of lists of str): A 2D list representing the game board, where each inner list is a row 
      of tiles on the board, and each tile is represented by a string with the format "resource-number".

    Returns:
    - bool: True if the board configuration is valid, meaning no '6' or '8' tiles are adjacent; 
      False otherwise.
    """

    # Initialize is_valid to True
    is_valid = True

    # Go through each cell in the 2D board list.
    for i in range(len(board)):
        for j in range(len(board[i])):
            current_tile = board[i][j]

            # Check if current tile is either 6 or 8
            if '-6' in current_tile or '-8' in current_tile:
                # Define neighbors based on column (even or odd)
                neighbors = [
                    (-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)
                ] if j % 2 == 0 else [
                    (-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)
                ]

                # Check all neighboring tiles
                for x, y in neighbors:
                    new_i, new_j = i + x, j + y

                    # Ensure new indices are within the board boundaries
                    if 0 <= new_i < len(board) and 0 <= new_j < len(board[new_i]):
                        neighboring_tile = board[new_i][new_j]

                        # Check if neighboring tile has a number (6 or 8)
                        if '-6' in neighboring_tile or '-8' in neighboring_tile:
                            is_valid = False
                            return is_valid  # Invalid adjacency found, return immediately

    # If no invalid adjacencies are found, the board is valid
    return is_valid

def generate_and_draw_new_board():
    """
    Generates a new Catan board and draws it on a canvas.

    This function loops indefinitely until a valid board is generated according to the rules.
    It clears the previous drawing on the canvas, generates a new random board configuration, draws it, and checks for validity.
    If the board is valid, it exits the loop, leaving the valid board displayed on the canvas.
    """
    while True:         
        canvas.delete("all")  # Clear the canvas of any previous drawings or elements.
        board_words, ports, colors = new_board()  # Generate a new board layout

        # Check if the newly generated board is valid
        if is_valid_board(board_words):
            print("Valid board generated.")
            break  # Exit the loop if the board is valid

    draw_board_gui(board_words, ports, colors)  # Draw the new board
    print(f'Valid Board {board_words}')

def draw_board_gui(board, ports, colors):
    """
    Draws the board and ports (if enabled) in a GUI.

    This function iterates over the `board` data structure (a list of lists containing strings) and
    uses information within each cell to set the photo and number of each hexagon representing
    resources on the game board. Hexagons are drawn on a predefined `canvas`. Images are added via 
    the create_image, sized via the create_polygon function, and resource numbers are added on top 
    of them. Additionally, if the global variable `show_ports` is set to True, ports are drawn using 
    the `draw_ports` function with the specified `colors`.

    Parameters:
    - board (list of lists of str): A 2D list where each element is a string with the resource type and 
    number separated by a dash (e.g., "wheat-8").
    - ports (list of tuples): A list where each tuple contains the row and column indices where a port should be drawn.
    - colors (list of str): A list of color strings to use for the ports.

    Globals:
    - show_ports (bool): A flag to determine whether ports should be drawn or not.
    - reg_or_exp (str): A string indicating the mode of the game board ("Regular" or "Expansion") that can affect coloring.
    """
    
    global show_ports  # Access the global variable
    global reg_or_exp # Access the global variable
    hex_height = int(math.sqrt(3) * hex_size) # Height of the hexagons
    hex_width = 2 * hex_size # Width of the hexagons
    offset_x = 375 # Intial x offset to center board
    offset_y = 150 # Intial y offset to center board
    circle_radius = 5  # Radius of the ports circles

    # Iterate though each row and column in board to draw and color the hexagon
    for row_index, row in enumerate(board):
        for col_index, cell in enumerate(row):

            refactor = 0.87

            # Calculate the position for each hex
            if (row_index % 2) == 0:
                # For even rows, no x-offset
                x = (offset_x + (col_index * hex_width)) * refactor
            else:
                # For odd rows, offset x by half the width of the hexagon
                x = (offset_x + (col_index * hex_width) + (hex_width / 2)) * refactor
            
            # y is calculated by the row index, offset vertically by the hex height per row
            y = (offset_y + row_index * (hex_height)) * refactor

            # Shift top, bottom, and center (if expansion) rows one hex tile over
            if len(row) == 6:
                x -= hex_width * refactor
            if row_index == 0:  # Top row
                x += hex_width * refactor
            elif row_index == len(board) - 1:  # Bottom row
                x += hex_width * refactor

            # Extract resource type and number from the cell string.
            resource = cell.split('-')[0]

            # Calculate the vertices of the hexagon for the outline
            points = []
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = math.pi / 180 * angle_deg
                point_x = x + hex_size * math.cos(angle_rad)
                point_y = y + hex_size * math.sin(angle_rad)
                points.append((point_x, point_y))

            if resource in photo_images:
                # Create an image object on the canvas at the calculated position
                canvas.create_image(x, y, image=photo_images[resource], anchor='center')

                # Draw the hexagon border on the canvas using the points
                canvas.create_polygon(points, outline='black', fill='', width=2)

            # If there's a number, create text on top of the image
            if '-' in cell:
                number = cell.split('-')[1]

                # Draw the tan circle slightly larger than the text
                circle_radius = 15 
                canvas.create_oval(x - circle_radius, y - circle_radius,
                                x + circle_radius, y + circle_radius,
                                fill="#FEE0AC", outline='black')
                
                # Color the 6's and 8's red
                if number in ('6', '8'):
                    canvas.create_text(x, y, text=number, fill='#B20909', font=("Arial", 16, "bold"))
                else:
                    canvas.create_text(x, y, text=number, fill='black', font=("Arial", 16, "bold"))

            # After drawing hexagons and numbers, check if ports should be drawn
            if show_ports:
                draw_ports(canvas, ports, offset_x, offset_y, hex_width, hex_height, refactor, colors)
                draw_legend()

def initialize_gui():
    """
    Initializes the graphical user interface (GUI) for the board game.

    This function sets up the initial GUI elements including a label to instruct the user to select a mode,
    radio buttons to choose between 'Regular' or 'Expansion' game modes, a button to generate a new board based
    on the selected mode, and a toggle button to show or hide ports on the game board.

    Upon selecting a mode, the global variable 'reg_or_exp' is updated to reflect the chosen mode,
    affecting how the board will be generated. The 'Generate New Board' button invokes a function to create
    and draw the board on the GUI. The 'Show Ports' toggle button allows the user to display or hide port locations
    on the board, which is reflected in the global 'show_ports' variable.

    The 'Generate New Board' and 'Show Ports' buttons are connected to command functions that execute the
    respective actions when clicked. This function must be called to initialize the board game's GUI before
    the game can be played.

    Globals:
    - reg_or_exp (str): Tracks the selected game mode ('Regular' or 'Expansion').
    - show_ports (bool): Determines whether ports should be displayed on the game board.
    """

    # Create a label in the GUI to prompt the user to select a game mode
    label = Label(root, text="Select Mode:")

    # Initialize a StringVar to hold the value of the selected game mode, default to "Regular"
    reg_or_exp_var = StringVar()
    reg_or_exp_var.set("Regular")

    # Define a function to update the global variable based on the selected mode
    def update_reg_or_exp():
        global reg_or_exp
        reg_or_exp = reg_or_exp_var.get()

    # Create a radio button for the 'Regular' game mode
    rb_regular = Radiobutton(root, text="Regular", variable=reg_or_exp_var, value="Regular", command=update_reg_or_exp)

    # Create a radio button for the 'Expansion' game mode
    rb_expansion = Radiobutton(root, text="Expansion", variable=reg_or_exp_var, value="Expansion", command=update_reg_or_exp)

    # Define a function to toggle button text
    def toggle_button_text():
        global show_ports  # Declare that you want to use the global variable

        # Toggle the show_ports variable between True and False
        show_ports = not show_ports

        # Update the button text based on the current state of show_ports
        toggle_button.config(text='Hide Ports' if show_ports else 'Show Ports')

    # Create a button that, when clicked, will generate and draw a new game board
    new_board_button = tk.Button(root, text="Generate New Board", command=generate_and_draw_new_board)

    # Create the toggle button
    toggle_button = tk.Button(root, text="Show Ports", command=toggle_button_text)

    # Place the label below the canvas
    label.grid(row=3, column=0, columnspan=1, padx=5, pady=5, sticky='w')

    # Other GUI elements follow in subsequent rows
    rb_regular.grid(row=4, column=0, padx=5, pady=5, sticky='w')
    rb_expansion.grid(row=5, column=0, padx=5, pady=5, sticky='w')
    new_board_button.grid(row=4, column=1, padx=(5), pady=5, sticky='e')
    toggle_button.grid(row=5, column=1, padx=(5), pady=5, sticky='e')

def draw_ports(canvas, ports, offset_x, offset_y, hex_width, hex_height, refactor, colors):
    """
    Draws the port locations on the game board.

    This function takes a canvas and a list of port locations, and draws a colored circle at each port's
    calculated position on the canvas. The color of the circle corresponds to the type of resource or
    trade ratio the port represents. The function ensures that the colors of the ports cycle through
    the provided list, starting over if there are more ports than colors.

    Parameters:
    - canvas (Canvas): The Tkinter canvas object where the ports will be drawn.
    - ports (list of tuples): A list of tuples where each tuple represents the (row, column) index of a port.
    - offset_x (int or float): The horizontal offset to align the ports with the hexes on the board.
    - offset_y (int or float): The vertical offset to align the ports with the hexes on the board.
    - hex_width (int or float): The width of the hexes on the board. Used to calculate port positions.
    - hex_height (int or float): The height of the hexes on the board. Used to calculate port positions.
    - refactor (float): A scaling factor to adjust the size of the ports relative to the board.
    - colors (list of str): A list of color names or hexadecimal color codes to fill the ports. Each color corresponds to a different type of port.
    """
    for index, port in enumerate(ports):
        # Determine the row and column from the port tuple
        row_index, col_index = port

        # Calculate the x and y position like the hexes, including the refactor
        x = (offset_x + (col_index * hex_width)) * refactor        
        y = (offset_y + row_index * (hex_height)) * refactor

        # Circle Radius
        circle_radius = 7.5
        
        # Choose a color for the port from the list, cycling back to the start if there are more ports than colors
        port_color = colors[index % len(colors)]
        
        # Draw a circle at the port's location with the chosen color
        canvas.create_oval(x - circle_radius, y - circle_radius,
                        x + circle_radius, y + circle_radius,
                        fill = port_color, outline = 'black') 

def draw_legend():
    """
    Draws a legend on the canvas to represent the meaning of various colors used in the game.

    This function iterates through a predefined dictionary of legend items, where each key-value
    pair represents a resource or port type and its corresponding color. It uses this information
    to draw circles of specified colors with labels on the canvas to serve as a legend for the game board.

    The legend starts at a fixed y-coordinate and displays each item with a specified padding
    in between. The colors and resource or port types are hardcoded within the function.
    """

    # Define the legend items and their corresponding colors
    legend_items = {
        "Wheat": "#ECCF1B",
        "Wood": "#1A4D00",
        "Sheep": "#97E83A",
        "Brick": "#BA0B0B",
        "Ore": "#A0A0A0",
        "3:1": "Black"
    }

    # Starting Y position for the legend items
    y_start = 100

    # Set a padding between items
    padding = 20

    # Circle Radius 
    circle_radius = 7.5

    # Offset to start drawing the legend text next to the rectangles
    offset_x = 100
    text_offset_x = offset_x + (circle_radius * 2) + 10

    for item, color in legend_items.items():
        # # Draw the rectangle for the legend color
        # canvas.create_rectangle(offset_x, y_start, offset_x + rect_width, y_start + rect_height, 
        #                         fill = color, outline = 'Black')
        
        canvas.create_oval(offset_x - circle_radius, y_start - circle_radius,
                            offset_x + circle_radius, y_start + circle_radius,
                            fill = color, outline = 'black') 
        # Draw the legend text
        canvas.create_text(text_offset_x, y_start, 
                           text=item, anchor='w', fill = 'Black')
        # Move the Y position for the next item
        y_start += (circle_radius * 2) + padding

def populate_tiles(tiles, row_lengths):
    """
    Populate the board with tiles based on the specified row lengths.

    Parameteres:
    - tiles (list): A list of tile identifiers that should be randomly placed on the board.
    - row_lengths (list): A list indicating how many tiles should be in each row.

    Returns:
    - list: A 2D list representing the board with populated tiles.
    """
    board = []  # Initialize an empty board
    for row_length in row_lengths:
        row = []  # Initialize an empty row
        # Continue to add tiles to the current row until it reaches the specified length
        while len(row) < row_length:
            tile = tiles.pop()  # Remove a tile from the end of the list
            row.append(tile)  # Add the tile to the current row
        board.append(row)  # Add the completed row to the board
    return board  # Return the fully populated board

def translate_to_text(board_list, rows):
    """
    Translates a board list with numeric representations into a list of text representations.
    
    Each number in the board_list corresponds to a resource or tile, which is represented as a string:
    - 0 corresponds to 'desert'
    - 1 corresponds to 'wheat'
    - 2 corresponds to 'wood'
    - 3 corresponds to 'sheep'
    - 4 corresponds to 'brick'
    - 5 corresponds to 'ore'

    The function constructs a 2D list where each numeric value from the original board_list is replaced
    with its corresponding text representation, based on the position of the resource in the 'text_list'.

    Parameters: 
    - board_list (list of lists of int): 2D list of integers where each integer represents a specific type of resource.
    - rows (int): Integer representing the number of rows in the board list.
    
    Returns: 
    A 2D list of strings where each string represents the name of a resource.
    """

    text_list = ['desert', 'wheat', 'wood', 'sheep', 'brick', 'ore'] # Define the mapping of numbers to resource names.
    board_text = [] # Initialize an empty list to hold the translated board text.
    
    # Create an empty sublist for each row in the board.
    for i in range(rows):
        board_text.append([]) # Begin with an empty row.
    
    # Go through each cell in the 2D board list.
    for i in range(rows):
        for j in range(len(board_list[i])):
            # Translate the numeric representation to text and add to the board text.
            board_text[i].append(text_list[board_list[i][j]])
    
    # Return the fully translated board text list.
    return board_text

def add_numbers(board, numbers_list):
    """
    Add numbers to each tile on the board except for the desert tiles.

    Parameters:
    - board (list): A 2D list representing the board with populated tiles.
    - numbers_list (list): A list of numbers that need to be placed on the board.

    Returns:
    - list: A 2D list representing the board with numbers added to the tiles.
    """
    numbers_iter = iter(numbers_list)  # Create an iterator from the numbers list
    for row in board:
        for index, tile in enumerate(row):
            if tile != 'desert':  # Check if the tile is not a desert
                # Try to get a number from the iterator and add it to the tile, if no numbers left, break the loop
                try:
                    number = next(numbers_iter)
                except StopIteration:
                    break
                row[index] = f"{tile}-{number}"  # Concatenate the tile type and the number with a dash
    return board  # Return the board with numbers added

def new_board():
    """
    Generates a new board configuration with random tile and number placement. This function supports
    creating a board for either the Regular or Expansion game mode. The game mode is determined by a 
    variable outside the function scope; 'reg_or_exp'.

    Each game mode has a predefined set of tiles (with quantities and types), numbers for the tiles,
    lengths of each row of the board to construct the appropriate hexagonal shape, and predefined port 
    locations with their associated colors.

    The function randomizes the tiles and numbers to provide a unique board configuration each time. It
    then calls other functions (not defined within this code snippet) to populate the board with tiles,
    convert the tiles to a text representation, and finally, add the numbers to the board.

    Returns:
    - board_words (list of lists of str): A 2D list representing the board with populated tiles and 
      assigned numbers in a text format.
    - ports (list of tuples): A list of tuples with floating-point values representing the coordinates 
      for the ports.
    - colors (list of strings): A list of strings representing the colors for the ports.
    """

    # Dictionaries to hold the different data for each mode.
    data = {
        'Regular': {
            'tiles': [0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5],
            'numbers_list': [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12],
            'row_lengths': [3, 4, 5, 4, 3],
            'ports': [(-0.65, 1), (-0.35, 0.5), (-0.65, 2), (-0.35, 2.5), 
                      (0.65, 4), (0.35, 3.5), (0.65, 0), (1.35, 0), 
                      (1.65, 4.5), (2.35, 4.5), (3.35, 0), (2.65, 0),
                      (3.35, 4), (3.65, 3.5), (4.65, 1), (4.35, 0.5), 
                      (4.65, 2), (4.35, 2.5)],
            'colors': ['Black', 'Black', 
                       '#97E83A', '#97E83A', 
                       'Black', 'Black', 
                       '#A0A0A0', '#A0A0A0', 
                       'Black', 'Black',
                       '#ECCF1B', '#ECCF1B',
                       '#BA0B0B', '#BA0B0B',
                       'Black', 'Black',
                       '#1A4D00', '#1A4D00']
        },
        'Expansion': {
            'tiles': [0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5],
            'numbers_list': [2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 8, 8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12],
            'row_lengths': [3, 4, 5, 6, 5, 4, 3],
            'ports': [(-0.65, 1), (-0.35, 0.5), (-0.65, 2), (-0.35, 2.5), 
                      (0.65, 4), (0.35, 3.5), (1.65, -0.5), (2.35, -0.5), 
                      (3.35, 5), (2.65, 5), (4.35, -0.5), (3.65, -0.5),
                      (5.35, 0), (4.65, 0), (4.65, 4), (4.35, 4.5),
                      (6.65, 1), (6.35, 0.5), (6.65, 2), (6.35, 2.5),
                      (5.65, 3.5), (6.35, 3.5)],
            'colors': ['#BA0B0B', '#BA0B0B', 
                       '#ECCF1B', '#ECCF1B', 
                       'Black', 'Black', 
                       '#A0A0A0', '#A0A0A0', 
                       'Black', 'Black', 
                       'Black', 'Black', 
                       '#1A4D00', '#1A4D00',
                       'Black', 'Black', 
                       '#97E83A', '#97E83A',
                       'Black', 'Black', 
                       '#97E83A', '#97E83A']
        }
    }
    
    mode_data = data[reg_or_exp]  # Get data based on current mode.
    ports = mode_data['ports'] # Define port locations
    colors = mode_data['colors'] # Define port colors
    
    # Randomize the lists
    random.shuffle(mode_data['tiles'])
    random.shuffle(mode_data['numbers_list'])
    
    # Populate the board with tiles
    board = populate_tiles(mode_data['tiles'], mode_data['row_lengths'])
    
    # Translate to text representation
    board_words = translate_to_text(board, len(mode_data['row_lengths']))
    
    # Add numbers to the board
    add_numbers(board_words, mode_data['numbers_list'])
    
    return board_words, ports, colors

if __name__ == "__main__":
    initialize_gui()
    root.mainloop()