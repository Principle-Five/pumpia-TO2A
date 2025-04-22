# Introduction
This repository contains code to analyse the TO2A phantom using the [PumpIA](https://github.com/Principle-Five/pumpia) framework.

It is currently not validated and is provided as is, see the license for more information.

The collection contains the following tests:
- Phantom Width (Geometric linearity and distortion)
- Resolution
- Slice Width

# Usage

Users should make themselves familiar with the [PumpIA user interface](https://principle-five.github.io/pumpia/usage/user_interface.html)

To run the collection:
1. Clone the repository
2. Use an environment manager to install the requirements from `requirements.txt` or install the requirements using the command `pip install -r requirements.txt` when in the repository directory
3. Run the `run_to2a_collection.py` script

To use the collection:
1. Load the folder with the relevant images
2. Drag and drop the series containing the TO2A images into the viewer of the `Main` tab
3. Generate the ROIs and run analysis
4. Correct the context if required (see below)
    - Re-run generating ROIs
5. Move any ROIs as required, this should be done through their relevant modules.
    - Re-run analysis
6. Copy the results in the relevant format. Horizontal is tab separated, vertical is new line separated.

## Correcting Context

The context used for this collection is based on the Auto Phantom Context Manager provided with PumpIA, however it is expanded to find the rotation of the phantom.
It has 2 new options:
- MTF Box Side
- Wedges Side

The MTF Box Side and Wedges Side options must not be on the same axis. i.e. top and bottom or left and right.
The orthogonality of these options allows for the orientation and any flipping to be known.

To avoid the program resetting any selected values the option `Full Manual Control` must be selected. This does not reset when a new image is loaded.

# Calculating The Context

The context for this phantom is calculated as follows (selecting `show boxes` allows some of this working to be seen):
1. The boundary of the phantom is found
2. Four boxes are offset horizontally and vertically from the centre and their average value used to find the location of the relevant inserts
