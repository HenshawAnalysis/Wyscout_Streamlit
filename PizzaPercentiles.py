import streamlit as st
st.set_page_config(layout="wide")
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
    st.title("HoM Data Visualisation Tool")
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

df = pd.read_csv('https://raw.githubusercontent.com/HenshawAnalysis/Wyscout_Streamlit/main/Wyscout_League_Export.csv')
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)

with st.sidebar:
    st.header('Filters')
    league = st.selectbox('League', ('England Premier League', 'England Championship','England National League North South', 'Argentina Primera Division 2022','Argentina Primera Division 2023','Albania Superiore League','Austria Bundesliga','Austria Bundesliga 2021-22','Belarus Premier League 2022','Belgium First Division B', 'Brazil Serie A 2022','Brazil Serie B 2022','Bulgaria First League', 'Chile Primera Division 2022','Chile Primera Division 2023', 'China Super League 2022','Colombia Primera A 2022','Colombia Primera A 2023','Costa Rica Primera Division','Cyprus First Division','Czech Fortuna Liga','Ecuador Serie A 2022','Egypt Premier League','Estonia Meistriliiga 2022', 'Finland Veikkausliiga 2022','Finland Ykkönen 2022', 'Georgia Erovnuli Liga 2022', 'Germany 2. Bundesliga','Greece Super League','Hungary NB1','Indonesia Liga 1','Italy Campionato Primavera 1', 'Italy Serie B', 'Japan J2-League 2022','Japan J2-League 2023', 'Korea K-League 2 2022', 'Latvia Virsliga 2022','Malaysia Super League 2022','Mexico Liga MX','Morocco Botola Pro','Netherlands Eredivisie','Netherlands Eerste Divisie','Northern Ireland Premiership', 'Peru Primera Division 2022','Portugal Primeira Liga','Portugal Segunda Liga','Romania SuperLiga','Scotland Championship','Slovenia Prva Liga','South Africa PSL','Spain La Liga','Spain Primera Division RFEF', 'Spain Segunda','Turkey Super Lig','Ukraine Premier League', 'Uruguay Primera Division 2022','Uruguay Primera Division 2023', 'Uzbekistan Super League 2022', 'Venezuela Primera Division 2022',))
    pos = st.selectbox('Position', ('Centre Back', 'Fullback & Wingback', 'Midfielder', 'Attacking Midfielder & Winger', 'Striker', 'Striker & Wide Forward'))
    template = pos
    mins = st.number_input('Minimum Minutes Played', 300, max(df['Minutes played'].astype(int)), 500)
    maxage = st.slider('Max Age', 15, max(df.Age.astype(int)), 45)

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

#Smart passes
df['Smart passes'] = df['Accurate smart passes, %'] /100 * df['Smart passes per 90']
df = df.round({'Smart passes': 2})

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
dfPercentiles = dfPlayers

dfPlayers = dfPlayers.reset_index(drop=True)

#Setting up templates using the metrics you want
#############################################################################
#Centre Back Template      

