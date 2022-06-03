from this import d
from numpy import single, size
import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# IMPLEMENT TEMPLATE OPTIONS, BALOON SOMETHING AND SNOW.

# FUNCTIONS
def formateo(lista):
    newformat=[]
    for elemento in lista: 
        newformat.append(elemento[0])
    return newformat


# Page init config
st.set_page_config(page_title="Pre-betting Analysis",
                    page_icon=":bar_chart:",
                    layout="wide")

# CONNECTION WITH SQL ------------------------------------------------------------------------------
@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()
# --------------------------------------------------------------------------------------------------
# Queries give a list of tuples. Each tuple is a row.

st.title("Soccer Analytics")
st.markdown("Welcome to Soccer analytics. In this webpage, you will find a series of graphs with filtering options that display a certain amount of "
            "data through different types of graphs. The data provided here allows for a deep analysis of the performance of multiple teams, as well as soccer players.\n"
            "In future updates, this webpage will include more data, graphs and filtering options to provide even more room for analytics. Enjoy!")


teamsraw = run_query("SELECT distinct h_team FROM matchesdata") #format this
teamsclean = formateo(teamsraw)

# -------------------------------- STATISTICS FOR ALL TEAMS VISUALIZATION ---------------------------------------

measurepicked="AVG"
longqueryh=f"""
    WITH hometeam(team, Goals, Half_time_goals, Shots_on_goal, Distance, Total_passes, Succesful_Passes, Failed_passes, Pass_ratio, Possession, Tackle_ratio, Fouls, Fouls_received, Offside, Corners) as (
	SELECT h_team, {measurepicked}(h_goals), {measurepicked}(h_ht_goals), {measurepicked}(h_shots_on_goal), {measurepicked}(h_distance), {measurepicked}(h_total_passes),{measurepicked}(h_success_passes), 
		{measurepicked}(h_failed_passes), {measurepicked}(h_pass_ratio), {measurepicked}(h_possession), {measurepicked}(h_tackle_ratio), {measurepicked}(h_fouls), 
        {measurepicked}(h_got_fouled), {measurepicked}(h_offside), {measurepicked}(h_corners)
	FROM matchesdata
    GROUP BY h_team
    )

    SELECT *
    FROM hometeam
    
    """
dfh = pd.read_sql_query(longqueryh,conn)

stats_raw = dfh.columns[1:]
stats_clean = [w.replace('_', ' ') for w in stats_raw] # https://stackoverflow.com/a/3136703

functions_clean=["Average", "Maximum", "Minimum", "Total"]
st.title("General Statistics for Teams")

st.markdown("Here you will find filtered information about thousands of matches performed by <font color=FF5733>Bundesliga</font> teams across multiple seasons and match days.\n"
        "Please make use of the options selector to see the reflected changes on the graph.\n"
        "With these tools, you are able to make over **100** different combinations for analysis!",unsafe_allow_html=True)
row13_1, row13_spacer2, row13_2 = st.columns((5, 1.4, 3.4))
with row13_2:
    st.subheader("Options Selector")
    statpicked = st.selectbox(
        'Pick a stat', 
        options=stats_clean 
    )
    game_typepicked = st.selectbox(
        'Pick a game type',
        options=["Home", "Away"],
    )
    measurepicked = st.selectbox(
        'Select an element of measure',
        options=functions_clean
    )
    chartpicked = st.radio(
        'Pick a chart type',
        options=["Horizontal bar chart","Vertical bar chart"]
    )
