import streamlit as st
import pandas as pd
from highlight_text import ax_text,fig_text
import mplsoccer
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
from highlight_text import ax_text,fig_text
from PIL import Image
import imageio
from mplsoccer import PyPizza, add_image, FontManager
import math
import warnings
warnings.filterwarnings('ignore')

header = st.container()

with header:
    st.title("Pizza Chart Visulatisation")
    st.text("Please use this tool to create your own data visualisation for specific players")
    st.text("Created by Liam Henshaw on behalf of Heart of Midlothian Football Club")

with st.expander('Instructions - Please drop down and read'):
    st.write('''
    1.) Use the filters on the left side of the page to select the league, position, minimum minutes played, and maximum age of players in the data set.\n 
    2.) This will determine the sample size of players that percentile ratings will generate for.\n
    3.) To create your visual, confirm the player you want to see by inputting or copy & pasting the player's name, team and age into the text boxes below.\n
    4.) To save your visual, right click and save as.\n
    ''')

dataset = st.container()

####################################################################################

#Do not change these inputs unless you want to edit the text or background colour
text_color = 'black'
background='white'

##################################################################

df = pd.read_csv('https://raw.githubusercontent.com/HenshawAnalysis/Wyscout_Streamlit/main/Combined_Data_For_Streamlit.csv')
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)

with st.sidebar:
    st.header('Filters')
    league = st.selectbox('League', ('England Premier League', 'England Championship', 'Argentina Primera División', 'Brazil Serie A', 'Chile Primera División', 'China Super League','Estonia Meistriliiga', 'Finland Veikkausliiga', 'Georgia Erovnuli Liga', 'Germany 2. Bundesliga', 'Italy Serie B', 'Japan J2-League', 'Korea K-League 2', 'Latvia Virslīga', 'Malaysia Super League','Netherlands Eredivisie', 'Peru Primera División','Scotland Championship', 'Spain Segunda', 'Uruguay Primera División', 'Uzbekistan Super League', 'Venezuela Primera División',))
    pos = st.selectbox('Position', ('Centre Back', 'Fullback & Wingback', 'Midfielder', 'Attacking Midfielder & Winger', 'Striker', 'Striker & Wide Forward'))
    template = pos
    mins = st.number_input('Minimum Minutes Played', 300, max(df['Minutes played'].astype(int)), 500)
    maxage = st.slider('Max Age', 15, max(df.Age.astype(int)), 40)

 #####################################################################

#Creating Touches "Proxy" - Only If It Is Needed

df['90s'] = df['Minutes played'] /90
df['Passes'] = df['Passes per 90'] * df['90s']
df['Received passes'] = df['Received passes per 90'] * df['90s']
df['Interceptions'] = df['Interceptions per 90'] * df['90s']
df['Sliding tackles'] = df['Sliding tackles per 90'] * df['90s']
df['Dribbles'] = df['Dribbles per 90'] * df['90s']
df = df.round({'Passes': 0})
df = df.round({'Received passes': 0})
df = df.round({'Interceptions': 0})
df = df.round({'Sliding tackles': 0})
df = df.round({'Dribbles': 0})
df['Touches'] = df['Passes'] + df['Received passes'] + df['Interceptions'] + df['Sliding tackles'] + df['Dribbles']


#############################################################################

#Create any additonal metrics you want to use here

#NPxG
df['PenoxG'] = df['Penalties taken'] * 0.76
df['NPxG'] = df['xG'] - df['PenoxG']
df['NPxG per 90'] = df['NPxG'] / df['Minutes played'] * 90
df = df.round({'NPxG per 90': 2})

#xG per shot
df['Total Shots'] = df['Shots'] 
df['xG/Shot'] = df['NPxG'] / df['Total Shots']
df = df.round({'xG/Shot': 2})

#xA per 100 passes
df['90s'] = df['Minutes played'] /90
df['Total passes'] =  df['Passes per 90'] * df['90s']
df['100 passes'] = df['Total passes'] / 100
df['xA per 100 passes'] = df['xA'] / df['100 passes']
df = df.round({'xA per 100 passes': 2})

#Succesful progressive passes
df['Successful progressive passes'] = df['Accurate progressive passes, %'] /100 * df['Progressive passes per 90']
df = df.round({'Successful progressive passes': 2})

