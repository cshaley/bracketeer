# bracketeer
Generate predicted bracket from a kaggle march madness machine learning competition submission.
https://www.kaggle.com/c/march-machine-learning-mania-2017

## Usage:
```
from bracket_builder import bracketeer
# directory structure should be /.../datapath/files.csv
b = bracketeer(2017, datapath)
b.make_bracket(submissionPath, outputFilePath)
```

## Dependencies
* matplotlib
* numpy
* pandas
* PIL

Additional input data/files not provided on kaggle:
* matchups.csv - matchup and bracket slot mapping for each seed in 2016
* empty_bracket.jpg - empty ncaa bracket
* matchup_locs.py - mapping dictionary from slots to image coordinates on empty_bracket.jpg

Output is a bracket filled in with team seeds, names, and winning likelihood for each game.  
The empty bracket is shown below.
![alt tag](https://raw.githubusercontent.com/cshaley/bracketeer/master/empty_brackets/2017.jpg)

The predicted bracket (this program's output) is shown below:
![alt tag](https://raw.githubusercontent.com/cshaley/bracketeer/master/sample/predicted_bracket.jpg)