with row13_1:
    column_selected = stats_clean.index(statpicked)
    statpicked = stats_raw[column_selected]

    functions_raw=["AVG", "MAX", "MIN", "SUM"]
    aggrfunc_selected = functions_clean.index(measurepicked)
    measurepicked=functions_raw[aggrfunc_selected]

    longquerya=f"""
    WITH ateam(team, Goals, Half_time_goals, Shots_on_goal, Distance, Total_passes, Succesful_Passes, Failed_passes, Pass_ratio, Possession, Tackle_ratio, Fouls, Fouls_received, Offside, Corners) as (
        SELECT a_team, {measurepicked}(a_goals), {measurepicked}(a_ht_goals), {measurepicked}(a_shots_on_goal), {measurepicked}(a_distance), {measurepicked}(a_total_passes),{measurepicked}(a_success_passes), 
            {measurepicked}(a_failed_passes), {measurepicked}(a_pass_ratio), {measurepicked}(a_possession), {measurepicked}(a_tackle_ratio), {measurepicked}(a_fouls), 
            {measurepicked}(a_got_fouled), {measurepicked}(a_offside), {measurepicked}(a_corners)
        FROM matchesdata
        GROUP BY a_team
    )

    SELECT *
    FROM ateam
    """

    longqueryh=f"""
    WITH hometeam(team, Goals, Half_time_goals, Shots_on_goal, Distance, Total_passes, Succesful_Passes, Failed_passes, Pass_ratio, Possession, Tackle_ratio, Fouls, Fouls_received, Offside, Corners) as (
	SELECT h_team, {measurepicked}(h_goals), {measurepicked}(h_ht_goals), {measurepicked}(h_shots_on_goal), {measurepicked}(h_distance), {measurepicked}(h_total_passes),{measurepicked}(h_success_passes), 
		{measurepicked}(h_failed_passes), {measurepicked}(h_pass_ratio), {measurepicked}(h_possession), {measurepicked}(h_tackle_ratio), {measurepicked}(h_fouls), 
        {measurepicked}(h_got_fouled), {measurepicked}(h_offside), {measurepicked}(h_corners)
	FROM matchesdata
    GROUP BY h_team
    )

    SELECT *
    FROM hometeam
    
    """

    dfa=pd.read_sql_query(longquerya,conn)
    dfh = pd.read_sql_query(longqueryh,conn)
    if chartpicked == "Horizontal bar chart":
        if game_typepicked == "Home":
            fig = px.bar(dfh, x=statpicked, y="team", width=900, height=700, template='plotly_dark')
            fig.update_traces(marker_color='#B03A2E')
            st.plotly_chart(fig)
        elif game_typepicked == "Away":
            fig = px.bar(dfa, x=statpicked, y="team", width=900, height=700, template='plotly_dark')
            fig.update_traces(marker_color='#B03A2E')
            st.plotly_chart(fig)
    elif chartpicked == "Vertical bar chart":
        if game_typepicked == "Home":
            fig = px.bar(dfh, y=statpicked, x="team", width=900, height=700, template='plotly_dark')
            fig.update_traces(marker_color='#B03A2E')
            st.plotly_chart(fig)
        elif game_typepicked == "Away":
            fig = px.bar(dfa, y=statpicked, x="team", width=900, height=700, template='plotly_dark')
            fig.update_traces(marker_color='#B03A2E')
            st.plotly_chart(fig)


# ---------------------------------------- INDIVIDUAL TEAM STATS -----------------------------------------
# NECESSARY ADDITIONS:
# ADJUST ORDER SO THAT GRAPH DOESNT LOOK SPIKY
# POSSIBLE ADDITIONS:
# ATTRIBUTE SELECTOR: ADD EDITION OF ATTRIBUTES APPPEARING (MIN 3)
# SEASON SELECTOR
# MATCHDAY SELECTOR

st.title("Individual Statistics for Teams")
row2_1, rowspacer2_1, row2_2 = st.columns((5, 0.6, 3.4))
with row2_2:
    st.subheader("Options Selector")
    gametypepicked = st.selectbox(
        'Pick a game type',
        options=["Home", "Away"],
        key=123
    )
    selectedteam = st.selectbox(
        'Select a team',
        options=teamsclean
    )