#Succesful final third passes
df['Successful final third passes'] = df['Accurate passes to final third, %'] /100 * df['Passes to final third per 90']
df = df.round({'Successful final third passes': 2})

#Defensive duels per touch
df['Defensive Duels'] = df['Defensive duels per 90'] * df['90s']
df['Defensive Duels Per Touch'] = df['Defensive Duels'] / df['Touches']
df = df.round({'Defensive Duels Per Touch': 4})

#Successful Defensive Actions duels per touch
df['Succ Defensive Actions'] = df['Successful defensive actions per 90'] * df['90s']
df['Successful Defensive Actions Per Touch'] = df['Succ Defensive Actions'] / df['Touches']
df = df.round({'Successful Defensive Actions Per Touch': 4})

#PAdj Tackles and Interceptions
df['PAdj Tackles & Interceptions'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']

#Successul crosses
df['Successful crosses'] = df['Accurate crosses, %'] /100 * df['Crosses per 90']
df = df.round({'Successful crosses': 2})

#Successul dribbles
df['Successful dribbles'] = df['Successful dribbles, %'] /100 * df['Dribbles per 90']
df = df.round({'Successful dribbles': 2})

#Removing any data with no values from Position, Team and Age
df = df.dropna(subset=['Position', 'Team within selected timeframe', 'Age']).reset_index(drop=True)

#Getting the player's main position
df['Main Position'] = ''
for i in range(len(df)):
    df['Main Position'][i] = df['Position'][i].split()[0]

#############################################################################################################################

# Filter data
dfPlayers = df[(df['Minutes played']>=mins) & (df['League']==league) & (df['Age']<=maxage)].copy()

if pos == 'Centre Back':
    dfPlayers = dfPlayers[(dfPlayers['Main Position'].str.contains('B'))]
    dfPlayers = dfPlayers[~dfPlayers['Main Position'].str.contains('WB')]
    dfPlayers = dfPlayers[~dfPlayers['Main Position'].str.contains('RB')]
    dfPlayers = dfPlayers[~dfPlayers['Main Position'].str.contains('LB')]

if pos == 'Fullback & Wingback':
    dfPlayers = dfPlayers[(dfPlayers['Main Position'].str.contains('LB')) |
                           (dfPlayers['Main Position'].str.contains('RB')) |
                           (dfPlayers['Main Position'].str.contains('WB'))]

if pos == 'Midfielder':
    dfPlayers = dfPlayers[(dfPlayers['Main Position'].str.contains('CMF')) |
                          	(dfPlayers['Main Position'].str.contains('DMF'))]

if pos == 'Attacking Midfielder & Winger':
    dfPlayers = dfPlayers[(dfPlayers['Main Position'].str.contains('AMF')) |
                            (dfPlayers['Main Position'].str.contains('WF')) |
                            (dfPlayers['Main Position'].str.contains('LAMF')) |
                            (dfPlayers['Main Position'].str.contains('RAMF')) |
                            (dfPlayers['Main Position'].str.contains('LW')) |
                            (dfPlayers['Main Position'].str.contains('RW'))]
    dfPlayers = dfPlayers[~dfPlayers['Main Position'].str.contains('WB')] 

if pos == 'Striker':
    dfPlayers = dfPlayers[(dfPlayers['Main Position'].str.contains('CF'))]

if pos == 'Striker & Wide Forward':
    dfPlayers = dfPlayers[(dfPlayers['Main Position'].str.contains('CF')) |
                            (dfPlayers['Main Position'].str.contains('RW')) |
                            (dfPlayers['Main Position'].str.contains('LW'))]
    dfPlayers = dfPlayers[~dfPlayers['Main Position'].str.contains('WB')] 

#############################################################################
dftable = dfPlayers

dfPlayers = dfPlayers.reset_index(drop=True)

#Setting up templates using the metrics you want
#############################################################################
#Centre Back Template      

if template == 'Centre Back':
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age',
                               "NPxG per 90","Offensive duels per 90","Offensive duels won, %",
                               'Progressive runs per 90',"Successful progressive passes","Accurate passes, %", 
                               'Accurate forward passes, %', "Forward passes per 90","Successful defensive actions per 90",
                               'Defensive duels per 90',"Defensive duels won, %","Aerial duels per 90",
                               "Aerial duels won, %", "Shots blocked per 90", "PAdj Tackles & Interceptions",]]

