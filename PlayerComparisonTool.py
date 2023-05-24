import streamlit as st
import pandas as pd
from soccerplots.radar_chart import Radar
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
import numpy as np
warnings.filterwarnings('ignore')

header = st.container()

with header:
    st.title("HoM Player Comparison Visualisation Tool")
    st.text("Please use this tool to create your own data visualisation for specific players")
    st.text("Created by Liam Henshaw on behalf of Heart of Midlothian Football Club")

with st.expander('Instructions - Please drop down and read'):
    st.write('''
    1.) Use the filters on the left side of the page to select the leagues for each player, position, minimum minutes played, and maximum age of players in the data set.\n 
    2.) This will determine the sample size of players that you can select from.\n
    3.) To create your visual, confirm the players you want to see by inputting or copy & pasting the player names, teams and ages into the text boxes below.\n
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
    league1 = st.selectbox('Player League One', ('England Premier League', 'England Championship','England National League North South', 'Argentina Primera Division 2022','Argentina Primera Division 2023','Albania Superiore League','Austria Bundesliga','Austria Bundesliga 2021-22','Belarus Premier League 2022','Belgium First Division B', 'Brazil Serie A 2022','Brazil Serie B 2022','Bulgaria First League', 'Chile Primera Division 2022','Chile Primera Division 2023', 'China Super League 2022','Colombia Primera A 2022','Colombia Primera A 2023','Costa Rica Primera Division','Cyprus First Division','Czech Fortuna Liga','Ecuador Serie A 2022','Egypt Premier League','Estonia Meistriliiga 2022', 'Finland Veikkausliiga 2022','Finland Ykkönen 2022', 'Georgia Erovnuli Liga 2022', 'Germany 2. Bundesliga','Greece Super League','Hungary NB1','Indonesia Liga 1','Italy Campionato Primavera 1', 'Italy Serie B', 'Japan J2-League 2022','Japan J2-League 2023', 'Korea K-League 2 2022', 'Latvia Virsliga 2022','Malaysia Super League 2022','Mexico Liga MX','Morocco Botola Pro','Netherlands Eredivisie','Netherlands Eerste Divisie','Northern Ireland Premiership', 'Peru Primera Division 2022','Portugal Primeira Liga','Portugal Segunda Liga','Romania SuperLiga','Scotland Championship','Slovenia Prva Liga','South Africa PSL','Spain La Liga','Spain Primera Division RFEF', 'Spain Segunda','Turkey Super Lig','Ukraine Premier League', 'Uruguay Primera Division 2022','Uruguay Primera Division 2023', 'Uzbekistan Super League 2022', 'Venezuela Primera Division 2022',))
    league2 = st.selectbox('Player League Two', ('England Premier League', 'England Championship','England National League North South', 'Argentina Primera Division 2022','Argentina Primera Division 2023','Albania Superiore League','Austria Bundesliga','Austria Bundesliga 2021-22','Belarus Premier League 2022','Belgium First Division B', 'Brazil Serie A 2022','Brazil Serie B 2022','Bulgaria First League', 'Chile Primera Division 2022','Chile Primera Division 2023', 'China Super League 2022','Colombia Primera A 2022','Colombia Primera A 2023','Costa Rica Primera Division','Cyprus First Division','Czech Fortuna Liga','Ecuador Serie A 2022','Egypt Premier League','Estonia Meistriliiga 2022', 'Finland Veikkausliiga 2022','Finland Ykkönen 2022', 'Georgia Erovnuli Liga 2022', 'Germany 2. Bundesliga','Greece Super League','Hungary NB1','Indonesia Liga 1','Italy Campionato Primavera 1', 'Italy Serie B', 'Japan J2-League 2022','Japan J2-League 2023', 'Korea K-League 2 2022', 'Latvia Virsliga 2022','Malaysia Super League 2022','Mexico Liga MX','Morocco Botola Pro','Netherlands Eredivisie','Netherlands Eerste Divisie','Northern Ireland Premiership', 'Peru Primera Division 2022','Portugal Primeira Liga','Portugal Segunda Liga','Romania SuperLiga','Scotland Championship','Slovenia Prva Liga','South Africa PSL','Spain La Liga','Spain Primera Division RFEF', 'Spain Segunda','Turkey Super Lig','Ukraine Premier League', 'Uruguay Primera Division 2022','Uruguay Primera Division 2023', 'Uzbekistan Super League 2022', 'Venezuela Primera Division 2022',))
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

#Successul dribbles
df['Successful dribbles'] = df['Successful dribbles, %'] /100 * df['Dribbles per 90']
df = df.round({'Successful dribbles': 2})

#Removing any data with no values from Position, Team and Age
df = df.dropna(subset=['Position', 'Team within selected timeframe', 'Age']).reset_index(drop=True)

#Getting the player's main position
df['Main Position'] = ''
for i in range(len(df)):
    df['Main Position'][i] = df['Position'][i].split()[0]

#############################################################################

df = df.dropna(subset=['Main Position']).reset_index(drop=True)

#############################################################################

# Filter data
df = df.loc[(df['League'] == league1 ) | (df['League'] == league2)]
dfPlayers = df[(df['Minutes played']>=mins) & (df['Age']<=maxage)].copy()

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
#Adding League Average
numeric_columns = dfPlayers.select_dtypes(include=np.number).columns
dfPlayers.loc['mean'] = dfPlayers[numeric_columns].mean()
dfPlayers.Player = dfPlayers.Player.fillna('League Average')
dfPlayers = dfPlayers.round(decimals = 2)


dftable = dfPlayers

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
                                "Deep completions per 90": "Deep completions"
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
                                "Deep completions per 90": "Deep completions"
                                 }, inplace=True)     

#############################################################################

#############################################################################
#Preview Table
final = dftable[['Player','Team within selected timeframe','Age','League','Main Position','Minutes played','Birth country', 'Contract expires',]]


final.Age = final.Age.astype(int)
final.sort_values(by=['Age'], inplace=True)
final = final[final['Age']<=maxage].reset_index(drop=True)

with dataset:
	st.write(final)

#############################################################################
#Season - Competition Data Base
complete = ['Colombia Primera A 2022','Colombia Primera A 2023', 'Ecuador Serie A 2022', 'Peru Primera Division 2022', 'Uruguay Primera Division 2022','Uruguay Primera Division 2023', 'Venezuela Primera Division 2022', 'Argentina Primera Division 2022','Argentina Primera Division 2023','Austria Bundesliga 2021-22','Belarus Premier League 2022', 'Brazil Serie A 2022','Brazil Serie A 2023', 'Chile Primera Division 2022','Chile Primera Division 2023', 'China Super League 2022', 'Estonia Meistriliiga 2022', 'Finland Veikkausliiga 2022','Finland Ykkönen 2022', 'Georgia Erovnuli Liga 2022', 'Korea K-League 2 2022', 'Latvia Virsliga 2022', 'Malaysia Super League 2022', 'Uzbekistan Super League 2022', 'Japan J2-League 2022','Japan J2-League 2023']
summer = ['Argentina Primera Division', 'Brazil Serie A', 'Chile Primera Division', 'China Super League','Colombia Primera A','Ecuador Serie A', 'Estonia Meistriliiga', 'Finland Veikkausliiga', 'Georgia Erovnuli Liga', 'Japan J2-League', 'Korea K-League 2','Latvia Virsliga','Malaysia Super League', 'Peru Primera Division', 'Uruguay Primera Division', 'Uzbekistan Super League', 'Venezuela Primera Division']
winter = ['England Premier League', 'England Championship','England National League North South','Albania Superiore League','Austria Bundesliga','Belgium First Division B','Bulgaria First League', 'Costa Rica Primera Division','Cyprus First Division','Czech Fortuna Liga','Egypt Premier League', 'Germany 2. Bundesliga','Greece Super League','Hungary NB1','Indonesia Liga 1','Italy Campionato Primavera 1', 'Italy Serie B','Mexico Liga MX','Morocco Botola Pro', 'Netherlands Eredivisie','Netherlands Eerste Divisie','Northern Ireland Premiership','Portugal Primeira Liga','Portugal Segunda Liga','Romania SuperLiga', 'Scotland Championship','Slovenia Prva Liga','South Africa PSL','Spain La Liga','Spain Primera Division RFEF', 'Spain Segunda','Turkey Super Lig','Ukraine Premier League']
if league1 in summer:
	ssn_1 = ' 2023'
elif league1 in winter:
    ssn_1 = ' 2022-23'
elif league1 in complete:
    ssn_1 = ''

if league2 in summer:
	ssn_2 = ' 2023'
elif league2 in winter:
    ssn_2 = ' 2022-23'
elif league2 in complete:
    ssn_2 = ''
#############################################################################

st.header("Enter the player's name, team and age to create the visuals")
st.text("Feel free to type the information, or copy and paste it from the table above")

selections = st.container()
with selections:
	disp1_col , disp2_col = st.columns(2)

	player1 = disp1_col.text_input("First Player's Name", "")
	team1 = disp1_col.text_input("First Player's Team", "")
	page1 = disp1_col.number_input("First Player's Age", step=1)

	player2 = disp2_col.text_input("Second Player's Name", "")
	team2 = disp2_col.text_input("Second Player's Team", "")
	page2 = disp2_col.number_input("Second Player's Age", step=1)

#############################################################################
#Setting df to plot
dfRadar = dfPlayers[(dfPlayers['Player']==player1) | (dfPlayers['Player']==player2)].reset_index(drop=True)

#Player's individual dataframes to get minutes played for each player
dfplayerone = dfRadar[(dfRadar['Player']==player1)]
dfplayertwo = dfRadar[(dfRadar['Player']==player2)]
#Get the mins played value for specific player needed for visual
minplay1 = int(dfplayerone['Minutes played'].values[0])
minplay2 = int(dfplayertwo['Minutes played'].values[0])

#Dropping minutes played column in radar df as it is not needed after getting the player values
dfRadar = dfRadar.drop('Minutes played', axis=1)

#Copy of radar df to display at the end as a table
comparison = dfRadar

#Dropping age and minutes played from df
dfPlayers = dfPlayers.drop('Age', axis=1)
dfPlayers = dfPlayers.drop('Minutes played', axis=1)

#Removing the 
dfPlayers = dfPlayers.quantile([0.05, 0.95])

params = list(dfPlayers.columns)

ranges = []
a_values = []
b_values = []

for x in params:
    a = min(dfPlayers[params][x])
    
    b = max(dfPlayers[params][x])
    
    ranges.append((a,b))
    
for x in range(len(dfRadar['Player'])):
    if dfRadar['Player'][x] == player1:
        a_values = dfRadar.iloc[x].values.tolist()
    if dfRadar['Player'][x] == player2:
        b_values = dfRadar.iloc[x].values.tolist()
        
a_values = a_values[3:]
b_values = b_values[3:]

values = [a_values,b_values]

#title 

title = dict(
    title_name=player1 + " (%i)\n" %(page1),
    title_color = '#dc2228',
    subtitle_name = team1 + "\n%s, %s\n%i minutes played" %(league1, ssn_1, minplay1),
    subtitle_color = 'black',
    title_name_2=player2 + " (%i)\n" %(page2),
    title_color_2 = '#3271ab',
    subtitle_name_2 = team2 + "\n%s, %s\n%i minutes played" %(league2, ssn_2, minplay2),
    subtitle_color_2 = 'black',
    title_fontsize = 24,
    subtitle_fontsize=16
)

## endnote 
endnote = "Graphic: Liam Henshaw on behalf of Heart of Midlothian FC\n Template: %s\n Notes: %i+ mins | All units are per 90mins | Data is via Wyscout" %(template, mins)

## make a subplot
fig, ax = plt.subplots(figsize=(14,18), facecolor="white")

radar = Radar(background_color="white", patch_color="#F0F0F0", label_color="black",
              range_color="black", label_fontsize=12, range_fontsize=6.5)

fig, ax = radar.plot_radar(ranges=ranges,params=params,values=values, 
                         radar_color=['#dc2228','#3271ab'],
                         alphas=[.7,.6],figax=(fig,ax), endnote=endnote, end_size=11.3, end_color="#545454", title=title,
                         compare=True)

im2 = imageio.imread('HeartsLogo.png')

# add image
ax_image = add_image(
    im2, fig, left=0.124, bottom=0.12, width=0.11, height=0.107
)   # these values might differ when you are plotting

plt.show()
st.pyplot(fig)

##########################################################################################################
#Table view comparison for player values
tabview = st.container()
with tabview:
	st.write(comparison)

######################################################################################################################
#Expander to see when the latest leagues were updated last
with st.expander('Latest Data Updates'):
    st.write('''
    England Premier League - Updated 09/06/2023\n
    England Championship 2022/23 -  Completed Season\n
    England National League North & South - Completed Season\n
    Argentina Primera Division - 2022 Completed Season\n
    Argentina Primera Division 2023 - Updated 209/06/2023\n
    Albania Superiore League - Updated 09/06/2023\n
    Austria Bundesliga - Updated 09/05/2023\n
    Austria Bundesliga 2021/22 - Completed Season\n
    Belarus Premier League 2022 - Completed Season\n
    Belgium First Division B - Updated 09/54/2023\n
    Brazil Serie A - 2022 Completed Season\n
    Brazil Serie B - 2022 Completed Season\n
    Bulgaria First League - Updated 09/05/2023\n
    Chile Primera Division - 2022 Completed Season\n
    Chile Primera Division 2023 -  Updated 09/06/2023\n
    China Super League - 2022 Completed Season\n
    Colombia Primera A - 2022 Completed Season \n
    Colombia Primera A 2023 - Updated 15/06/2023\n
    Costa Rica Primera Divisioon - Updated 09/05/2023\n
    Cyprus First Division - Updated 09/05/2023\n
    Czech Fortuna Liga - Updated 09/05/2023\n
    Ecuador Serie A - 2022 Completed Season \n
    Egypt Premier League - Updated 09/05/2023\n
    Estonia Meistriliiga - 2022 Completed Season\n
    Finland Veikkausliiga - 2022 Completed Season\n
    Finland Ykkönen - 2022 Completed Season\n
    Georgia Erovnuli Liga - 2022 Completed Season\n
    Germany 2. Bundesliga - Updated 09/05/2023\n
    Greece Super League - Updated 09/05/2023\n
    Hungary NB1 - Updated 09/05/2023\n
    Indonesia Liga 1 - Updated 09/05/2023\n
    Italy Campionato Primavera 1 - Updated 09/05/2023\n
    Italy Serie B - Updated 09/05/2023\n
    Japan J2-League - 2022 Completed Season\n
    Japan J2-League 2023 - Updated 09/05/2023\n
    Korea K-League 2 - 2022 Completed Season\n
    Latvia Virsliga - 2022 Completed Season\n
    Malaysia Super League - 2022 Completed Season\n
    Mexico Liga MX - Updated 09/05/2023\n
    Morocco Botola Pro - Updated 09/05/2023\n
    Netherlands Eredivisie - Updated 09/05/2023\n
    Netherlands Eerste Divisie - Updated 09/05/2023\n
    Northern Ireland Premiership - Updated 09/05/2023\n
    Peru Primera Division - 2022 Completed Season\n
    Portugal Primeira Liga - Updated 09/05/2023\n
    Portugal Segunda Liga - Updated 09/05/2023\n
    Romania SuperLiga - Updated 09/05/2023\n
    Scotland Championship - Updated 09/05/2023\n
    Slovenia Prva Liga - Updated 09/05/2023\n
    South Africa PSL - Updated 09/05/2023\n
    Spain La Liga - Updated 09/05/2023\n
    Spain Primera División RFEF - Updated 09/05/2023\n
    Spain Segunda - Updated 09/05/2023\n
    Turkey Super Lig - Updated 09/05/2023\n
    Ukraine Premier League - Updated 09/05/2023\n
    Uruguay Primera Division - 2022 Completed Season\n
    Uruguay Primera Division 2023 -  Updated 09/05/2023\n
    Uzbekistan Super League - 2022 Completed Season\n
    Venezuela Primera Divisi0n - 2022 Completed Season\n
    ''')