# items removed: total, success and failed passes. Distance.
singlecountrystats_queryh = f"""
WITH hometeam(Goals, Half_time_goals, Shots_on_goal, Pass_ratio, Possession, Tackle_ratio, Fouls, Fouls_received, Offside, Corners) as (
	SELECT AVG(h_goals), AVG(h_ht_goals), AVG(h_shots_on_goal), AVG(h_pass_ratio), AVG(h_possession), AVG(h_tackle_ratio), AVG(h_fouls), 
        AVG(h_got_fouled), AVG(h_offside), AVG(h_corners)
	FROM matchesdata
    WHERE h_team='{selectedteam}'
)

SELECT *
FROM hometeam
"""

singlecountrystats_querya = f"""
WITH hometeam(Goals, Half_time_goals, Shots_on_goal, Pass_ratio, Possession, Tackle_ratio, Fouls, Fouls_received, Offside, Corners) as (
	SELECT AVG(a_goals), AVG(a_ht_goals), AVG(a_shots_on_goal), AVG(a_pass_ratio), AVG(a_possession), AVG(a_tackle_ratio), AVG(a_fouls), 
        AVG(a_got_fouled), AVG(a_offside), AVG(a_corners)
	FROM matchesdata
    WHERE a_team='{selectedteam}'
)

SELECT *
FROM hometeam
"""

items_to_delete=['Distance', 'Total passes', 'Succesful Passes', 'Failed passes']
stats_clean_radar = list(stats_clean)
for item in items_to_delete:
    stats_clean_radar.remove(item)