#Renaming metrics until all metrics   
        dfPlayers.rename(columns={"NPxG per 90": "Non-penalty xG",
                                "Non-penalty goals per 90": "Non-penalty goals",
                                "Shots per 90": "Shots",
                                "xG/Shot": "xG/Shot",
                                "Goal conversion, %": "Goal conversion %",                                
                                "Offensive duels per 90": "Offensive duels",
                                "Offensive duels won, %": "Offensive duel\nsuccess %",
                                "Progressive runs per 90": "Progressive runs",
                                "Successful progressive passes": "Progressive passes",
                                "Accurate passes, %": "Pass completion",
                                "Accurate forward passes, %": "Forward pass\ncompletion",
                                "Forward passes per 90": "Forward passes",
                                "Successful defensive actions per 90": "Successful\ndefensive actions",
                                "Defensive duels per 90": "Defensive duels",
                                "Defensive duels won, %": "Defensive duel\nsuccess %",
                                "Aerial duels per 90": "Aerial duels",
                                "Aerial duels won, %": "Aerial duel\nsuccess %",
                                "Shots blocked per 90": "Shots blocked",
                                "PAdj Tackles & Interceptions": "PAdj tackles\n& interceptions",
                                "Successful crosses": "Successful crosses",
                                "Successful dribbles": "Successful dribbles",
                                "Touches in box per 90": "Attacking box\ntouches",
                                "xA per 100 passes": "xA per 100\npasses",                                  
                                "Key passes per 90": "Key passes",
                                "Deep completions per 90": "Deep completions"
                                 }, inplace=True)
    
#############################################################################
#Fullback & Wingback Template      

if template == 'Fullback & Wingback':
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age',
                               "Successful crosses","Successful dribbles", "Offensive duels per 90",
                               "Offensive duels won, %","Touches in box per 90",'Progressive runs per 90',
                               "Successful progressive passes","Accurate passes, %", 
                               'xA per 100 passes', "Key passes per 90",'Defensive duels per 90',
                               "Defensive duels won, %","Aerial duels per 90",
                               "Aerial duels won, %", "PAdj Tackles & Interceptions",]]

#Renaming metrics until all metrics   
        dfPlayers.rename(columns={"NPxG per 90": "Non-penalty xG",
                                "Non-penalty goals per 90": "Non-penalty goals",
                                "Shots per 90": "Shots",
                                "xG/Shot": "xG/Shot",
                                "Goal conversion, %": "Goal conversion %",                                
                                "Offensive duels per 90": "Offensive duels",
                                "Offensive duels won, %": "Offensive duel\nsuccess %",
                                "Progressive runs per 90": "Progressive runs",
                                "Successful progressive passes": "Progressive passes",
                                "Accurate passes, %": "Pass completion",
                                "Accurate forward passes, %": "Forward pass\ncompletion",
                                "Forward passes per 90": "Forward passes",
                                "Successful defensive actions per 90": "Successful\ndefensive actions",
                                "Defensive duels per 90": "Defensive duels",
                                "Defensive duels won, %": "Defensive duel\nsuccess %",
                                "Aerial duels per 90": "Aerial duels",
                                "Aerial duels won, %": "Aerial duel\nsuccess %",
                                "Shots blocked per 90": "Shots blocked",
                                "PAdj Tackles & Interceptions": "PAdj tackles\n& interceptions",
                                "Successful crosses": "Successful crosses",
                                "Successful dribbles": "Successful dribbles",
                                "Touches in box per 90": "Attacking box\ntouches",
                                "xA per 100 passes": "xA per 100\npasses",                                  
                                "Key passes per 90": "Key passes",
                                "Deep completions per 90": "Deep completions"
                                 }, inplace=True)     
    
#############################################################################
#Midfielder Template        
if template == 'Midfielder':
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age',
                               "NPxG per 90","Shots per 90","Progressive runs per 90",
                               "Successful progressive passes","Accurate passes, %", 
                               'Accurate forward passes, %', "Forward passes per 90",'xA per 100 passes',
                               "Key passes per 90", "Deep completions per 90",'Defensive duels per 90',
                               "Defensive duels won, %","Aerial duels per 90",
                               "Aerial duels won, %", "PAdj Tackles & Interceptions",]]
        
