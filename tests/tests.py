from bracketeer import build_bracket, extNode
import os
import pkg_resources

def test_build_bracket_2017():
    build_bracket(
        teamsPath=pkg_resources.resource_filename('tests', 'input/teams.csv'),
        seedsPath=pkg_resources.resource_filename('tests', 'input/seeds.csv'),
        slotsPath=pkg_resources.resource_filename('tests', 'input/slots.csv'),
        submissionPath=pkg_resources.resource_filename('tests', 'input/sub.csv'),
        year=2017,
        outputPath='output.png'
    )
    assert(os.path.isfile('output.png'))

def test_extNode():
    a = extNode(0)
    b = extNode(1, parent=a)
    a.right = b