if template == 'Centre Back':
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age', 'Minutes played',
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
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age', 'Minutes played',
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
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age', 'Minutes played',
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
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age', 'Minutes played',
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
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age', 'Minutes played',
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
        dfPlayers = dfPlayers[["Player",'Team within selected timeframe', 'Age', 'Minutes played',
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
final = dftable[['Player','Team within selected timeframe','Age','League','Main Position','Minutes played','Birth country', 'Contract expires',]]

final = final.loc[(final['League']==league)]

final.Age = final.Age.astype(int)
final.sort_values(by=['Age'], inplace=True)
final = final[final['Age']<=maxage].reset_index(drop=True)

with dataset:
	st.write(final)

#############################################################################


st.header("Enter the player's name, team and age to create the visuals")
st.text("Feel free to type the information, or copy and paste it from the table above")
player = st.text_input("Player's Name", "")
team = st.text_input("Player's Team", "")
page = st.number_input("Player's Age", step=1)

#Season - Competition Data Base
complete = ['Colombia Primera A 2022','Colombia Primera A 2023', 'Ecuador Serie A 2022', 'Peru Primera Division 2022', 'Uruguay Primera Division 2022','Uruguay Primera Division 2023', 'Venezuela Primera Division 2022', 'Argentina Primera Division 2022','Argentina Primera Division 2023','Austria Bundesliga 2021-22','Belarus Premier League 2022', 'Brazil Serie A 2022','Brazil Serie A 2023', 'Chile Primera Division 2022','Chile Primera Division 2023', 'China Super League 2022', 'Estonia Meistriliiga 2022', 'Finland Veikkausliiga 2022','Finland Ykkönen 2022', 'Georgia Erovnuli Liga 2022', 'Korea K-League 2 2022', 'Latvia Virsliga 2022', 'Malaysia Super League 2022', 'Uzbekistan Super League 2022', 'Japan J2-League 2022','Japan J2-League 2023']
summer = ['Argentina Primera Division', 'Brazil Serie A', 'Chile Primera Division', 'China Super League','Colombia Primera A','Ecuador Serie A', 'Estonia Meistriliiga', 'Finland Veikkausliiga', 'Georgia Erovnuli Liga', 'Japan J2-League', 'Korea K-League 2','Latvia Virsliga','Malaysia Super League', 'Peru Primera Division', 'Uruguay Primera Division', 'Uzbekistan Super League', 'Venezuela Primera Division']
winter = ['England Premier League', 'England Championship','England National League North South','Albania Superiore League','Austria Bundesliga','Belgium First Division B','Bulgaria First League', 'Costa Rica Primera Division','Cyprus First Division','Czech Fortuna Liga','Egypt Premier League', 'Germany 2. Bundesliga','Greece Super League','Hungary NB1','Indonesia Liga 1','Italy Campionato Primavera 1', 'Italy Serie B','Mexico Liga MX','Morocco Botola Pro', 'Netherlands Eredivisie','Netherlands Eerste Divisie','Northern Ireland Premiership','Portugal Primeira Liga','Portugal Segunda Liga','Romania SuperLiga', 'Scotland Championship','Slovenia Prva Liga','South Africa PSL','Spain La Liga','Spain Primera Division RFEF', 'Spain Segunda','Turkey Super Lig','Ukraine Premier League']
if league in summer:
	ssn_ = ' 2022'

elif league in winter:
    ssn_ = ' 2022-23'

elif league in complete:
    ssn_ = ''

#############################################################################
pizzadf = dfPlayers

#NEW DATA FRAME FOR YOUR PLAYER / EDIT NAME
pizzaplayer = pizzadf.loc[dfPlayers['Player']==player].reset_index()

#Get the mins played value for specific player needed for visual
minplay = int(pizzaplayer['Minutes played'].values[0])

#Getting just the data values for visual
pizzaplayer = list(pizzaplayer.loc[0])
pizzaplayer = pizzaplayer[5:]

#get parameters
params = list(pizzadf.columns)

#drop the first list team because we don't need player name. Start at first metric
params = params[4:]

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
    figsize=(10, 10),                # adjust figsize according to your need
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
    0.515, 0.975, "%s (%i) - %s\n" %(player, page, team),
    size=16, fontweight='bold', ha="center", color="#000000"
)

# add subtitle
fig.text(
    0.515, 0.956,
    "%i minutes played\nPercentile Rank vs %ss - "%(minplay, template) + league + ssn_,
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
)   # these values might differ when you are pl

visuals = st.container()
with visuals:

	disp1_col , disp2_col = st.columns(2)
disp1_col.pyplot(fig)
#######################################################################################################################

#Renaming Metrics
dfPercentiles['Successful defensive actions'] = dfPercentiles['Successful defensive actions per 90'] 
dfPercentiles['Defensive duels'] = dfPercentiles['Defensive duels per 90'] 
dfPercentiles['Defensive duel success %'] = dfPercentiles['Defensive duels won, %'] 
dfPercentiles['Aerial duels'] = dfPercentiles['Aerial duels per 90'] 
dfPercentiles['Aerial duel success %'] = dfPercentiles['Aerial duels won, %'] 
dfPercentiles['Shots blocked'] = dfPercentiles['Shots blocked per 90'] 
dfPercentiles['PAdj interceptions'] = dfPercentiles['PAdj Interceptions'] 
dfPercentiles['Successful attacking actions'] = dfPercentiles['Successful attacking actions per 90']
dfPercentiles['Non-penalty xG'] = dfPercentiles['NPxG per 90'] 
dfPercentiles['Non-penalty goals'] = dfPercentiles['Non-penalty goals per 90'] 
dfPercentiles['Shots'] = dfPercentiles['Shots per 90'] 
dfPercentiles['Crosses'] = dfPercentiles['Crosses per 90'] 
dfPercentiles['Crossing accuracy %'] = dfPercentiles['Accurate crosses, %']
dfPercentiles['Dribbles'] = dfPercentiles['Dribbles per 90']
dfPercentiles['Dribble success %'] = dfPercentiles['Successful dribbles, %']
dfPercentiles['Offensive duels'] = dfPercentiles['Offensive duels per 90'] 
dfPercentiles['Offensive duel success %'] = dfPercentiles['Offensive duels won, %'] 
dfPercentiles['Attacking box touches'] = dfPercentiles['Touches in box per 90'] 
dfPercentiles['Attacking box touches per 90'] = dfPercentiles['Touches in box per 90'] 
dfPercentiles['Progressive runs'] = dfPercentiles['Progressive runs per 90'] 
dfPercentiles['Pass completion %'] = dfPercentiles['Accurate passes, %'] 
dfPercentiles['Forward passes'] = dfPercentiles['Forward passes per 90'] 
dfPercentiles['Forward pass completion %'] = dfPercentiles['Accurate forward passes, %'] 
dfPercentiles['Second assists'] = dfPercentiles['Second assists per 90'] 
dfPercentiles['Key passes'] = dfPercentiles['Key passes per 90']
dfPercentiles['Received passes'] = dfPercentiles['Received passes per 90'] 
dfPercentiles['Passes to penalty area'] = dfPercentiles['Passes to penalty area per 90'] 
dfPercentiles['Passes to penalty area success %'] = dfPercentiles['Accurate passes to penalty area, %'] 
dfPercentiles['Deep completions'] = dfPercentiles['Deep completions per 90']
dfPercentiles['Goal conversion %'] = dfPercentiles['Goal conversion, %'] 
dfPercentiles['Fouls won'] = dfPercentiles['Fouls suffered per 90'] 
dfPercentiles['Shots on target %'] = dfPercentiles['Shots on target, %'] 
dfPercentiles['Shot assists'] = dfPercentiles['Shot assists per 90'] 
dfPercentiles['Offensive duels success %'] = dfPercentiles['Offensive duels won, %'] 
dfPercentiles['Progressive passes'] = dfPercentiles['Successful progressive passes'] 




percentilesdf = dfPercentiles[dfPercentiles["Player"] == player].copy()

#Bar Chart Percentiles
CB1 = "Non-penalty xG"
CB2 = "Offensive duels"
CB3 = "Offensive duels success %"
CB4 = "Successful attacking actions"
CB5 = "Progressive runs"
CB6 = "Progressive passes"
CB7 = "Pass completion %"
CB8 = "Forward pass completion %"
CB9 = "Forward passes"
CB10 = "Successful defensive actions"
CB11 = "Defensive duels"
CB12 = "Defensive duel success %"
CB13 = "Aerial duels"
CB14 = "Aerial duel success %"
CB15 = "Shots blocked"
CB16 = "PAdj interceptions"

FBWB1 = "Non-penalty xG"
FBWB2 = "Shots"
FBWB3 = "Offensive duels"
FBWB4 = "Offensive duels success %"
FBWB5 = "Dribbles"
FBWB6 = "Dribble success %"
FBWB7 = "Crosses"
FBWB8 = "Crossing accuracy %"
FBWB9 = "Attacking box touches"
FBWB10 = "Successful attacking actions"
FBWB11 = "Progressive runs"
FBWB12 = "Progressive passes"
FBWB13 = "xA per 100 passes"
FBWB14 = "Key passes"
FBWB15 = "Second assists"
FBWB16 = "Pass completion %"
FBWB17 = "Forward passes"
FBWB18 = "Forward pass completion %"
FBWB19 = "Passes to penalty area"
FBWB20 = "Passes to penalty area success %"
FBWB21 = "Successful defensive actions"
FBWB22 = "Defensive duels"
FBWB23 = "Defensive duel success %"
FBWB24 = "Aerial duels"
FBWB25 = "Aerial duel success %"
FBWB26 = "Shots blocked"
FBWB27 = "PAdj interceptions"

MID1 = "Non-penalty xG"
MID2 = "Shots"
MID3 = "Offensive duels"
MID4 = "Offensive duels success %"
MID5 = "Dribbles"
MID6 = "Dribble success %"
MID7 = "Attacking box touches"
MID8 = "Successful attacking actions"
MID9 = "Progressive runs"
MID10 = "Progressive passes"
MID11 = "xA per 100 passes"
MID12 = "Key passes"
MID13 = "Second assists"
MID14 = "Smart passes"
MID15 = "Deep completions"
MID16 = "Received passes"
MID17 = "Pass completion %"
MID18 = "Forward passes"
MID19 = "Forward pass completion %"
MID20 = "Passes to penalty area"
MID21 = "Passes to penalty area success %"
MID22 = "Successful defensive actions"
MID23 = "Defensive duels"
MID24 = "Defensive duel success %"
MID25 = "Aerial duels"
MID26 = "Aerial duel success %"
MID27 = "Shots blocked"
MID28 = "PAdj interceptions"

AMW1 = "Non-penalty xG"
AMW2 = "Non-penalty goals"
AMW3 = "Goal conversion %"
AMW4 = "xG/Shot"
AMW5 = "Shots"
AMW6 = "Offensive duels"
AMW7 = "Offensive duels success %"
AMW8 = "Dribbles"
AMW9 = "Dribble success %"
AMW10 = "Attacking box touches"
AMW11 = "Crosses"
AMW12 = "Crossing accuracy %"
AMW13 = "Successful attacking actions"
AMW14 = "Progressive runs"
AMW15 = "Progressive passes"
AMW16 = "Fouls won"
AMW17 = "xA per 100 passes"
AMW18 = "Key passes"
AMW19 = "Second assists"
AMW20 = "Smart passes"
AMW21 = "Deep completions"
AMW22 = "Received passes"
AMW23 = "Pass completion %"
AMW24 = "Forward passes"
AMW25 = "Forward pass completion %"
AMW26 = "Passes to penalty area"
AMW27 = "Passes to penalty area success %"
AMW28 = "Successful defensive actions"
AMW29 = "Defensive duels"
AMW30 = "Defensive duel success %"
AMW31 = "Aerial duels"
AMW32 = "Aerial duel success %"
AMW33 = "Shots blocked"
AMW34 = "PAdj interceptions"

ST1 = "Non-penalty xG"
ST2 = "Non-penalty goals"
ST3 = "Goal conversion %"
ST4 = "Shots on target %"
ST5 = "Shots"
ST6 = "xG/Shot"
ST7 = "Offensive duels"
ST8 = "Offensive duels success %"
ST9 = "Dribbles"
ST10 = "Dribble success %"
ST11 = "Attacking box touches"
ST12 = "Successful attacking actions"
ST13 = "Fouls won"
ST14 = "xA per 100 passes"
ST15 = "Shot assists"
ST16 = "Second assists"
ST17 = "Deep completions"
ST18 = "Received passes"
ST19 = "Successful defensive actions"
ST20 = "Defensive duels"
ST21 = "Defensive duel success %"
ST22 = "Aerial duels"
ST23 = "Aerial duel success %"
ST24 = "PAdj interceptions"

#Get the specific player's value
xCB1 = percentilesdf[CB1].values[0]
xCB2 = percentilesdf[CB2].values[0]
xCB3 = percentilesdf[CB3].values[0]
xCB4 = percentilesdf[CB4].values[0]
xCB5 = percentilesdf[CB5].values[0]
xCB6 = percentilesdf[CB6].values[0]
xCB7 = percentilesdf[CB7].values[0]
xCB8 = percentilesdf[CB8].values[0]
xCB9 = percentilesdf[CB9].values[0]
xCB10 = percentilesdf[CB10].values[0]
xCB11 = percentilesdf[CB11].values[0]
xCB12 = percentilesdf[CB12].values[0]
xCB13 = percentilesdf[CB13].values[0]
xCB14 = percentilesdf[CB14].values[0]
xCB15 = percentilesdf[CB15].values[0]
xCB16 = percentilesdf[CB16].values[0]

xFBWB1 = percentilesdf[FBWB1].values[0]
xFBWB2 = percentilesdf[FBWB2].values[0]
xFBWB3 = percentilesdf[FBWB3].values[0]
xFBWB4 = percentilesdf[FBWB4].values[0]
xFBWB5 = percentilesdf[FBWB5].values[0]
xFBWB6 = percentilesdf[FBWB6].values[0]
xFBWB7 = percentilesdf[FBWB7].values[0]
xFBWB8 = percentilesdf[FBWB8].values[0]
xFBWB9 = percentilesdf[FBWB9].values[0]
xFBWB10 = percentilesdf[FBWB10].values[0]
xFBWB11 = percentilesdf[FBWB11].values[0]
xFBWB12 = percentilesdf[FBWB12].values[0]
xFBWB13 = percentilesdf[FBWB13].values[0]
xFBWB14 = percentilesdf[FBWB14].values[0]
xFBWB15 = percentilesdf[FBWB15].values[0]
xFBWB16 = percentilesdf[FBWB16].values[0]
xFBWB17 = percentilesdf[FBWB17].values[0]
xFBWB18 = percentilesdf[FBWB18].values[0]
xFBWB19 = percentilesdf[FBWB19].values[0]
xFBWB20 = percentilesdf[FBWB20].values[0]
xFBWB21 = percentilesdf[FBWB21].values[0]
xFBWB22 = percentilesdf[FBWB22].values[0]
xFBWB23 = percentilesdf[FBWB23].values[0]
xFBWB24 = percentilesdf[FBWB24].values[0]
xFBWB25 = percentilesdf[FBWB25].values[0]
xFBWB26 = percentilesdf[FBWB26].values[0]
xFBWB27 = percentilesdf[FBWB27].values[0]

xMID1 = percentilesdf[MID1].values[0]
xMID2 = percentilesdf[MID2].values[0]
xMID3 = percentilesdf[MID3].values[0]
xMID4 = percentilesdf[MID4].values[0]
xMID5 = percentilesdf[MID5].values[0]
xMID6 = percentilesdf[MID6].values[0]
xMID7 = percentilesdf[MID7].values[0]
xMID8 = percentilesdf[MID8].values[0]
xMID9 = percentilesdf[MID9].values[0]
xMID10 = percentilesdf[MID10].values[0]
xMID11 = percentilesdf[MID11].values[0]
xMID12 = percentilesdf[MID12].values[0]
xMID13 = percentilesdf[MID13].values[0]
xMID14 = percentilesdf[MID14].values[0]
xMID15 = percentilesdf[MID15].values[0]
xMID16 = percentilesdf[MID16].values[0]
xMID17 = percentilesdf[MID17].values[0]
xMID18 = percentilesdf[MID18].values[0]
xMID19 = percentilesdf[MID19].values[0]
xMID20 = percentilesdf[MID20].values[0]
xMID21 = percentilesdf[MID21].values[0]
xMID22 = percentilesdf[MID22].values[0]
xMID23 = percentilesdf[MID23].values[0]
xMID24 = percentilesdf[MID24].values[0]
xMID25 = percentilesdf[MID25].values[0]
xMID26 = percentilesdf[MID26].values[0]
xMID27 = percentilesdf[MID27].values[0]
xMID28 = percentilesdf[MID28].values[0]

xAMW1 = percentilesdf[AMW1].values[0]
xAMW2 = percentilesdf[AMW2].values[0]
xAMW3 = percentilesdf[AMW3].values[0]
xAMW4 = percentilesdf[AMW4].values[0]
xAMW5 = percentilesdf[AMW5].values[0]
xAMW6 = percentilesdf[AMW6].values[0]
xAMW7 = percentilesdf[AMW7].values[0]
xAMW8 = percentilesdf[AMW8].values[0]
xAMW9 = percentilesdf[AMW9].values[0]
xAMW10 = percentilesdf[AMW10].values[0]
xAMW11 = percentilesdf[AMW11].values[0]
xAMW12 = percentilesdf[AMW12].values[0]
xAMW13 = percentilesdf[AMW13].values[0]
xAMW14 = percentilesdf[AMW14].values[0]
xAMW15 = percentilesdf[AMW15].values[0]
xAMW16 = percentilesdf[AMW16].values[0]
xAMW17 = percentilesdf[AMW17].values[0]
xAMW18 = percentilesdf[AMW18].values[0]
xAMW19 = percentilesdf[AMW19].values[0]
xAMW20 = percentilesdf[AMW20].values[0]
xAMW21 = percentilesdf[AMW21].values[0]
xAMW22 = percentilesdf[AMW22].values[0]
xAMW23 = percentilesdf[AMW23].values[0]
xAMW24 = percentilesdf[AMW24].values[0]
xAMW25 = percentilesdf[AMW25].values[0]
xAMW26 = percentilesdf[AMW26].values[0]
xAMW27 = percentilesdf[AMW27].values[0]
xAMW28 = percentilesdf[AMW28].values[0]
xAMW29 = percentilesdf[AMW29].values[0]
xAMW30 = percentilesdf[AMW30].values[0]
xAMW31 = percentilesdf[AMW31].values[0]
xAMW32 = percentilesdf[AMW32].values[0]
xAMW33 = percentilesdf[AMW33].values[0]
xAMW34 = percentilesdf[AMW34].values[0]

xST1 = percentilesdf[ST1].values[0]
xST2 = percentilesdf[ST2].values[0]
xST3 = percentilesdf[ST3].values[0]
xST4 = percentilesdf[ST4].values[0]
xST5 = percentilesdf[ST5].values[0]
xST6 = percentilesdf[ST6].values[0]
xST7 = percentilesdf[ST7].values[0]
xST8 = percentilesdf[ST8].values[0]
xST9 = percentilesdf[ST9].values[0]
xST10 = percentilesdf[ST10].values[0]
xST11 = percentilesdf[ST11].values[0]
xST12 = percentilesdf[ST12].values[0]
xST13 = percentilesdf[ST13].values[0]
xST14 = percentilesdf[ST14].values[0]
xST15 = percentilesdf[ST15].values[0]
xST16 = percentilesdf[ST16].values[0]
xST17 = percentilesdf[ST17].values[0]
xST18 = percentilesdf[ST18].values[0]
xST19 = percentilesdf[ST19].values[0]
xST20 = percentilesdf[ST20].values[0]
xST21 = percentilesdf[ST21].values[0]
xST22 = percentilesdf[ST22].values[0]
xST23 = percentilesdf[ST23].values[0]
xST24 = percentilesdf[ST24].values[0]

###############################################################################################

pct1CB = stats.percentileofscore(dfPercentiles[CB1],xCB1)
pct2CB = stats.percentileofscore(dfPercentiles[CB2],xCB2)
pct3CB = stats.percentileofscore(dfPercentiles[CB3],xCB3)
pct4CB = stats.percentileofscore(dfPercentiles[CB4],xCB4)
pct5CB = stats.percentileofscore(dfPercentiles[CB5],xCB5)
pct6CB = stats.percentileofscore(dfPercentiles[CB6],xCB6)
pct7CB = stats.percentileofscore(dfPercentiles[CB7],xCB7)
pct8CB = stats.percentileofscore(dfPercentiles[CB8],xCB8)
pct9CB = stats.percentileofscore(dfPercentiles[CB9],xCB9)
pct10CB = stats.percentileofscore(dfPercentiles[CB10],xCB10)
pct11CB = stats.percentileofscore(dfPercentiles[CB11],xCB11)
pct12CB = stats.percentileofscore(dfPercentiles[CB12],xCB12)
pct13CB = stats.percentileofscore(dfPercentiles[CB13],xCB13)
pct14CB = stats.percentileofscore(dfPercentiles[CB14],xCB14)
pct15CB = stats.percentileofscore(dfPercentiles[CB15],xCB15)
pct16CB = stats.percentileofscore(dfPercentiles[CB16],xCB16)

pct1FBWB = stats.percentileofscore(dfPercentiles[FBWB1],xFBWB1)
pct2FBWB = stats.percentileofscore(dfPercentiles[FBWB2],xFBWB2)
pct3FBWB = stats.percentileofscore(dfPercentiles[FBWB3],xFBWB3)
pct4FBWB = stats.percentileofscore(dfPercentiles[FBWB4],xFBWB4)
pct5FBWB = stats.percentileofscore(dfPercentiles[FBWB5],xFBWB5)
pct6FBWB = stats.percentileofscore(dfPercentiles[FBWB6],xFBWB6)
pct7FBWB = stats.percentileofscore(dfPercentiles[FBWB7],xFBWB7)
pct8FBWB = stats.percentileofscore(dfPercentiles[FBWB8],xFBWB8)
pct9FBWB = stats.percentileofscore(dfPercentiles[FBWB9],xFBWB9)
pct10FBWB = stats.percentileofscore(dfPercentiles[FBWB10],xFBWB10)
pct11FBWB = stats.percentileofscore(dfPercentiles[FBWB11],xFBWB11)
pct12FBWB = stats.percentileofscore(dfPercentiles[FBWB12],xFBWB12)
pct13FBWB = stats.percentileofscore(dfPercentiles[FBWB13],xFBWB13)
pct14FBWB = stats.percentileofscore(dfPercentiles[FBWB14],xFBWB14)
pct15FBWB = stats.percentileofscore(dfPercentiles[FBWB15],xFBWB15)
pct16FBWB = stats.percentileofscore(dfPercentiles[FBWB16],xFBWB16)
pct17FBWB = stats.percentileofscore(dfPercentiles[FBWB17],xFBWB17)
pct18FBWB = stats.percentileofscore(dfPercentiles[FBWB18],xFBWB18)
pct19FBWB = stats.percentileofscore(dfPercentiles[FBWB19],xFBWB19)
pct20FBWB = stats.percentileofscore(dfPercentiles[FBWB20],xFBWB20)
pct21FBWB = stats.percentileofscore(dfPercentiles[FBWB21],xFBWB21)
pct22FBWB = stats.percentileofscore(dfPercentiles[FBWB22],xFBWB22)
pct23FBWB = stats.percentileofscore(dfPercentiles[FBWB23],xFBWB23)
pct24FBWB = stats.percentileofscore(dfPercentiles[FBWB24],xFBWB24)
pct25FBWB = stats.percentileofscore(dfPercentiles[FBWB25],xFBWB25)
pct26FBWB = stats.percentileofscore(dfPercentiles[FBWB26],xFBWB26)
pct27FBWB = stats.percentileofscore(dfPercentiles[FBWB27],xFBWB27)

pct1MID = stats.percentileofscore(dfPercentiles[MID1],xMID1)
pct2MID = stats.percentileofscore(dfPercentiles[MID2],xMID2)
pct3MID = stats.percentileofscore(dfPercentiles[MID3],xMID3)
pct4MID = stats.percentileofscore(dfPercentiles[MID4],xMID4)
pct5MID = stats.percentileofscore(dfPercentiles[MID5],xMID5)
pct6MID = stats.percentileofscore(dfPercentiles[MID6],xMID6)
pct7MID = stats.percentileofscore(dfPercentiles[MID7],xMID7)
pct8MID = stats.percentileofscore(dfPercentiles[MID8],xMID8)
pct9MID = stats.percentileofscore(dfPercentiles[MID9],xMID9)
pct10MID = stats.percentileofscore(dfPercentiles[MID10],xMID10)
pct11MID = stats.percentileofscore(dfPercentiles[MID11],xMID11)
pct12MID = stats.percentileofscore(dfPercentiles[MID12],xMID12)
pct13MID = stats.percentileofscore(dfPercentiles[MID13],xMID13)
pct14MID = stats.percentileofscore(dfPercentiles[MID14],xMID14)
pct15MID = stats.percentileofscore(dfPercentiles[MID15],xMID15)
pct16MID = stats.percentileofscore(dfPercentiles[MID16],xMID16)
pct17MID = stats.percentileofscore(dfPercentiles[MID17],xMID17)
pct18MID = stats.percentileofscore(dfPercentiles[MID18],xMID18)
pct19MID = stats.percentileofscore(dfPercentiles[MID19],xMID19)
pct20MID = stats.percentileofscore(dfPercentiles[MID20],xMID20)
pct21MID = stats.percentileofscore(dfPercentiles[MID21],xMID21)
pct22MID = stats.percentileofscore(dfPercentiles[MID22],xMID22)
pct23MID = stats.percentileofscore(dfPercentiles[MID23],xMID23)
pct24MID = stats.percentileofscore(dfPercentiles[MID24],xMID24)
pct25MID = stats.percentileofscore(dfPercentiles[MID25],xMID25)
pct26MID = stats.percentileofscore(dfPercentiles[MID26],xMID26)
pct27MID = stats.percentileofscore(dfPercentiles[MID27],xMID27)
pct28MID = stats.percentileofscore(dfPercentiles[MID28],xMID28)

pct1AMW = stats.percentileofscore(dfPercentiles[AMW1],xAMW1)
pct2AMW = stats.percentileofscore(dfPercentiles[AMW2],xAMW2)
pct3AMW = stats.percentileofscore(dfPercentiles[AMW3],xAMW3)
pct4AMW = stats.percentileofscore(dfPercentiles[AMW4],xAMW4)
pct5AMW = stats.percentileofscore(dfPercentiles[AMW5],xAMW5)
pct6AMW = stats.percentileofscore(dfPercentiles[AMW6],xAMW6)
pct7AMW = stats.percentileofscore(dfPercentiles[AMW7],xAMW7)
pct8AMW = stats.percentileofscore(dfPercentiles[AMW8],xAMW8)
pct9AMW = stats.percentileofscore(dfPercentiles[AMW9],xAMW9)
pct10AMW = stats.percentileofscore(dfPercentiles[AMW10],xAMW10)
pct11AMW = stats.percentileofscore(dfPercentiles[AMW11],xAMW11)
pct12AMW = stats.percentileofscore(dfPercentiles[AMW12],xAMW12)
pct13AMW = stats.percentileofscore(dfPercentiles[AMW13],xAMW13)
pct14AMW = stats.percentileofscore(dfPercentiles[AMW14],xAMW14)
pct15AMW = stats.percentileofscore(dfPercentiles[AMW15],xAMW15)
pct16AMW = stats.percentileofscore(dfPercentiles[AMW16],xAMW16)
pct17AMW = stats.percentileofscore(dfPercentiles[AMW17],xAMW17)
pct18AMW = stats.percentileofscore(dfPercentiles[AMW18],xAMW18)
pct19AMW = stats.percentileofscore(dfPercentiles[AMW19],xAMW19)
pct20AMW = stats.percentileofscore(dfPercentiles[AMW20],xAMW20)
pct21AMW = stats.percentileofscore(dfPercentiles[AMW21],xAMW21)
pct22AMW = stats.percentileofscore(dfPercentiles[AMW22],xAMW22)
pct23AMW = stats.percentileofscore(dfPercentiles[AMW23],xAMW23)
pct24AMW = stats.percentileofscore(dfPercentiles[AMW24],xAMW24)
pct25AMW = stats.percentileofscore(dfPercentiles[AMW25],xAMW25)
pct26AMW = stats.percentileofscore(dfPercentiles[AMW26],xAMW26)
pct27AMW = stats.percentileofscore(dfPercentiles[AMW27],xAMW27)
pct28AMW = stats.percentileofscore(dfPercentiles[AMW28],xAMW28)
pct29AMW = stats.percentileofscore(dfPercentiles[AMW29],xAMW29)
pct30AMW = stats.percentileofscore(dfPercentiles[AMW30],xAMW30)
pct31AMW = stats.percentileofscore(dfPercentiles[AMW31],xAMW31)
pct32AMW = stats.percentileofscore(dfPercentiles[AMW32],xAMW32)
pct33AMW = stats.percentileofscore(dfPercentiles[AMW33],xAMW33)
pct34AMW = stats.percentileofscore(dfPercentiles[AMW34],xAMW34)

pct1ST = stats.percentileofscore(dfPercentiles[ST1],xST1)
pct2ST = stats.percentileofscore(dfPercentiles[ST2],xST2)
pct3ST = stats.percentileofscore(dfPercentiles[ST3],xST3)
pct4ST = stats.percentileofscore(dfPercentiles[ST4],xST4)
pct5ST = stats.percentileofscore(dfPercentiles[ST5],xST5)
pct6ST = stats.percentileofscore(dfPercentiles[ST6],xST6)
pct7ST = stats.percentileofscore(dfPercentiles[ST7],xST7)
pct8ST = stats.percentileofscore(dfPercentiles[ST8],xST8)
pct9ST = stats.percentileofscore(dfPercentiles[ST9],xST9)
pct10ST = stats.percentileofscore(dfPercentiles[ST10],xST10)
pct11ST = stats.percentileofscore(dfPercentiles[ST11],xST11)
pct12ST = stats.percentileofscore(dfPercentiles[ST12],xST12)
pct13ST = stats.percentileofscore(dfPercentiles[ST13],xST13)
pct14ST = stats.percentileofscore(dfPercentiles[ST14],xST14)
pct15ST = stats.percentileofscore(dfPercentiles[ST15],xST15)
pct16ST = stats.percentileofscore(dfPercentiles[ST16],xST16)
pct17ST = stats.percentileofscore(dfPercentiles[ST17],xST17)
pct18ST = stats.percentileofscore(dfPercentiles[ST18],xST18)
pct19ST = stats.percentileofscore(dfPercentiles[ST19],xST19)
pct20ST = stats.percentileofscore(dfPercentiles[ST20],xST20)
pct21ST = stats.percentileofscore(dfPercentiles[ST21],xST21)
pct22ST = stats.percentileofscore(dfPercentiles[ST22],xST22)
pct23ST = stats.percentileofscore(dfPercentiles[ST23],xST23)
pct24ST = stats.percentileofscore(dfPercentiles[ST24],xST24)

###############################################################################################

#Centre Back Template      
if template == 'Centre Back':
        bar_df = pd.DataFrame ({'Metric': [CB1,CB2,CB3,CB4,CB5,CB6,CB7,CB8,CB9,CB10,CB11,CB12,CB13,CB14,CB15,CB16],
                                'Percentile': [pct1CB,pct2CB,pct3CB,pct4CB,pct5CB,pct6CB,pct7CB,pct8CB,pct9CB,pct10CB,pct11CB,pct12CB,pct13CB,pct14CB,pct15CB,pct16CB],
                                'Value': [xCB1,xCB2,xCB3,xCB4,xCB5,xCB6,xCB7,xCB8,xCB9,xCB10,xCB11,xCB12,xCB13,xCB14,xCB15,xCB16]})

#Fullback & Wingback Template        
if template == 'Fullback & Wingback':
        bar_df = pd.DataFrame ({'Metric': [FBWB1,FBWB2,FBWB3,FBWB4,FBWB5,FBWB6,FBWB7,FBWB8,FBWB9,FBWB10,FBWB11,FBWB12,FBWB13,FBWB14,FBWB15,FBWB16,FBWB17,FBWB18,FBWB19,FBWB20,FBWB21,FBWB22,FBWB23,FBWB24,FBWB25,FBWB26,FBWB27],
                                'Percentile': [pct1FBWB,pct2FBWB,pct3FBWB,pct4FBWB,pct5FBWB,pct6FBWB,pct7FBWB,pct8FBWB,pct9FBWB,pct10FBWB,pct11FBWB,pct12FBWB,pct13FBWB,pct14FBWB,pct15FBWB,pct16FBWB,pct17FBWB,pct18FBWB,pct19FBWB,pct20FBWB,pct21FBWB,pct22FBWB,pct23FBWB,pct24FBWB,pct25FBWB,pct26FBWB,pct27FBWB],
                                'Value': [xFBWB1,xFBWB2,xFBWB3,xFBWB4,xFBWB5,xFBWB6,xFBWB7,xFBWB8,xFBWB9,xFBWB10,xFBWB11,xFBWB12,xFBWB13,xFBWB14,xFBWB15,xFBWB16,xFBWB17,xFBWB18,xFBWB19,xFBWB20,xFBWB21,xFBWB22,xFBWB23,xFBWB24,xFBWB25,xFBWB26,xFBWB27]})
        
#Midfielder Template        
if template == 'Midfielder':
        bar_df = pd.DataFrame ({'Metric': [MID1,MID2,MID3,MID4,MID5,MID6,MID7,MID8,MID9,MID10,MID11,MID12,MID13,MID14,MID15,MID16,MID17,MID18,MID19,MID20,MID21,MID22,MID23,MID24,MID25,MID26,MID27,MID28],
                                'Percentile': [pct1MID,pct2MID,pct3MID,pct4MID,pct5MID,pct6MID,pct7MID,pct8MID,pct9MID,pct10MID,pct11MID,pct12MID,pct13MID,pct14MID,pct15MID,pct16MID,pct17MID,pct18MID,pct19MID,pct20MID,pct21MID,pct22MID,pct23MID,pct24MID,pct25MID,pct26MID,pct27MID,pct28MID],
                                'Value': [xMID1,xMID2,xMID3,xMID4,xMID5,xMID6,xMID7,xMID8,xMID9,xMID10,xMID11,xMID12,xMID13,xMID14,xMID15,xMID16,xMID17,xMID18,xMID19,xMID20,xMID21,xMID22,xMID23,xMID24,xMID25,xMID26,xMID27,xMID28]})
#Attacking Midfielder & Winger Template        
if template == 'Attacking Midfielder & Winger':
        bar_df = pd.DataFrame ({'Metric': [AMW1,AMW2,AMW3,AMW4,AMW5,AMW6,AMW7,AMW8,AMW9,AMW10,AMW11,AMW12,AMW13,AMW14,AMW15,AMW16,AMW17,AMW18,AMW19,AMW20,AMW21,AMW22,AMW23,AMW24,AMW25,AMW26,AMW27,AMW28,AMW29,AMW30,AMW31,AMW32,AMW33,AMW34],
                                'Percentile': [pct1AMW,pct2AMW,pct3AMW,pct4AMW,pct5AMW,pct6AMW,pct7AMW,pct8AMW,pct9AMW,pct10AMW,pct11AMW,pct12AMW,pct13AMW,pct14AMW,pct15AMW,pct16AMW,pct17AMW,pct18AMW,pct19AMW,pct20AMW,pct21AMW,pct22AMW,pct23AMW,pct24AMW,pct25AMW,pct26AMW,pct27AMW,pct28AMW,pct29AMW,pct30AMW,pct31AMW,pct32AMW,pct33AMW,pct34AMW],
                                'Value': [xAMW1,xAMW2,xAMW3,xAMW4,xAMW5,xAMW6,xAMW7,xAMW8,xAMW9,xAMW10,xAMW11,xAMW12,xAMW13,xAMW14,xAMW15,xAMW16,xAMW17,xAMW18,xAMW19,xAMW20,xAMW21,xAMW22,xAMW23,xAMW24,xAMW25,xAMW6,xAMW27,xAMW28,xAMW29,xAMW30,xAMW31,xAMW32,xAMW33,xAMW34]})

#Striker Template        
if template == 'Striker':
        bar_df = pd.DataFrame ({'Metric': [ST1,ST2,ST3,ST4,ST5,ST6,ST7,ST8,ST9,ST10,ST11,ST12,ST13,ST14,ST15,ST16,ST17,ST18,ST19,ST20,ST21,ST22,ST23,ST24],
                                'Percentile': [pct1ST,pct2ST,pct3ST,pct4ST,pct5ST,pct6ST,pct7ST,pct8ST,pct9ST,pct10ST,pct11ST,pct12ST,pct13ST,pct14ST,pct15ST,pct16ST,pct17ST,pct18ST,pct19ST,pct20ST,pct21ST,pct22ST,pct23ST,pct24ST],
                                'Value': [xST1,xST2,xST3,xST4,xST5,xST6,xST7,xST8,xST9,xST10,xST11,xST12,xST13,xST14,xST15,xST16,xST17,xST18,xST19,xST20,xST21,xST22,xST23,xST24]})

#Striker Template        
if template == 'Striker & Wide Forward':
        bar_df = pd.DataFrame ({'Metric': [ST1,ST2,ST3,ST4,ST5,ST6,ST7,ST8,ST9,ST10,ST11,ST12,ST13,ST14,ST15,ST16,ST17,ST18,ST19,ST20,ST21,ST22,ST23,ST24],
                                'Percentile': [pct1ST,pct2ST,pct3ST,pct4ST,pct5ST,pct6ST,pct7ST,pct8ST,pct9ST,pct10ST,pct11ST,pct12ST,pct13ST,pct14ST,pct15ST,pct16ST,pct17ST,pct18ST,pct19ST,pct20ST,pct21ST,pct22ST,pct23ST,pct24ST],
                                'Value': [xST1,xST2,xST3,xST4,xST5,xST6,xST7,xST8,xST9,xST10,xST11,xST12,xST13,xST14,xST15,xST16,xST17,xST18,xST19,xST20,xST21,xST22,xST23,xST24]})

#PLOT        
        
col = []
for val in bar_df.Percentile:
    if val < 20:
        col.append('#CF1C1A')#red
    elif val <= 40:
        col.append('#DB7A7A')#FFA93B
    elif val >=80:
        col.append('#2A7FC0')#green
    elif val <=60:
        col.append('#EAEDE0')#plain close to background
    else:
        col.append('#94D3EC')#E9CE4C


# NOW PLOTTING THE barh
fig, ax = plt.subplots()
fig.patch.set_facecolor(background)
ax.set_facecolor(background)
fig.set_size_inches(9,13.35)
ax.barh(y='Metric', width=bar_df.Percentile, data=bar_df,
        color=col, ec='black', lw=.5, alpha=.8)
#Reverse axis to 
ax.invert_yaxis()


ax.set(ylabel=None)
plt.xlim([0, 100])
ax.set_xlabel("Percentile Rank",fontsize=12)


for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(12)


for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(12)
    
for i in range(len(bar_df)):
    if bar_df['Percentile'][i]<20:
        ax.annotate('%.2f' %bar_df['Value'][i], xy=(bar_df['Percentile'][i]+1, i), ha='left', va='center', color='black', fontsize='12',fontweight='bold', zorder=10)
    else:
        ax.annotate('%.2f' %bar_df['Value'][i], xy=(bar_df['Percentile'][i]-1, i), ha='right', va='center', color='black', fontsize='12',fontweight='bold', zorder=10)


spines = ["top","right","bottom","left"]
for s in spines:
    if s in ["top","right"]:
        ax.spines[s].set_visible(False)

plt.axvline(50,linestyle='dashed',c='black',lw=2,zorder=1, alpha=0.4)

#"IF" statements for the various lines seperating the visual for each template

if template == 'Centre Back':
    plt.axhline(4.51,linestyle='-',c='black',lw=2,zorder=1)
    plt.axhline(8.51,linestyle='-',c='black',lw=2,zorder=1)
    fig_text(0.91,0.81,"ATTACKING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.61,"POSSESSION", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.36,"DEFENDING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)


if template == 'Fullback & Wingback':
    plt.axhline(10.52,linestyle='-',c='black',lw=2,zorder=1)
    plt.axhline(19.52,linestyle='-',c='black',lw=2,zorder=1)
    fig_text(0.91,0.78,"ATTACKING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.525,"POSSESSION", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.295,"DEFENDING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)

if template == 'Midfielder':
    plt.axhline(8.532,linestyle='-',c='black',lw=2,zorder=1)
    plt.axhline(20.52,linestyle='-',c='black',lw=2,zorder=1)
    fig_text(0.91,0.81,"ATTACKING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.55,"POSSESSION", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.3,"DEFENDING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
       
if template == 'Attacking Midfielder & Winger':
    plt.axhline(13.532,linestyle='-',c='black',lw=2,zorder=1)
    plt.axhline(26.52,linestyle='-',c='black',lw=2,zorder=1)
    fig_text(0.91,0.77,"ATTACKING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.5,"POSSESSION", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.275,"DEFENDING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
      
if template == 'Striker':
    plt.axhline(11.532,linestyle='-',c='black',lw=2,zorder=1)
    plt.axhline(17.518,linestyle='-',c='black',lw=2,zorder=1)
    fig_text(0.91,0.73,"ATTACKING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.48,"POSSESSION", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.29,"DEFENDING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)

if template == 'Striker & Wide Forward':
    plt.axhline(11.532,linestyle='-',c='black',lw=2,zorder=1)
    plt.axhline(17.518,linestyle='-',c='black',lw=2,zorder=1)
    fig_text(0.91,0.73,"ATTACKING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.48,"POSSESSION", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)
    fig_text(0.91,0.29,"DEFENDING", fontweight='bold',size=16, color="black", alpha=0.5, zorder=2, rotation=270.)

    
fig_text(-0.16,0.96,"%s (%i) - %s" %(player, page, team),  fontweight='bold',size=36)
fig_text(-0.16,0.92,"%i minutes played\n%s | %s %s | %s template" %(minplay, team, league, ssn_, template), fontweight='bold',size=16)
fig_text(0.432,0.865,"Average "  + league +  " " + template, fontweight='bold',size=11, fontstyle='italic', color="black", alpha=0.7, zorder=2)



# add credits
CREDIT_1 = "Graphic: Liam Henshaw on behalf of Heart of Midlothian FC"
CREDIT_2 = "Notes: All data is per 90 mins | Data is via Wyscout | Data only includes players who have played %i" %(mins)
CREDIT_3 = "How to read: Bar length shows the percentile rank | Bold number is the raw data value for that metric"

fig.text(
    -0.16, 0.000, f"{CREDIT_1}\n{CREDIT_2}\n{CREDIT_3}", size=11,
    color="#545454", fontstyle='italic',
    ha="left"
)

im2 = imageio.imread('HeartsLogo.png')

# add image
ax_image = add_image(
    im2, fig, left=0.83, bottom=-0.02, width=0.11, height=0.092
)   # these values might differ when you are plotting

#Below are the final visuals
disp2_col.pyplot(fig)
#######################################################################################################################
with st.expander('Latest Data Updates'):
    st.write('''
    England Premier League 2022-23 - Last Updated 25/05/2023\n
    England Championship 2022-23 - Completed season\n
    England National League North & South 2022-23 - Completed season\n
    Argentina Primera Division 2022 - Completed season\n
    Argentina Primera Division 2023 - Last Updated 25/05/2023\n
    Albania Superiore League 2022-23 - Last Updated 25/05/2023\n
    Austria Bundesliga 2022-23 - Last Updated 25/05/2023\n
    Austria Bundesliga 2021-22 - Completed season\n
    Belarus Premier League 2022 - Completed season\n
    Belgium First Division B 2022-23 - Last Updated 25/05/2023\n
    Brazil Serie A 2022 - Completed season\n
    Brazil Serie B 2022 - Completed season\n
    Bulgaria First League 2022-23 - Last Updated 25/05/2023\n
    Chile Primera Division 2022 - Completed season\n
    Chile Primera Division 2023 - Last Updated 25/05/2023\n
    China Super League 2022 - Completed season\n
    Colombia Primera A 2022 - Completed season\n
    Colombia Primera A 2023 - Last Updated 25/05/2023\n
    Costa Rica Primera Divisioon 2022-23 - Last Updated 25/05/2023\n
    Cyprus First Division 2022-23 - Last Updated 25/05/2023\n
    Czech Fortuna Liga 2022-23 - Last Updated 25/05/2023\n
    Ecuador Serie A 2022 - Completed season\n
    Egypt Premier League 2022-23 - Last Updated 25/05/2023\n
    Estonia Meistriliiga 2022 - Completed season\n
    Finland Veikkausliiga 2022 - Completed season\n
    Finland Ykkönen 2022 - Completed season\n
    Georgia Erovnuli Liga 2022 - Completed season\n
    Germany 2. Bundesliga 2022-23 - Last Updated 25/05/2023\n
    Greece Super League 2022-23 - Last Updated 25/05/2023\n
    Hungary NB1 2022-23 - Last Updated 25/05/2023\n
    Indonesia Liga 1 2022-23 - Last Updated 25/05/2023\n
    Italy Campionato Primavera 1 2022-23 - Last Updated 25/05/2023\n
    Italy Serie B 2022-23 - Last Updated 25/05/2023\n
    Japan J2 2023 - Last Updated 25/05/2023\n
    Japan J2 2022 - Completed season\n
    Korea K League 2022 - Completed season\n
    Latvia Virsliga 2022 - Completed season\n
    Malaysia Super League 2022 - Completed season\n
    Mexico Liga MX 2022-23 - Last Updated 25/05/2023\n
    Morocco Botola Pro 2022-23 - Last Updated 25/05/2023\n
    Netherlands Eredivisie 2022-23 - Last Updated 25/05/2023\n
    Netherlands Eerste Divisie 2022-23 - Last Updated 25/05/2023\n
    Northern Ireland Premiership 2022-23 - Last Updated 25/05/2023\n
    Peru Primera Division 2022 - Completed season\n
    Portugal Primeira Liga 2022-23 - Last Updated 25/05/2023\n
    Portugal Segunda Liga 2022-23 - Last Updated 25/05/2023\n
    Romania SuperLiga 2022-23 - Last Updated 25/05/2023\n
    Scotland Championship 2022-23 - Completed season\n
    Slovenia Prva Liga 2022-23 - Last Updated 25/05/2023\n
    South Africa PSL 2022-23 - Last Updated 25/05/2023\n
    Spain La Liga 2022-23 - Last Updated 25/05/2023\n
    Spain Primera División RFEF 2022-23 - Last Updated 25/05/2023\n
    Spain Segunda 2022-23 - Last Updated 25/05/2023\n
    Turkey Super Lig 2022-23 - Last Updated 25/05/2023\n
    Ukraine Premier League 2022-23 - Last Updated 25/05/2023\n
    Uruguay Primera Division 2022 - Completed season\n
    Uruguay Primera Division 2023 - Last Updated 25/05/2023\n
    Uzbekistan Super League 2022 - Completed season\n
    Venezuela Primera Division 2022 - Completed season\n
    ''')