#Renaming metrics until all metrics   
        dfPlayers.rename(columns={"NPxG per 90": "Non-penalty xG",
                                "Non-penalty goals per 90": "Non-penalty goals",
                                "Shots per 90": "Shots",
                                "xG/Shot": "xG/Shot",
                                "Goal conversion, %": "Goal conversion %",                                
                                "Offensive duels per 90": "Offensive duels",
                                "Offensive duels won, %": "Offensive duel\nsuccess %",
                                "Progressive runs per 90": "Progressive runs",
                                "Successful progressive passes": "Progressive passes",
                                "Accurate passes, %": "Pass completion",
                                "Accurate forward passes, %": "Forward pass\ncompletion",
                                "Forward passes per 90": "Forward passes",
                                "Successful defensive actions per 90": "Successful\ndefensive actions",
                                "Defensive duels per 90": "Defensive duels",
                                "Defensive duels won, %": "Defensive duel\nsuccess %",
                                "Aerial duels per 90": "Aerial duels",
                                "Aerial duels won, %": "Aerial duel\nsuccess %",
                                "Shots blocked per 90": "Shots blocked",
                                "PAdj Tackles & Interceptions": "PAdj tackles\n& interceptions",
                                "Successful crosses": "Successful crosses",
                                "Successful dribbles": "Successful dribbles",
                                "Touches in box per 90": "Attacking box\ntouches",
                                "xA per 100 passes": "xA per 100\npasses",                                  
                                "Key passes per 90": "Key passes",
                                "Deep completions per 90": "Deep completions"
                                 }, inplace=True)        

#############################################################################
#Att Mid & Winger Template        
if template == 'Attacking Midfielder & Winger':
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age',
                               "Non-penalty goals per 90","NPxG per 90","Shots per 90",
                               'xG/Shot',"Goal conversion, %","Successful crosses","Successful dribbles",
                               "Offensive duels per 90","Offensive duels won, %","xA per 100 passes", 
                               "Key passes per 90", "Deep completions per 90",'Defensive duels per 90',
                               "Defensive duels won, %", "PAdj Tackles & Interceptions",]]
        
#Renaming metrics until all metrics   
        dfPlayers.rename(columns={"NPxG per 90": "Non-penalty xG",
                                "Non-penalty goals per 90": "Non-penalty goals",
                                "Shots per 90": "Shots",
                                "xG/Shot": "xG/Shot",
                                "Goal conversion, %": "Goal conversion %",                                
                                "Offensive duels per 90": "Offensive duels",
                                "Offensive duels won, %": "Offensive duel\nsuccess %",
                                "Progressive runs per 90": "Progressive runs",
                                "Successful progressive passes": "Progressive passes",
                                "Accurate passes, %": "Pass completion",
                                "Accurate forward passes, %": "Forward pass\ncompletion",
                                "Forward passes per 90": "Forward passes",
                                "Successful defensive actions per 90": "Successful\ndefensive actions",
                                "Defensive duels per 90": "Defensive duels",
                                "Defensive duels won, %": "Defensive duel\nsuccess %",
                                "Aerial duels per 90": "Aerial duels",
                                "Aerial duels won, %": "Aerial duel\nsuccess %",
                                "Shots blocked per 90": "Shots blocked",
                                "PAdj Tackles & Interceptions": "PAdj tackles\n& interceptions",
                                "Successful crosses": "Successful crosses",
                                "Successful dribbles": "Successful dribbles",
                                "Touches in box per 90": "Attacking box\ntouches",
                                "xA per 100 passes": "xA per 100\npasses",                                  
                                "Key passes per 90": "Key passes",
                                "Deep completions per 90": "Deep completions"
                                 }, inplace=True)             
        
#############################################################################
#Striker Template        
if template == 'Striker':
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age',
                               "Non-penalty goals per 90","NPxG per 90","Shots per 90",
                               'xG/Shot',"Goal conversion, %","Touches in box per 90", 
                               'Dribbles per 90', "Successful dribbles, %","Offensive duels per 90",
                               "Offensive duels won, %","xA per 100 passes", "Defensive duels per 90",
                               "Aerial duels per 90","Aerial duels won, %", "PAdj Tackles & Interceptions",]]