with row2_1:
    if gametypepicked=='Home':
        dfh_radar=pd.read_sql_query(singlecountrystats_queryh,conn)
        fig = px.line_polar(dfh_radar, r=dfh_radar.loc[0], theta=stats_clean_radar, line_close=True, width=820, height=730, template='plotly_dark', color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.update_traces(fill='toself')
        st.plotly_chart(fig)
    elif gametypepicked=='Away':
        dfa_radar=pd.read_sql_query(singlecountrystats_querya,conn)
        fig = px.line_polar(dfa_radar, r=dfa_radar.loc[0], theta=stats_clean_radar, line_close=True, width=820, height=730, template='plotly_dark', color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.update_traces(fill='toself')
        st.plotly_chart(fig)


#https://towardsdatascience.com/creating-interactive-radar-charts-with-python-2856d06535f6

# ----------------------------------- PLAYER INDIVIDUAL STATS ----------------------------------------------------
st.title("General Penalty Statistics for Goalkeepers")
st.markdown("Here, you will find the performance of multiple <font color=28B463>goalkeepers</font> when faced with penalties in soccer, based on a sample of matches. Please make use of the options selector to see the reflected changes on the graphs. ",unsafe_allow_html=True)
# when faced with penalties, these goal keepers se desempeñan the following way...
row3_1, rowspacer3_1, row3_2 = st.columns((5, 2.3, 3.4))
with row3_2:
    st.subheader("Options Selector")
    gkvalues_raw = ['NotConceded', 'Conceded', 'PKsFaced', 'Saves']
    gkvalues_clean = ['Not Conceded', 'Conceded', 'Penalty Kicks Faced', 'Saves']
    selectedvalue = st.selectbox(
            'Select a value',
            options=sorted(gkvalues_clean)
        )
    auxindex = gkvalues_clean.index(selectedvalue)
    selectedvalue = gkvalues_raw[auxindex]

    orderoptions_clean = ['Ascendant value', 'Descendant value', 'Goalkeeper']
    selectedorder = st.selectbox(
            'Order by',
            options=orderoptions_clean
        )

with row3_1:
    if selectedorder == 'Goalkeeper':
        playerinfo_query="""
        SELECT *
        FROM goalkeepers_penalties
        ORDER BY Goalkeeper desc
        """
    elif selectedorder == 'Descendant value':
        playerinfo_query=f"""
        SELECT *
        FROM goalkeepers_penalties
        ORDER BY {selectedvalue} desc
        """
    elif selectedorder == 'Ascendant value':
        playerinfo_query=f"""
        SELECT *
        FROM goalkeepers_penalties
        ORDER BY {selectedvalue} asc
        """
    color_discrete_sequence=px.colors.qualitative.Alphabet
    dfgk = pd.read_sql_query(playerinfo_query,conn)
    if auxindex <= 2:
        fig = px.bar(dfgk, x=selectedvalue, y='Goalkeeper', width=1000, height=1000, template='plotly_dark',color_discrete_sequence=px.colors.qualitative.Dark2)
        
        st.plotly_chart(fig)
    else:
        fig = px.bar(dfgk, x='Goalkeeper', y=selectedvalue, width=1000, height=1000, template='plotly_dark',color_discrete_sequence=px.colors.qualitative.Dark2)
        st.plotly_chart(fig)

st.title("Individual Penalty Statistics for Goalkeepers")
row4_1, rowspacer4_1, row4_2 = st.columns((5, 2.3, 3.4))
with row4_2:
    st.subheader("Options Selector")
    playernames_query="""
    SELECT Goalkeeper
    FROM goalkeepers_penalties
    """
    playernames_raw=run_query(playernames_query)
    playernames_clean=formateo(playernames_raw)
    selectedgk = st.selectbox(
            'Select a goalkeeper',
            options=sorted(playernames_clean)
    )

with row4_1:
    indplayerinfo_query = f"""
    SELECT distinct NotConceded, Conceded, PKsFaced, Saves
    FROM goalkeepers_penalties
    WHERE Goalkeeper='{selectedgk}'
    """

    dfgk_radar=pd.read_sql_query(indplayerinfo_query,conn)
    fig = px.line_polar(dfgk_radar, r=dfgk_radar.loc[0], theta=gkvalues_clean, line_close=True, width=820, height=730, template='plotly_dark',color_discrete_sequence=px.colors.qualitative.Vivid)
    fig.update_traces(fill='toself')
    st.plotly_chart(fig)

# ------------------------------- BETTING SITES ----------------------------------------------------------------------

st.title("Time to bet!")
st.markdown("Now that you've been able to run your eyes through our analytical system, it's time to bet!")
st.markdown("In order to help you, we've brought you some of the most popular, legal webpages in Colombia. Enjoy, and thanks for visiting!")
st.markdown("")
row5_1, rowspacer5_1, row5_2, rowspacer5_2, row5_3 = st.columns((3.4, 0.2, 3.4, 0.2, 3.4))
with row5_1:
    st.markdown("[![Foo](https://pbs.twimg.com/profile_images/839741742706483201/P0fe49HO_400x400.jpg)](https://sports.sportium.com.co/)")
with row5_2:
    st.markdown("[![Foo](https://pbs.twimg.com/profile_images/1481366454842896386/PaN0kQjd_400x400.jpg)](https://betplay.com.co/)")
with row5_3:
    st.markdown("[![Foo](https://pbs.twimg.com/profile_images/1493751760636108803/eZimWuVK_400x400.jpg)](https://www.wplay.co/)")

row6_1, rowspacer6_1, row6_2, rowspacer6_2, row6_3 = st.columns((3.4, 0.2, 3.4, 0.2, 3.4))
with row6_1:
    st.markdown("[![Foo](https://pbs.twimg.com/profile_images/1366315605876432896/wmNZHmwu_400x400.jpg)](https://sports.bwin.co/es/sports)")
with row6_2:
    st.markdown("[![Foo](https://pbs.twimg.com/profile_images/1245303968709971970/Q-NmYnxm_400x400.jpg)](https://www.codere.com.co/)")
with row6_3:
    st.markdown("[![Foo](https://pbs.twimg.com/profile_images/1465304950498594826/FCDFw48u_400x400.jpg)](https://www.luckia.co/)")
