# predicted_bracket_generator
Generate predicted bracket from a kaggle march madness machine learning competition submission.
https://www.kaggle.com/c/march-machine-learning-mania-2017

## Usage:
from bracket_builder import make_bracket
make_bracket(DATAPATH, submissionPath, emptyBracketPath, outputFilePath)

Output is a bracket filled in with team seeds, names, and winning likelihood for each game.  
![alt tag](https://raw.githubusercontent.com/cshaley/predicted_bracket_generator/master/empty_bracket.jpg)
