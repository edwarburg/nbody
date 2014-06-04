# N-body simulator

Simulates point masses in 2D space that gravitationally interact with one another.

## Dependencies

`pygame` and `jsonpickle`. Both can be installed with `sudo pip install`.

## To run:

`python main.py`

Load a saved file:

`python main.py examples/two_planets.json`

You can also specify the time delta used for each tick of the simulation. 

`python main.py --dt 500`

This increases the speed the masses appear to move, but can also make them behave more erratically at high velocities. The default is 300.

## How to use

* Add masses by clicking. You can give the mass an initial velocity by holding down the click and dragging in the direction you want the mass to move. 
* Change the size of the mass with the arrow keys: up and down increase by increments of 10,000, left and right scale by a factor of 10.
* Press `c` to clear all masses.
* Press `s` to save. Saves to a file named `save.json` in the current directory.
* Press `r` to reload the contents of `save.json`
* Press `q` to quit.