#Renaming metrics until all metrics   
        dfPlayers.rename(columns={"NPxG per 90": "Non-penalty xG",
                                "Non-penalty goals per 90": "Non-penalty goals",
                                "Shots per 90": "Shots",
                                "xG/Shot": "xG/Shot",
                                "Goal conversion, %": "Goal conversion %",                                
                                "Offensive duels per 90": "Offensive duels",
                                "Offensive duels won, %": "Offensive duel\nsuccess %",
                                "Progressive runs per 90": "Progressive runs",
                                "Successful progressive passes": "Progressive passes",
                                "Accurate passes, %": "Pass completion",
                                "Accurate forward passes, %": "Forward pass\ncompletion",
                                "Forward passes per 90": "Forward passes",
                                "Successful defensive actions per 90": "Successful\ndefensive actions",
                                "Defensive duels per 90": "Defensive duels",
                                "Defensive duels won, %": "Defensive duel\nsuccess %",
                                "Aerial duels per 90": "Aerial duels",
                                "Aerial duels won, %": "Aerial duel\nsuccess %",
                                "Shots blocked per 90": "Shots blocked",
                                "PAdj Tackles & Interceptions": "PAdj tackles\n& interceptions",
                                "Successful crosses": "Successful crosses",
                                "Successful dribbles": "Successful dribbles",
                                "Touches in box per 90": "Attacking box\ntouches",
                                "xA per 100 passes": "xA per 100\npasses",                                  
                                "Key passes per 90": "Key passes",
                                "Deep completions per 90": "Deep completions",
                                "Dribbles per 90": "Dribbles attempted",
                                "Successful dribbles, %": "Dribble success %"
                                 }, inplace=True)     
#############################################################################
#Striker Template        
if template == 'Striker & Wide Forward':
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age',
                               "Non-penalty goals per 90","NPxG per 90","Shots per 90",
                               'xG/Shot',"Goal conversion, %","Touches in box per 90", 
                               'Dribbles per 90', "Successful dribbles, %","Offensive duels per 90",
                               "Offensive duels won, %","xA per 100 passes", "Defensive duels per 90",
                               "Aerial duels per 90","Aerial duels won, %", "PAdj Tackles & Interceptions",]]

#Renaming metrics until all metrics   
        dfPlayers.rename(columns={"NPxG per 90": "Non-penalty xG",
                                "Non-penalty goals per 90": "Non-penalty goals",
                                "Shots per 90": "Shots",
                                "xG/Shot": "xG/Shot",
                                "Goal conversion, %": "Goal conversion %",                                
                                "Offensive duels per 90": "Offensive duels",
                                "Offensive duels won, %": "Offensive duel\nsuccess %",
                                "Progressive runs per 90": "Progressive runs",
                                "Successful progressive passes": "Progressive passes",
                                "Accurate passes, %": "Pass completion",
                                "Accurate forward passes, %": "Forward pass\ncompletion",
                                "Forward passes per 90": "Forward passes",
                                "Successful defensive actions per 90": "Successful\ndefensive actions",
                                "Defensive duels per 90": "Defensive duels",
                                "Defensive duels won, %": "Defensive duel\nsuccess %",
                                "Aerial duels per 90": "Aerial duels",
                                "Aerial duels won, %": "Aerial duel\nsuccess %",
                                "Shots blocked per 90": "Shots blocked",
                                "PAdj Tackles & Interceptions": "PAdj tackles\n& interceptions",
                                "Successful crosses": "Successful crosses",
                                "Successful dribbles": "Successful dribbles",
                                "Touches in box per 90": "Attacking box\ntouches",
                                "xA per 100 passes": "xA per 100\npasses",                                  
                                "Key passes per 90": "Key passes",
                                "Deep completions per 90": "Deep completions",
                                "Dribbles per 90": "Dribbles attempted",
                                "Successful dribbles, %": "Dribble success %"
                                 }, inplace=True)     
    
