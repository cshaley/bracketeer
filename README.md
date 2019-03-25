# bracketeer
[![PyPI](https://img.shields.io/pypi/v/bracketeer.svg)]()
[![Python](https://img.shields.io/pypi/pyversions/bracketeer.svg)]()
[![license](https://img.shields.io/github/license/cshaley/bracketeer.svg)]()
![Travis](https://img.shields.io/travis/cshaley/bracketeer.svg)



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
        teamsPath='sample/Teams.csv',
        seedsPath='sample/NCAATourneySeeds.csv',
        submissionPath='sample/submit_example.csv',
        slotsPath='sample/NCAATourneySlots.csv',
        resultsPath=None,
        year=2019
)
```

`resultsPath` is an optional `CSV` file containing 
results of games already played. If it is provided then the
in the cases that the team the user predicted to win 
loses, it will substitute the actual winning team. This is
intended to visualize the predictions for later rounds, after the
match-ups are set.

Example, 

```
from bracketeer import build_bracket
b = build_bracket(
        outputPath='output_current.png',
        teamsPath='sample/Teams.csv',
        seedsPath='sample/NCAATourneySeeds.csv',
        submissionPath='sample/submit_example.csv',
        slotsPath='sample/NCAATourneySlots.csv',
        resultsPath='sample/current_results_example.csv',
        year=2019
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
![alt tag](/empty_brackets/2017.jpg)

The predicted bracket (this program's output) is shown below:
![alt tag](/sample/output.png)

The predicted bracket, applying known results for the first round:
![alt tag](/sample/output_current.png)
