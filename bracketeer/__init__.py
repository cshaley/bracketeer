import os
import pkg_resources

from binarytree import Node
# import matplotlib.pyplot as plt # for notebook usage
# import numpy as np # for notebook usage
import pandas as pd
from PIL import Image, ImageDraw

from .slot_coordinates import slot_coordinates


__version__ = '0.1.5'

ID = 'id'
PRED = 'pred'
SEASON = 'season'
TEAM = 'teamname'


class extNode(Node):
    def __init__(self, value, left=None, right=None, parent=None):
        Node.__init__(self, value, left=left, right=right)
        if parent is not None and isinstance(parent, extNode):
            self.__setattr__('parent', parent)
        else:
            self.__setattr__('parent', None)

    def __setattr__(self, name, value):
        # Magically set the parent to self when a child is created
        if (name in ['left', 'right']
                and value is not None
                and isinstance(value, extNode)):
            value.parent = self
        object.__setattr__(self, name, value)


def build_tree(values):
    nodes = [None if v is None else extNode(v) for v in values]

    for index in range(1, len(nodes)):
        node = nodes[index]
        if node is not None:
            parent_index = (index - 1) // 2
            parent = nodes[parent_index]
            if parent is None:
                raise NodeNotFoundError(
                    'Parent node missing at index {}'
                    .format(parent_index)
                )
            setattr(parent, 'left' if index % 2 else 'right', node)
    return nodes[0] if nodes else None


def build_bracket(outputPath='output.png',
                  teamsPath='data/Teams.csv',
                  seedsPath='data/TourneySeeds.csv',
                  slotsPath='data/TourneySlots.csv',
                  submissionPath='data/submit.csv',
                  year=2017):

    assert os.path.isfile(teamsPath), '{} is not a valid file path for teamsPath.'.format(teamsPath)
    assert os.path.isfile(seedsPath), '{} is not a valid file path for seedsPath.'.format(seedsPath)
    assert os.path.isfile(slotsPath), '{} is not a valid file path for slotsPath.'.format(slotsPath)
    assert os.path.isfile(submissionPath), '{} is not a valid file path for submissionPath.'.format(submissionPath)

    def clean_col_names(df):
        return df.rename(columns={col: col.lower().replace('_', '') for col in df.columns})

    teams_df = clean_col_names(pd.read_csv(teamsPath))
    seeds_df = clean_col_names(pd.read_csv(seedsPath))
    slots_df = clean_col_names(pd.read_csv(slotsPath))
    submit = clean_col_names(pd.read_csv(submissionPath))

    df = seeds_df.merge(teams_df, left_on='teamid', right_on='teamid')
    keepcols = [SEASON, 'seed', 'teamid', TEAM]
    df = df.loc[df[SEASON] == year, keepcols].reset_index(drop=True)

    # Create bracket tree from slot data.  Create seed to slot mapping as well.
    s = slots_df[slots_df['season'] == year]
    seed_slot_map = {0: 'R6CH'}
    bkt = extNode(0)

    counter = 1
    current_nodes = [bkt]
    current_id = -1
    current_index = 0

    while current_nodes:
        next_nodes = []
        current_index = 0
        while current_index < len(current_nodes):
            node = current_nodes[current_index]
            if len(s[s['slot'] == seed_slot_map[node.value]].index) > 0:
                node.left = extNode(counter)
                node.right = extNode(counter + 1)
                seed_slot_map[counter] = s[s['slot'] == seed_slot_map[node.value]].values[0][2]
                seed_slot_map[counter + 1] = s[s['slot'] == seed_slot_map[node.value]].values[0][3]
                next_nodes.append(node.left)
                next_nodes.append(node.right)
                counter += 2
            current_index += 1
            current_id += 1
        current_nodes = next_nodes

    num_slots = len(seed_slot_map.keys())

    def get_team_id(seedMap):
        return (seedMap, df[df['seed'] == seed_slot_map[seedMap]]['teamid'].values[0])

    # Solve bracket using predictions
    # Also reate a map with slot, seed, game_id, pred
    pred_map = {}
    for level in list(reversed(bkt.levels)):
        for ix, node in enumerate(level[0: len(level) // 2]):
            team1 = get_team_id(level[ix * 2].value)
            team2 = get_team_id(level[ix * 2 + 1].value)
            if team2[1] < team1[1]:
                temp = team1
                team1 = team2
                team2 = temp
            gid = '{season}_{t1}_{t2}'.format(season=year, t1=team1[1], t2=team2[1])
            pred = submit[submit[ID] == gid][PRED].values[0]
            if pred >= 0.5:
                level[ix * 2].parent.value = team1[0]
                pred_map[level[ix * 2].value] = (seed_slot_map[level[ix * 2].value], gid, pred)
            else:
                level[ix * 2].parent.value = team2[0]
                pred_map[level[ix * 2 + 1].value] = (seed_slot_map[level[ix * 2].value], gid, 1 - pred)

    # Create data for writing to image
    slotdata = []
    for ix, key in enumerate([b for a in bkt.levels for b in a]):
        xy = slot_coordinates[2017][num_slots - ix]
        pred = ''
        if key.parent is not None and key.parent.value in pred_map\
                and pred_map[key.parent.value][0] == seed_slot_map[key.value]:
            pred = "{:.2f}".format(pred_map[key.parent.value][2] * 100)
        try:
            st = '{seed} {team} {pred}%'.format(
                seed=seed_slot_map[key.value],
                team=df[df['seed'] == seed_slot_map[key.value]][TEAM].values[0],
                pred=pred
            )
        except IndexError as e:
            st = str(seed_slot_map[key.value])
        slotdata.append((xy, st))

    # Create bracket image
    # relevant:
    # https://stackoverflow.com/questions/26649716/how-to-show-pil-image-in-ipython-notebook
    emptyBracketPath = pkg_resources.resource_filename('bracketeer', 'empty_brackets/2017.jpg')
    img = Image.open(emptyBracketPath)
    draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    # draw.text((x, y),"Sample Text",(r,g,b))
    for slot in slotdata:
        draw.text(slot[0], str(slot[1]), (0, 0, 0))

    # dpi = 72
    # margin = 0.05  # (5% of the width/height of the figure...)
    # xpixels, ypixels = 940, 700

    # Make a figure big enough to accomodate an axis of xpixels by ypixels
    # as well as the ticklabels, etc...
    # figsize = (1 + margin) * ypixels / dpi, (1 + margin) * xpixels / dpi
    # fig = plt.figure(figsize=figsize, dpi=dpi)
    # Make the axis the right size...
    # ax = fig.add_axes([margin, margin, 1 - 2*margin, 1 - 2*margin])

    # ax.imshow(np.asarray(img))
    # plt.show() # for in notebook
    img.save(outputPath)
