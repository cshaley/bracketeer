from bracketeer import build_bracket, extNode
import os

def test_build_bracket_2017():
    build_bracket(
        teamsPath='input/teams.csv',
        seedsPath='input/seeds.csv',
        slotsPath='input/slots.csv',
        submissionPath='input/sub.csv',
        year=2017,
        outputPath='output.png'
    )
    assert(os.path.isfile('output.png'))

def test_extNode():
    a = extNode(0)
    b = extNode(1, parent=a)
    a.right = b

