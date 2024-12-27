# Project Name: PixelBuild

PixelBuild is a unique game concept that focuses on the creative and calming aspects of block-building. Inspired by the mechanics of Minecraft, this game provides an immersive experience where players can engage in world-building.

## What does the game do:

PixelBuild is a voxel-based game that allows players to interact with a dynamic 3D world. Players can:

- Place, delete, or modify blocks to shape their environment.
- Focus on creative expression and relaxation through building.

This emphasis on sandbox-style building without combat elements makes PixelBuild a versatile and engaging experience for players who enjoy creativity and exploration.

## Competitive Analysis:

While there are other block-building games like Minecraft, PixelBuild distinguishes itself by focusing solely on the creative and calming aspects of gameplay. PixelBuild provides a peaceful environment for players to express their creativity.

The main component that sets PixelBuild apart from similar games is its focus on breakable blocks and the ability to modify the environment freely. By removing combat elements, it provides a more creative gameplay experience that appeals to players seeking relaxation.

## Structural Plan:

Project will be organized in a way that it is categorized depending on the usage.
For example:
I will have util functions on one file, classes on another and base cmu_graphics on the other so that all the files are sorted and easy to understand. I will also add assets folder in which I will add my objects and pictures.

## Algorithmic plan:

The trickiest part would be implementing camera orientation for selecting a block. I would approach this through geometric formula where it could find the intersection of a camera line to the plane.

## Timeline plan:

- tp1: base graphics
- tp2: upgraded graphics
- tp3: creative update

## Version Control Plan:

To ensure efficient coding and backup:

- The project uses Git for version control.
- Code is hosted on a private GitHub repository.
- Features are developed incrementally, with regular commits and pushes to the main branch after testing.

  [Link to Github Repository](https://github.com/Enhmunh-E/112-term-project)

## Module List:

    cmu_graphics
    copy
    math
    time
    json
    datetime
    os

## Algorithms Used:

- [Cohen Sutherland Algorithm](https://en.wikipedia.org/wiki/Cohen%E2%80%93Sutherland_algorithm) for line clipping

- [Perspective Projection](https://en.wikipedia.org/wiki/3D_projection) for rendering on screen

- [Painter's Algorithm](https://en.wikipedia.org/wiki/Painter%27s_algorithm#:~:text=Similarly%2C%20the%20painter's%20algorithm%20sorts,this%20order%2C%20farthest%20to%20closest.) for rendering order

### TP 1 Update:

Created a basic graphics library which works but has plenty of bugs and non efficient.

### TP 2 Update:

Fixed bugs for 3d graphics and made the code more efficient by reducing the faces to draw.

### TP 3 Update:

I have implemented world saving, menu, start screens for a proper gameplay

## Pictures

### GamePlay

![tp2](./assets/tp2.png)

### Version Control

![tp2](./assets/versionControl.png)

## How to Run the project

1. Clone the game from github.
2. Install CMU Graphics in it.
3. Open cmu_graphics.py file and change the following code to this:
   (You can skip this if you are running this from the clone of original github repo)

   From:

   ```
   if event.type == pygame.MOUSEBUTTONDOWN and event.button <= 3:
       self.callUserFn(
           "onMousePress",
           (\*event.pos, event.button - 1),
       )
   ```

   To:

   ```
   if event.type == pygame.MOUSEBUTTONDOWN and event.button <= 3:
       self.callUserFn(
           "onMousePress",
           (\*event.pos, event.button - 1, event.button - 1),
       )
   ```

4. Run the app.py file.

## How to Play

### Movement Controls

#### Directional Movement: Use the arrow keys and , or . to move your position in the 3D space:

    Up Arrow: Move forward along the X-axis.
    Down Arrow: Move backward along the X-axis.
    Right Arrow: Move right along the Y-axis.
    Left Arrow: Move left along the Y-axis.
    Comma (,): Move up along the Z-axis.
    Period (.): Move down along the Z-axis.

#### View-Based Movement: Use W, A, S, D for movement relative to where you are looking:

    W: Move forward in the direction you are facing.

    S: Move backward in the direction you are facing.

    A: Strafe left (move sideways) relative to your view direction.

    D: Strafe right (move sideways) relative to your view direction.

### Orientation Control

#### Mouse Dragging: Click and drag the mouse to rotate your view:

    Dragging horizontally adjusts your view horizontally.

    Dragging vertically adjusts your view vertically.

### Block Interaction

#### Placing Blocks:

    Press F to place a block at a highlighted position in your view. Ensure there is no existing block at that position.

#### Deleting Blocks:

    Right-click (label 2) to delete a block at a selected position. Note that you cannot delete the last remaining block in the world.
    Block Selection

#### Change Block Type:

    Press number keys (0 to 9) to select different block types/colors. The number corresponds to different colors or types, with 0 selecting the tenth option.

### Exiting and Saving

#### Exit Game:

    Press Escape to save your current world state and return to the main menu. This action also plays a sound cue indicating the action.
