# snack-attack
*Snack Attack* is a 2D labyrinth game designed using Python. The player controls a combine vehicle to collect fruit items and fight vegetable enemies before proceeding to the next level.

The game is inspired by *Mine Shaft*, released on the IBM PCjr in 1984.

<br>
<img width="1602" height="932" alt="new_title_screenshot" src="https://github.com/user-attachments/assets/4c7a1e65-489d-4596-8ad9-eb844c2f8922" />

## Video Demo

<video src="https://github.com/user-attachments/assets/e3de73c9-39b0-4a71-9bcf-fb77037038db" width="1600" height="900" controls></video>

## Installation

You can install and run the project in two ways:

* Method 1: From a released version
  * Download the latest .zip file from the Releases page.
  * Unzip the file and run the provided executables (.exe) on a Windows PC, located in the ``bin`` folder.
  * A display resolution of at least `1600 x 900` is required to view the entire window.
  * Note that Windows scaling may need to be disabled on certain displays.
  
* Method 2: From source code
  * Download and install Python 3.13.5 or newer.
  * Add your Python installation folder and the associated ``Scripts`` folder to your system environment variables "Path" variable.
  * Download the project source code and unzip, or clone the repository using Git.
  * Install the project's dependencies from the root directory by running the following command: ``pip install -r requirements.txt``
  * You can then run the game directly from the source code. 

## Overview
*Snack Attack* features original source code, hand-drawn sprites, custom sound effects generated from Jsfxr (https://sfxr.me/), and hand-crafted levels made with a custom level editor. I created this game to grow my skills and understanding of Python, object oriented programming, game design, and computer graphics.

The first challenge I faced was determining how to produce levels which followed the same ruleset from the *Mine Shaft* game. The path is comprised of interconnected square cells, where a square equal to the standard cell width must fit snugly within the path. It should not be possible to draw a square larger than this standard cell within the maze. Nor should it be possible to draw a diagonal line, starting from an edge, that is smaller than the diagonal formed within a standard square cell. For example, the top three patterns are possible within the maze, while the bottom patterns are not: 

![screenshot_patterns](https://github.com/user-attachments/assets/73d19c4d-9881-409c-9223-4d45492815e3)

## Level Builder
These compliance checks are enforced each time the user attempts to draw a new block in the level builder. The first mode of the level builder allows the user to draw the maze by left-clicking the mouse on a desired location, or by using the arrow keys to traverse relative to the most recently added coordinate. An external or built-in touchpad can also be used, similar to the mouse option. Undoing the last added coordinate is done by pressing the `X` key. Additionally, this mode allows the user to toggle between 10 maze color options, cycle the speed at which the player and enemies will move, and cycle the number of enemies of each type. Corn and Tomato enemies can be destroyed by the player, while Pumpkins are invincible. Pressing `Escape` allows the user to select a `level_path_coordinates.csv` file from a prior maze.

<br>
<img width="1602" height="932" alt="new_screenshot_01" src="https://github.com/user-attachments/assets/d20613d3-d187-4b0a-b906-5757a508048a" />
<br><br>

A specific coordinate can be erased by right-clicking with the mouse. This right-click reveals small white dots representing the chosen coordinates, which are provided as a visual aid.

<br>
<img width="1602" height="932" alt="new_screenshot_02" src="https://github.com/user-attachments/assets/b15fa252-044c-494b-bdb4-5caff92e8f1f" />
<br><br>

Once the user hits the `A` key to finalize the level, the second mode is activated which allows for the selection of locations for each of the relevant assets. This includes the player starting location, the player's respawn location if destroyed, the starting location for all enemy types, four item locations, and the exit location, which will appear once all enemies are destroyed or all items are collected. By hovering the mouse over a desired location in the maze and pressing the appropriate key, the asset is placed visually, and its coordinates are later exported to a file. Right-clicking is used to undo the last action.

<br>
<img width="1602" height="932" alt="new_screenshot_03" src="https://github.com/user-attachments/assets/70d07794-e590-4986-9bfb-0f3229bbbfb5" />
<br><br>

Upon pressing `C` to export the level, the user is prompted to create a folder within the ``levels`` folder. This is where the levels are loaded in the game, in ascending alphabetical order. This example level is shown below in a gameplay screenshot:

<br>
<img width="1602" height="932" alt="new_screenshot_04" src="https://github.com/user-attachments/assets/19d0043d-2c3c-43f8-a522-17c1b3963cad" />

## Gameplay
Upon completing the final level in the ``levels`` folder, these levels are repeated using the frantic game speed, with a pre-defined number of enemies. This behavior is similar to that in the *Mine Shaft* game. It is possible, however, to add countless levels to this folder to delay when this behavior is encountered. The game includes 10 levels, with a screenshot of the third level shown as follows:

<br>
<img width="1602" height="932" alt="screenshot_05" src="https://github.com/user-attachments/assets/26ecb89e-3d12-4dae-b271-c22feb18c259" />
<br><br>

On the title screen, the `F5` key is used to cycle different animation smoothness options. The most coarse option converts the level to a grid of 1s (walls) and 0s (path) with a level width of 256 and a level height of 192. The level is upscaled to the screen with a factor of 4, so the coarse option will inherently appear more "choppy" during movements. The normal option doubles the coarse grid, while the fine option quadruples it to match the screen resolution, meaning each pixel is navigable.

These three options were included because it was found that older PCs can struggle with the normal or fine options, to the point that the game appears more sluggish. This occurs when the computer cannot render the game tick within the expected time. When cycling the options, observe whether sprites appear to move slower than with the coarse option. If so, it is recommended to use the default coarse option. For faster PCs, this will not be an issue, and a time delay is introduced at each game tick to ensure the game renders at the intended speed.

The `F1` key toggles between the four control schemes available to the player. These consist of either `W`, `A`, `S`, `D` for up, left, down, right and `Enter` for firing the weapon, or `I`, `J`, `K`, `L` and `F`. The first scheme for these layouts features "hold-to-move" logic, where the player character will only traverse in a given direction if the user is holding down the corresponding key. The second scheme features "press-to-move" logic, where pressing a given direction key will initiate movement in that direction until the `Spacebar` is pressed to stop movement. If the player cannot move in the requested direction, the previously selected direction is attempted, as this simplifies navigation in complex mazes (rather than requiring a pixel-perfect location before user input results in meaningful action).

Player lives are decremented upon contact with an enemy and increase by one if all items are collected. Score is increased by destroying enemies and by collecting items. The `Escape` key ends the game and returns to the title screen, which also occurs if the player expends all remaining lives. The `Pause` key pauses the game, and `F10` skips to the next level. This `F10` key can be pressed repeatedly to skip multiple levels, so the user does not have to wait for the maze to be drawn. The mazes are drawn block-by-block over the course of several seconds, which is not necessary on modern PCs. However, this "retro" aesthetic was implemented to give the user a momentary break from the previous level, to illustrate how the level was created in the editor, and as a nod to the *Mine Shaft* game.

## Level Builder Demo
The following video demonstrates the complete use of the level editor and game executables: 

<video src="https://github.com/user-attachments/assets/a7f9fa59-6207-494d-a7d4-eac32576fb12" width="1600" height="900" controls></video>

## Features Wishlist
Great joy was found in this project, and work on adding new features would continue if time permitted. Potential features include:
1. Resizable window and full screen modes, maintaining aspect ratio.
2. Procedural level generation with a custom algorithm or AI model.
3. Improved enemy pathfinding when near the player, potentially using a flow field across the level grid, generated with the BFS algorithm.
4. Further performance optimizations.
