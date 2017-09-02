import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# Custom for this program
from matchup_locs.ml2017 import matchup_locs


# CONSTANTS
HIGHTEAM = 'highTeam'
ID = 'id'
LOSER = 'loser'
LOWTEAM = 'lowTeam'
LTEAM = 'Lteam'
PRED = 'pred'
ROUND = 'round'
SEASON = 'Season'
SLOT = 'Slot'
TEAM = 'Team'
WINNER = 'winner'
WTEAM = 'Wteam'

# Column names used for matchup and slot mapping
roundlist = ['Roundof68', 'Roundof64', 'Roundof32', 'Sweet16', 'Elite8', 'Final4', 'Championship2']
slotlist = ['Slot68', 'Slot64', 'Slot32', 'Slot16', 'Slot8', 'Slot4', 'Slot2']

# Parameters for loading data
DATA_LIST = ["Teams",
             "TourneySeeds",
             "matchups2017",
             ]


def make_bracket(DATAPATH, submissionPath, emptyBracketPath, outputFilePath):
    # Default data loads
    for st in DATA_LIST:
        execstr = st + " = pd.read_csv(DATAPATH + " + "'" + st + ".csv', sep=',')"
        exec(execstr, globals())

    matchups = matchups2017

    # Default data transformations
    matchups[TEAM] = matchups[TEAM].astype(str)
    Teams_str = Teams
    Teams_str['Team_Id'] = Teams_str['Team_Id'].astype(str)

    submit = pd.read_csv(submissionPath)
    submit = submit.rename(columns={a:a.lower() for a in submit.columns.values})
    assert PRED in submit.columns.values
    assert ID in submit.columns.values
    
    def make_matchup_df(df, level, slot, previous_losers, dropna=False):
        """Organize data by self joining on matchups so we can generate matchup ids
        
        Params:
        -------
        df: matchups dataframe with matchups and slots columns for each team/seed
        level: round to generate level for
        slot: slot list for the above round (should probably be programmatically determined instead)
        dropna: use for Roundof68 only"""

        if dropna:
            out = df.merge(df.dropna(), on=level)
        else:
            out = df.merge(df, on=level)
        out = out[(out['Seed_x'] != out['Seed_y']) & (out['Seed_x'] < out['Seed_y'])]
        out['firstLower?'] = out['Team_x'] < out['Team_y']
        out[LOWTEAM] = pd.DataFrame([out['Team_x'], out['Team_y']]).min().astype(int).astype(str)
        out[HIGHTEAM] = pd.DataFrame([out['Team_x'], out['Team_y']]).max().astype(int).astype(str)
        out = out[out[slot+'_x'] != out[slot+'_y']]
        df1 = out.loc[out['firstLower?'] == True, :]
        df1 = df1.rename(columns={a: a.replace('x', LOWTEAM).replace('y', HIGHTEAM) for a in df1.columns})
        df2 = out.loc[out['firstLower?'] == False, :]
        df2 = df2.rename(columns={a: a.replace('x', HIGHTEAM).replace('y', LOWTEAM) for a in df2.columns})
        dfout = pd.concat([df1, df2])
        dfout = dfout[  ~(dfout[HIGHTEAM].isin(previous_losers))
                      & ~(dfout[LOWTEAM].isin(previous_losers))]
        return dfout

    def get_winners(df, level, matchupsdf, dropna=False):
        """Generate a new dataframe with winners and losers called out 
        based on the submission for each round
        Params:
        -------
        df: df created by the make_matchup_df function
        level: column name for round in matchupsdf
        matchupsdf: matchups dataframe with matchups and slots columns for each team/seed
        dropna: use for Roundof68 Only
        """
        df[ID] = df[SEASON + '_' + LOWTEAM].astype(str) + '_' + df[TEAM+'_'+LOWTEAM] + '_' + df[TEAM+'_'+HIGHTEAM]
        windf = submit.set_index(ID).join(df.set_index(ID), how='inner')

        windf[WINNER] = ''
        windf.loc[windf[PRED] >= 0.5, WINNER] = windf.loc[windf[PRED] >= 0.5, TEAM+'_'+LOWTEAM]
        windf.loc[windf[PRED] < 0.5, WINNER] = windf.loc[windf[PRED] < 0.5, TEAM+'_'+HIGHTEAM]
        windf[LOSER] = ''
        windf.loc[windf[PRED] < 0.5, LOSER] = windf.loc[windf[PRED] < 0.5, TEAM+'_'+LOWTEAM]
        windf.loc[windf[PRED] >= 0.5, LOSER] = windf.loc[windf[PRED] >= 0.5, TEAM+'_'+HIGHTEAM]
        windf['round'] = level
        
        if dropna:
            matchupsdf = matchupsdf.dropna()
        out = matchupsdf.merge(windf, left_on=TEAM, right_on=TEAM+'_'+LOWTEAM)

        return out[list(set(windf.columns.values)-set([level]))]

    # create dataframes laying out data for each possible matchup in each round
    rounds = {'Roundof68': make_matchup_df(matchups, 'Roundof68', 'Slot68', pd.DataFrame(), dropna=True)}
    losers = get_winners(rounds['Roundof68'], 'Roundof68', matchups)[LOSER]
    for r, s in zip(roundlist[1:], slotlist[1:]):
        rounds[r] = make_matchup_df(matchups, r, s, losers)
        losers = pd.concat((losers, get_winners(rounds[r], r, matchups)[LOSER])).reset_index(drop=True)


    # TODO: this should be reducible...just need to keep the winner/loser columns
    # determine winners of each possible matchup in each round
    #mlist = [get_winners(rounds['Roundof68'], 'Roundof68', matchups, dropna=True)]
    mlist = []
    for r in roundlist:
        mlist.append(get_winners(rounds[r], r, matchups))

    # Create backet summary dataframe
    bracket = pd.concat(mlist).reset_index(drop=True)
    bracket['matchup'] = ''
    for r in roundlist:
        r = r + '_' + LOWTEAM
        bracket.loc[bracket['round'] == r, 'matchup'] = bracket.loc[bracket['round'] == r, r]

    # Create ID column and add team names to bracket dataframe
    bracket[ID] = bracket[SEASON + '_' + LOWTEAM].astype(str) + '_' + bracket[TEAM + '_' + LOWTEAM] + '_' +                 pd.DataFrame([bracket[WINNER], bracket[LOSER]]).max().astype(int).astype(str)
    bracket = (
        bracket
        .merge(Teams_str, left_on=WINNER, right_on='Team_Id')
        .rename(columns={'Team_Name': 'Winner_Name'})
        .merge(Teams_str, left_on=LOSER, right_on='Team_Id')
        .rename(columns={'Team_Name': 'Loser_Name'})
        .drop(['Team_Id_x', 'Team_Id_y'], axis=1)
        .sort_values(by='matchup')
        .reset_index(drop=True)
    )

    # Finalize creation of data for the bracket image
    # Slot (representing unique slot for a team to be put in the bracket)
    # seed, team name, and percent likelihood of winning
    bracket['WSlot'] = -1
    bracket['LSlot'] = -1

    for slot, r in zip(slotlist, roundlist):
        bracket.loc[(bracket[ROUND] == r) & (bracket[WINNER] == bracket[LOWTEAM]), 'WSlot'] =         bracket.loc[(bracket[ROUND] == r) & (bracket[WINNER] == bracket[LOWTEAM]), slot + '_' + LOWTEAM]
        bracket.loc[(bracket[ROUND] == r) & (bracket[WINNER] == bracket[HIGHTEAM]), 'WSlot'] =         bracket.loc[(bracket[ROUND] == r) & (bracket[WINNER] == bracket[HIGHTEAM]), slot+'_'+HIGHTEAM]
        bracket.loc[(bracket[ROUND] == r) & (bracket[LOSER] == bracket[LOWTEAM]), 'LSlot'] =         bracket.loc[(bracket[ROUND] == r) & (bracket[LOSER] == bracket[LOWTEAM]), slot+'_'+LOWTEAM]
        bracket.loc[(bracket[ROUND] == r) & (bracket[LOSER] == bracket[HIGHTEAM]), 'LSlot'] =         bracket.loc[(bracket[ROUND] == r) & (bracket[LOSER] == bracket[HIGHTEAM]), slot+'_'+HIGHTEAM]

    bracket.loc[bracket[WINNER] == bracket[LOWTEAM], 'WSeed'] = bracket.loc[bracket[WINNER] == bracket[LOWTEAM], 'Seed_' + LOWTEAM]
    bracket.loc[bracket[WINNER] == bracket[HIGHTEAM], 'WSeed'] = bracket.loc[bracket[WINNER] == bracket[HIGHTEAM], 'Seed_' + HIGHTEAM]
    bracket.loc[bracket[LOSER] == bracket[LOWTEAM], 'LSeed'] = bracket.loc[bracket[LOSER] == bracket[LOWTEAM], 'Seed_' + LOWTEAM]
    bracket.loc[bracket[LOSER] == bracket[HIGHTEAM], 'LSeed'] = bracket.loc[bracket[LOSER] == bracket[HIGHTEAM], 'Seed_' + HIGHTEAM]

    bracket.loc[bracket[WINNER] == bracket[LOWTEAM], 'WPred'] = bracket.loc[bracket[WINNER] == bracket[LOWTEAM], PRED]
    bracket.loc[bracket[WINNER] == bracket[HIGHTEAM], 'WPred'] = 1 - bracket.loc[bracket[WINNER] == bracket[HIGHTEAM], PRED]
    bracket.loc[bracket[WINNER] == bracket[LOWTEAM], 'LPred'] = None
    bracket.loc[bracket[WINNER] == bracket[HIGHTEAM], 'LPred'] = None

    slots1 = bracket[['Loser_Name', 'LSlot', 'LSeed', 'LPred']].    rename(columns={'LSlot': SLOT, 'Loser_Name': 'Team_Name', 'LSeed': 'Seed', 'LPred': PRED})
    slots2 = bracket[['Winner_Name', 'WSlot', 'WSeed', 'WPred']].    rename(columns={'WSlot': SLOT, 'Winner_Name': 'Team_Name', 'WSeed': 'Seed', 'WPred': PRED})
    slots = pd.concat([slots1, slots2]).reset_index(drop=True)

    # Create input strings for image
    slotsdict = {}
    for row in slots.values:
        if ~np.isnan(row[3]):
            slotsdict[int(row[1])] = row[2] + ' ' + row[0] + ' ' + "{0:.2f}%".format(row[3] * 100)
        else:
            slotsdict[int(row[1])] = row[2] + ' ' + row[0]

    # Create input data for the image
    slotdata = {}
    for k in matchup_locs.keys():
        if k in slotsdict:
            slotdata[k] = (matchup_locs[k], slotsdict[k])
    if '%' in slotdata[134]:
        slotdata[135] = (matchup_locs[135], ' '.join([a for a in slotsdict[134].split(' ')[:-1]]))
    else:
        slotdata[135] = (matchup_locs[135], ' '.join([a for a in slotsdict[133].split(' ')[:-1]]))

    # Create bracket image
    # relevant: https://stackoverflow.com/questions/26649716/how-to-show-pil-image-in-ipython-notebook
    img = Image.open(emptyBracketPath)
    draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    # draw.text((x, y),"Sample Text",(r,g,b))
    for key, slot in slotdata.items():
        draw.text(slot[0], slot[1], (0, 0, 0))

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
    #plt.show() # for in notebook
    img.save(outputFilePath)

if __name__ == "__main__":

    # PARAMETERS
    DATAPATH = "data/"
    submissionPath = DATAPATH + 'submit.csv'
    emptyBracketPath = 'empty_brackets/2017.jpg'
    outputFilePath = 'predicted_bracket.jpg'

    # Run program
    make_bracket(DATAPATH, submissionPath, emptyBracketPath, outputFilePath)
