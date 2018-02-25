# bracketeer
[![PyPI](https://img.shields.io/pypi/v/bracketeer.svg)]()
[![Python](https://img.shields.io/pypi/pyversions/bracketeer.svg)]()
[![license](https://img.shields.io/github/license/cshaley/bracketeer.svg)]()


Generate predicted bracket from a kaggle march madness machine learning competition submission.
https://www.kaggle.com/c/march-machine-learning-mania-2017

## Installation
To install, do one of the following two things:

`pip install bracketeer`

OR

```
git clone https://github.com/cshaley/bracketeer.git
cd bracketeer
python setup.py install
```

## Usage:
```
from bracketeer import build_bracket
b = build_bracket(
        outputPath='output.png',
        teamsPath='data/Teams.csv',
        seedsPath='data/TourneySeeds.csv',
        submissionPath='data/submit.csv',
        slotsPath='data/TourneySlots.csv',
        year=2017
)
```

## Dependencies
* binarytree
* matplotlib
* numpy
* pandas
* PIL

Additional input data/files not provided on kaggle:
* empty_bracket.jpg - empty ncaa bracket
* slot_coordinates.py - mapping dictionary from slots to image coordinates on empty_bracket.jpg
* ordered_seed_list.py - order of seeds on the bracket

Output is a bracket filled in with team seeds, names, and winning likelihood for each game.  
The empty bracket is shown below.
![alt tag](https://raw.githubusercontent.com/cshaley/bracketeer/master/bracketeer/empty_brackets/2017.jpg)

The predicted bracket (this program's output) is shown below:
![alt tag](https://raw.githubusercontent.com/cshaley/bracketeer/master/sample/predicted_bracket.jpg)