#############################################################################
#Preview Table
final = dftable[['Player','Team within selected timeframe','Age','League','Main Position','Birth country', 'Contract expires',]]

final = final.loc[(final['League']==league)]

final.Age = final.Age.astype(int)
final.sort_values(by=['Age'], inplace=True)
final = final[final['Age']<=maxage].reset_index(drop=True)

with dataset:
	st.write(final)

#############################################################################


st.header("Enter the player's name, team and age to create the visual")
st.text("Feel free to type the information, or copy and paste it from the table above")
player = st.text_input("Player's Name", "")
team = st.text_input("Player's Team", "")
page = st.number_input("Player's Age", step=1)

#Season - Competition Data Base
complete = ['Argentina Primera División', 'Brazil Serie A', 'Chile Primera División', 'China Super League','Estonia Meistriliiga', 'Finland Veikkausliiga', 'Georgia Erovnuli Liga', 'Japan J2-League', 'Korea K-League 2','Latvia Virslīga','Malaysia Super League', 'Peru Primera División', 'Uruguay Primera División', 'Uzbekistan Super League', 'Venezuela Primera División']
incomplete = ['England Premier League', 'England Championship', 'Germany 2. Bundesliga', 'Italy Serie B','Netherlands Eredivisie', 'Scotland Championship', 'Spain Segunda']
summer = ['Argentina Primera División', 'Brazil Serie A', 'Chile Primera División', 'China Super League', 'Estonia Meistriliiga', 'Finland Veikkausliiga', 'Georgia Erovnuli Liga', 'Japan J2-League', 'Korea K-League 2','Latvia Virslīga','Malaysia Super League', 'Peru Primera División', 'Uruguay Primera División', 'Uzbekistan Super League', 'Venezuela Primera División']
winter = ['England Premier League', 'England Championship', 'Germany 2. Bundesliga', 'Italy Serie B', 'Netherlands Eredivisie', 'Scotland Championship', 'Spain Segunda']
if league in summer:
	ssn_ = ' 2022'
	if league in incomplete:
		xtratext = ' | Data as of 1/29/23'
	elif league in complete:
		xtratext = ' | Data final for 2022'
elif league in winter:
    ssn_ = ' 2022-23'
    if league in incomplete:
        xtratext = ' | Data as of 1/29/23'
    elif league in complete:
        xtratext = ' | Data final for 2022'


#############################################################################
pizzadf = dfPlayers

#NEW DATA FRAME FOR YOUR PLAYER / EDIT NAME
pizzaplayer = pizzadf.loc[dfPlayers['Player']==player].reset_index()
pizzaplayer = list(pizzaplayer.loc[0])
pizzaplayer = pizzaplayer[4:]

#get parameters
params = list(pizzadf.columns)

#drop the first list team because we don't need player name. Start at first metric
params = params[3:]

#Get Percentiles
values = []
for x in range(len(params)):
    values.append(math.floor(stats.percentileofscore(pizzadf[params[x]],pizzaplayer[x])))
    
    
#Get Percentiles
values = []
for x in range(len(params)):
    values.append(math.floor(stats.percentileofscore(pizzadf[params[x]],pizzaplayer[x])))
    
    
#SETTING UP PIZZA
# color for the slices and text for each of the templates

if template == 'Centre Back':
    slice_colors = ["#660000"] * 4 + ["#014F8A"] * 4 + ["#5A5A5A"] * 7
    text_colors = ["white"] * 15

if template == 'Fullback & Wingback':
    slice_colors = ["#660000"] * 6 + ["#014F8A"] * 4 + ["#5A5A5A"] * 5
    text_colors = ["white"] * 15
    
if template == 'Midfielder':
    slice_colors = ["#660000"] * 3 + ["#014F8A"] * 7 + ["#5A5A5A"] * 5
    text_colors = ["white"] * 15
    
if template == 'Attacking Midfielder & Winger':
    slice_colors = ["#660000"] * 7 + ["#014F8A"] * 5 + ["#5A5A5A"] * 3
    text_colors = ["white"] * 15

if template == 'Striker':
    slice_colors = ["#660000"] * 6 + ["#014F8A"] * 5 + ["#5A5A5A"] * 4
    text_colors = ["white"] * 15
    
