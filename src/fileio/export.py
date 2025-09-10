import os
import shutil
import csv
from settings import config as cfg


# Function to export path coordinates to csv file, adjusted for the offset
# due to image position and boundary
def export_path_coords_to_csv(coords, draw_image_x, draw_image_y, image_boundary):
    shifted_coords = [
        (t[0] - (draw_image_x + image_boundary), t[1] - (draw_image_y + image_boundary))
        for t in coords
    ]

    with open(cfg.FILES["path_coordinates"], "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["X", "Y"])  # Write header row
        writer.writerows(shifted_coords)


# Function to export asset coordinates to csv file, adjusted for the offset
# due to image position and boundary
def export_asset_coords_to_csv(asset_defs, draw_image_x, draw_image_y, image_boundary):
    # If location specified, adjust for offset
    for asset in asset_defs:
        if asset.get("location"):
            asset["location"] = (
                asset["location"][0] - (draw_image_x + image_boundary),
                asset["location"][1] - (draw_image_y + image_boundary),
            )

    fieldnames = asset_defs[0].keys()
    with open(cfg.FILES["asset_coordinates"], "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asset_defs)


# Function to export dictionary containing metadata
def export_metadata(maze_metadata):
    fieldnames = maze_metadata.keys()
    with open(cfg.FILES["metadata"], "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(maze_metadata.keys())
        writer.writerow(maze_metadata.values())


# Function to export dictionary containing settings
def export_settings(settings):
    fieldnames = settings.keys()
    with open(cfg.FILES["settings"], "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(settings.keys())
        writer.writerow(settings.values())


# Funtion to draw maze grid to text file
def export_maze_grid_to_txt(maze_grid):
    f = open(cfg.FILES["grid"], "w")
    for row in maze_grid:
        row_str = ",".join(map(str, row))
        f.write(row_str + "\n")
    f.close()


# Move files to another directory
def move_files(source_directory, destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    for filename in os.listdir(source_directory):
        # Check if the file ends with .csv or .txt or .png
        if filename.endswith((".csv", ".txt", ".png")):
            source_path = os.path.join(source_directory, filename)
            destination_path = os.path.join(destination_directory, filename)

            try:
                shutil.move(source_path, destination_path)
                print(f"Moved '{filename}' to '{destination_directory}'")
            except Exception as e:
                print(f"Error moving '{filename}': {e}")


# Move specified file to another directory
def move_one_file(source_file, source_directory, destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    for filename in os.listdir(source_directory):
        # Check if the file ends with .csv or .txt or .png
        if source_file == filename:
            source_path = os.path.join(source_directory, filename)
            destination_path = os.path.join(destination_directory, filename)

            try:
                shutil.move(source_path, destination_path)
                print(f"Moved '{filename}' to '{destination_directory}'")
            except Exception as e:
                print(f"Error moving '{filename}': {e}")
