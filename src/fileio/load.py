import os
import csv
import pygame


# Loads all png images from a directory and stores in a list
def import_image_dir(directory_path):
    loaded_images = {}
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(directory_path, filename)
            try:
                image_surface = pygame.image.load(image_path).convert()
                image_name = os.path.splitext(filename)[0]
                loaded_images[image_name] = image_surface
            except pygame.error as e:
                print(f"Error loading image: {filename}: {e}")
    return loaded_images


# Saves paths associated with levels at a given directory if appropriate
# supporting files are found
def get_levels(directory_path):
    levels = []
    for folder in os.listdir(directory_path):
        map_path = os.path.join(directory_path, folder)
        if not folder.startswith(".") and os.path.isdir(map_path):
            asset_filepath = ""
            grid_filepath = ""
            metadata_filepath = ""
            path_filepath = ""
            screenshot_filepath = ""
            for filename in os.listdir(map_path):
                if filename.lower().endswith("asset_coordinates.csv"):
                    asset_filepath = os.path.join(map_path, filename)
                elif filename.lower().endswith("grid.txt"):
                    grid_filepath = os.path.join(map_path, filename)
                elif filename.lower().endswith("metadata.csv"):
                    metadata_filepath = os.path.join(map_path, filename)
                elif filename.lower().endswith("path_coordinates.csv"):
                    path_filepath = os.path.join(map_path, filename)
                elif filename.lower().endswith("screenshot.png"):
                    screenshot_filepath = os.path.join(map_path, filename)
            if asset_filepath and grid_filepath and metadata_filepath and path_filepath:
                levels.append(
                    {
                        "assets": asset_filepath,
                        "grid": grid_filepath,
                        "metadata": metadata_filepath,
                        "path": path_filepath,
                        "screenshot": screenshot_filepath,
                    }
                )
            else:
                print(
                    f"Could not load level at this location due to missing files: {map_path}"
                )
    return levels


# Function to read csv containing one or more dictionaries
def read_csv_dict(csvfile):
    data_list = []
    try:
        with open(csvfile, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data_list.append(row)
    except FileNotFoundError:
        print(f"Error: '{csvfile}' not found.")
    except Exception as e:
        print(f"An error occurred while reading {csvfile}: {e}")
    return data_list


# Function to read maze path coordinates from csv file
def read_csv_path(csvfile):
    path_coords = []
    try:
        with open(csvfile, "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip first row
            for row in reader:
                x = float(row[0])
                y = float(row[1])
                path_coords.append((x, y))
    except FileNotFoundError:
        print(f"Error: '{csvfile}' not found.")
    except Exception as e:
        print(f"An error occurred while reading {csvfile}: {e}")
    return path_coords


# Function to read maze grid from text file
def import_maze_grid_from_txt(txt_file):
    maze_grid = []
    try:
        with open(txt_file, "r") as file:
            for line in file:
                row = [int(item.strip()) for item in line.strip().split(",")]
                maze_grid.append(row)
    except FileNotFoundError:
        print(f"Error: File not found at {txt_file}")
    except Exception as e:
        print(f"An error occurred while parsing {txt_file}: {e}")
    return maze_grid