if template == 'Striker & Wide Forward':
    slice_colors = ["#660000"] * 6 + ["#014F8A"] * 5 + ["#5A5A5A"] * 4
    text_colors = ["white"] * 15  

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    background_color=background,     # background color
    straight_line_color="#EBEBE9",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=0,               # linewidth of last circle
    other_circle_lw=0,              # linewidth for other circles
    inner_circle_size=5            # size of inner circle
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                          # list of values
    figsize=(9, 11),                # adjust figsize according to your need
    color_blank_space="same",        # use same color to fill blank space
    slice_colors=slice_colors,       # color for individual slices
    value_colors=text_colors,        # color for the value-text
    value_bck_colors=slice_colors,   # color for the blank spaces
    blank_alpha=0.4,                 # alpha for blank-space colors
    kwargs_slices=dict(
        edgecolor="white", zorder=2, linewidth=1
    ),                               # values to be used when plotting slices
    kwargs_params=dict(
        color="#000000", fontsize=11,
    ),                               # values to be used when adding parameter
    kwargs_values=dict(
        color="white", fontsize=12,
        bbox=dict(
            edgecolor="white", facecolor="cornflowerblue",
            boxstyle="round,pad=0.2", lw=1
        )
    )                                # values to be used when adding parameter-values
)

# add title
fig.text(
    0.515, 0.975, "%s (%i) - %s" %(player, page, team),
    size=16, fontweight='bold', ha="center", color="#000000"
)

# add subtitle
fig.text(
    0.515, 0.956,
    "Percentile Rank vs %ss - "%(template) + league + ssn_,
    size=14,
    ha="center", color="#000000"
)

# add credits
CREDIT_1 = "Graphic: Liam Henshaw on behalf of Heart of Midlothian FC"
CREDIT_2 = "Template: %s" %(template)
CREDIT_3 = "Notes: All units are per 90mins | Data is via Wyscout | %s+ mins" %(mins)

fig.text(
    0.94, 0.000, f"{CREDIT_1}\n{CREDIT_2}\n{CREDIT_3}", size=9,
    color="#545454", fontstyle='italic',
    ha="right"
)

# add text
fig.text(
    0.35, 0.93, "Attacking     Possession     Defending", size=14,
    color="#000000"
)

# add rectangles
fig.patches.extend([
    plt.Rectangle(
        (0.32, 0.9275), 0.025, 0.021, fill=True, color="#660000",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.445, 0.9275), 0.025, 0.021, fill=True, color="#014F8A",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.582, 0.9275), 0.025, 0.021, fill=True, color="#5A5A5A",
        transform=fig.transFigure, figure=fig
    ),
])

im2 = imageio.imread('HeartsLogo.png')

# add image
ax_image = add_image(
    im2, fig, left=0.09, bottom=-0.01, width=0.13, height=0.127
)   # these values might differ when you are plotting

plt.show()
st.pyplot(fig)


##########################################################################################################
with st.expander('Latest Data Updates'):
    st.write('''
    England Premier League - Updated 16/02/2023\n
    England Championship - Updated 16/02/2023\n
	Argentina Primera División - 2022 Completed Season\n
	Brazil Serie A - 2022 Completed Season\n
	Chile Primera División - 2022 Completed Season\n
	China Super League - 2022 Completed Season\n
	Estonia Meistriliiga - 2022 Completed Season\n
    Finland Veikkausliiga - 2022 Completed Season\n
    Georgia Erovnuli Liga - 2022 Completed Season\n
    Germany 2. Bundesliga - Updated 17/02/2023\n
    Italy Serie B - Updated 17/02/2023\n
    Japan J2-League - 2022 Completed Season\n
    Korea K-League 2 - 2022 Completed Season\n
    Latvia Virslīga - 2022 Completed Season\n
    Malaysia Super League - 2022 Completed Season\n
    Netherlands Eredivisie - Updated 17/02/2023\n
    Peru Primera División - 2022 Completed Season\n
    Scotland Championship - Updated 17/02/2023\n
    Spain Segunda - Updated 17/02/2023\n
    Uruguay Primera División - 2022 Completed Season\n
    Uzbekistan Super League - 2022 Completed Season\n
    Venezuela Primera División - 2022 Completed Season\
    ''')