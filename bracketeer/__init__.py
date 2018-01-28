import os

from binarytree import Node
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from .ordered_seed_list import seed_slot_map, num_slots
from .slot_coordinates import slot_coordinates

ID = 'id'
PRED = 'pred'
SEASON = 'season'
TEAM = 'team_name'


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


def build_bracket(output_path='output.png', 
    teamsPath='data/Teams.csv',
    seedsPath='data/TourneySeeds.csv',
    submissionPath='data/submit.csv'):

    assert os.path.isfile(teamsPath), '{} is not a valid file path for teamsPath.'.format(teamsPath)
    assert os.path.isfile(seedsPath), '{} is not a valid file path for seedsPath.'.format(seedsPath)
    assert os.path.isfile(submissionPath), '{} is not a valid file path for submissionPath.'.format(submissionPath)

    def cols_to_lower(df):
        return df.rename(columns={col: col.lower() for col in df.columns})

    teams_df = cols_to_lower(pd.read_csv(teamsPath))
    seeds_df = cols_to_lower(pd.read_csv(seedsPath))
    submit = cols_to_lower(pd.read_csv(submissionPath))

    df = seeds_df.merge(teams_df, left_on='team', right_on='team_id')
    keepcols = [SEASON, 'seed', 'team_id', TEAM]
    df = df.loc[df[SEASON] == 2017, keepcols].reset_index(drop=True)

    # Build the bracket
    # Leave off the last 8 (play-in seeds) when building the bracket
    # as they have custom locations
    bkt = build_tree(list(reversed(seed_slot_map.keys()))[:-8])

    # In seed_slot_map, each of these seeds has the following location:
    # W11   18
    # W16   10
    # Y16   42
    # Z11   66
    # So we set their children in the binary tree to the play-in seeds
    bkt[num_slots - 18].left = extNode(1)
    bkt[num_slots - 18].right = extNode(2)
    bkt[num_slots - 10].left = extNode(3)
    bkt[num_slots - 10].right = extNode(4)
    bkt[num_slots - 42].left = extNode(5)
    bkt[num_slots - 42].right = extNode(6)
    bkt[num_slots - 66].left = extNode(7)
    bkt[num_slots - 66].right = extNode(8)

    def get_team_id(seedMap):
        return (seedMap, df[df['seed'] == seed_slot_map[seedMap]]['team_id'].values[0])

    # Solve bracket using predictions
    for level in list(reversed(bkt.levels)):
        for ix, node in enumerate(level[0: len(level) // 2]):
            team1 = get_team_id(level[ix * 2].value)
            team2 = get_team_id(level[ix * 2 + 1].value)
            if team2[1] < team1[1]:
                temp = team1
                team1 = team2
                team2 = temp
            gid = '2017_{t1}_{t2}'.format(t1=team1[1], t2=team2[1])
            if submit[submit[ID] == gid][PRED].values[0] >= 0.5:
                level[ix * 2].parent.value = team1[0]
            else: 
                level[ix * 2].parent.value = team2[0]


    # Create data for writing to image
    slotdata = []
    for ix, key in enumerate([b for a in bkt.levels for b in a]):
        xy = slot_coordinates[2017][num_slots - ix]
        try:
            st = '{seed} {team}'.format(
                seed=seed_slot_map[key.value],
                team=df[df['seed']==seed_slot_map[key.value]][TEAM].values[0]
            )
        except IndexError as e:
            st = str(seed_slot_map[key.value])
        slotdata.append((xy, st))


    # Create bracket image
    # relevant:
    # https://stackoverflow.com/questions/26649716/how-to-show-pil-image-in-ipython-notebook
    emptyBracketPath = 'empty_brackets/2017.jpg'
    img = Image.open(emptyBracketPath)
    draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    # draw.text((x, y),"Sample Text",(r,g,b))
    for slot in slotdata:
        draw.text(slot[0], str(slot[1]), (0, 0, 0))

    dpi = 72
    margin = 0.05  # (5% of the width/height of the figure...)
    xpixels, ypixels = 940, 700

    # Make a figure big enough to accomodate an axis of xpixels by ypixels
    # as well as the ticklabels, etc...
    figsize = (1 + margin) * ypixels / dpi, (1 + margin) * xpixels / dpi
    fig = plt.figure(figsize=figsize, dpi=dpi)
    # Make the axis the right size...
    ax = fig.add_axes([margin, margin, 1 - 2*margin, 1 - 2*margin])

    ax.imshow(np.asarray(img))
    # plt.show() # for in notebook
    img.save(output_path)

if __name__ == '__main__':
    build_bracket()
