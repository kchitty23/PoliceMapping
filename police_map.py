
#libraries used to make project possible
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random
import matplotlib.pyplot as plt

#main function that runs for duration of program
def main():
    #import and clean the data
    df = pd.read_csv("full_police_data.csv")
    df = clean_data(df)
    
    #create an initial session state for the individual map dataframe with specific pinpoints
    if "rn" not in st.session_state:
        st.session_state["rn"] = randomize(df)
    
    #write initial text
    write_headers()
    
    #write individual map text
    st.header("Individual Map")
    st.write("Below, you can find a map of the United States with pinpoints where incidents of police killings have "
            + "occurred. You can filter the incidents based on the year, gender, victim's race, officer(s)' race(s), "
            + "the cause of death, and the weapon the victim possessed, if any. Hit randomize after selecting filters "
            + "to update the map. You can read additional details about each incident by clicking on the associated "
             + "pinpoint.")
    
    #create filters, update session state with new dataframe for individual map, otherwise would revert to original
    #if not using session state - found this in Streamlit documentation
    ind_fils = ind_filters(df)
    if st.button("Randomize"):
        st.session_state["rn"] = randomize(df,ind_fils)
        
    #create map
    ind_map(st.session_state.rn)
    
    #write state map text, create filters, create map
    st.header("State Map")
    st.write("Below, you can find a map with death counts from police brutality by each state. You can filter the "
            + "incidents based on the year, gender, victim's race, officer(s)' race(s), the cause of death, and the " 
            + "weapon the victim possessed, if any. Hover over a state to see its count.")
    
    st_fils = state_filters(df)
    state_map(df,st_fils)
    
    #graphs and analysis of data
    st.header("Data Visualization")
    show_graphs(df)
    
    #display resources, places to donate for user
    write_resources()
    
#clean dataframe to use
def clean_data(df):
    #clean and rename columns
    df.rename({"long":"lon"},axis=1,inplace=True)
    df[["officer_races","circumstances"]] = df[["officer_races","circumstances"]].fillna("Unknown")
    
    df["race"] = df["race"].replace(["Unknown race"], "Unknown")
    df["race"] = df["race"].replace(["Native Hawaiian and Pacific Islander"], "Pacific Islander")
    
    #make date column in datetime objects
    df["date_dt"] = pd.to_datetime(df["date"])
    df["year"] = df["date_dt"].dt.strftime("%Y")
    
    #make state column have full state name, rather than abbreviations, this is to later use to connect dataset to
    #geojson to display state map, uses dictionary mapping to work
    state_dict = states = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'American Samoa','AZ': 'Arizona',
        'CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'District of Columbia','DE': 'Delaware',
        'FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois',
        'IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland',
        'ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'Northern Mariana Islands',
        'MS': 'Mississippi','MT': 'Montana','NA': 'National','NC': 'North Carolina','ND': 'North Dakota',
        'NE': 'Nebraska','NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NV': 'Nevada','NY': 'New York',
        'OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'Puerto Rico','RI': 'Rhode Island',
        'SC': 'South Carolina','SD': 'South Dakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia',
        'VI': 'Virgin Islands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'West Virginia',
        'WY': 'Wyoming'}

    state_final = {}
    for state in df["state"].unique():
        if state in state_dict:
            state_final[state] = state_dict[state]

    df["state"] = df["state"].map(state_final)
    
    #edit officer_races column, return df
    df["officer_races"] = df["officer_races"].str.title()
    return df

#write introduction headers
def write_headers():
    st.title("Mapping Police Killings 2013-2022")
    
    st.header("Introduction")
    st.write("Police brutality is a large issue in America. On average, each year, police officers kill 1116 people. "
             + "While information about a select few incidents is circulated in mainstream media, the majority of "
             + "killings go unreported, the victims' names forgotten. This site aims to draw people's attention to "
             + "the magnitude of police brutality. Below, you will find interactive maps that illustrate the issue "
             + "at an individual level, on a case-by-case basis, as well as at a state level with total case counts. "
             + "We can't sit by and simply let police brutality take the lives of innocent Americans. Change needs " 
             + "to occur now.")
             
    st.write("All data taken from https://mappingpoliceviolence.org/. The dataset contains information from the past "
            + "ten years, with a total of 11,168 recorded incidents.")
    
#write final section that has resources, donation links
def write_resources():
    st.header("Resources")
    st.write("To learn more about police brutality, visit the following websites:")
    st.markdown("""
    - https://www.amnesty.org/en/what-we-do/police-brutality/
    - https://www.nature.com/articles/d41586-020-01846-z
    - https://www.nytimes.com/topic/subject/police-brutality-misconduct-and-shootings
    """)
    
    st.write("You can donate to fight police abuse at:")
    st.markdown("""
    - https://www.aclu.org/other/fighting-police-abuse-community-action-manual
    - https://campaignzero.org/
    """)
    st.header("Change. Now.")
    

#create a histogram or bar chart for the inputted column
def return_graph(df,col,rot):
    #get the count for each unique element within a column
    y = df.groupby(col).count().rename({"Unnamed: 0":"count"},axis=1)["count"]
    fig = plt.figure(figsize=(10,6))
    
    #plot bar chart for age, histogram for rest
    if col != "age":
        plt.bar(y.index,y.values)
    else:
        plt.hist(df[col],bins=20)
        
    #add information to graph
    plt.title("Annual Police Killings")
    plt.xlabel(col.title())
    plt.ylabel("# of Killings")
    plt.xticks(rotation=rot)
    return fig
    

#for each column, create graph and write explanation below
def show_graphs(df):
    st.subheader("By Year")
    f=return_graph(df,"year",0)
    st.pyplot(f)
    st.write("Over the past ten years, the number of killings has hovered between 1100-1200. However, in recent "
             + "years, it is worth noting a slight uptick in killings. This suggests that the issue of police "
             + "brutality may be getting worse in America.")
    
    st.subheader("By Race")
    f = return_graph(df,"race",60)
    st.pyplot(f)
    st.write("The graph shows that White people face the highest number of police brutality incidents with 4767, "
            + "followed by Black people with 1953, Hispanic people with 1953, Asian people with 160, "
            + "Native American people with 147, and Pacific Islander people with 61. However, we are unable to "
            + "conclude that the problem affects a certain race disproportionately, as different races make up "
            + "varying percentages of the American population.")
    
    st.subheader("By Gender")
    f = return_graph(df[df["gender"].isin(["Male","Female"])],"gender",0)
    st.pyplot(f)
    st.write("From the graph, males were the victims of 10,552 cases of police brutality, while women were killed "
            + "in only 584 incidents. This suggests that police brutality disproportionately affects men, as the "
            + "ratio of men:women in the United States is 98:100. It is worth noting that 10 transgender people were "
            + "victims of police brutality killings, although this was not shown in the graph due to the scale.")
    
    st.subheader("By Age")
    f = return_graph(df,"age",0)
    st.pyplot(f)
    st.write("Police brutality tended to affect people in their 20s and 30s the most, where the mode of the graph "
            + "is. However, what is more concerning is the ends of the graph. The police killed 3 5 year-old children "
            + "and  a 107 year-old. This is proof that police brutality must be constrained immediately.")
    

#create lists that are used to build selectboxes for different descriptors
def get_filters(df):
    #get unique values in column, sort, add unclicked value, and then remove nan
    year = list(df["year"].unique())
    year.sort(reverse=True)
    year = [""] + year
    year = [x for x in year if pd.notnull(x)]
    
    race = [""] + list(df["race"].unique())
    race = [x for x in race if pd.notnull(x)]
    
    #create lists for other columns, some using descriptors with most data, otherwise nothing to plot
    gender = [""] + list(df["gender"].value_counts().head(4).index)
    off_race = [""] + ["White","Hispanic","Black","Asian"]
    d_cause = [""] + list(df["death_cause"].value_counts().head(6).index)
    v_armed = [""] + list(df["v_armed"].value_counts().head(10).index)
    
    return [year,gender,race,off_race,d_cause,v_armed]

#create filters for individual case map
def ind_filters(df):
    #divide into columns
    col1,col2,col3 = st.columns(3)
    fils = get_filters(df)
    
    #add selectbox to each column
    with col1:
        year = st.selectbox("Year",fils[0])
        off = st.selectbox("Officer Race",fils[3])
    
    with col2:
        race = st.selectbox("Victim Race",fils[2])
        death = st.selectbox("Death Cause",fils[4])
    
    with col3:
        gender = st.selectbox("Gender",fils[1])
        armed = st.selectbox("Victim Armed",fils[5])
        
    return year,off,race,death,armed,gender

#create filters for state case map, same as previous function, but needed separate variables and function to make 
#separate sets of filters, otherwise would produce an error. No other way without creating duplicate function.
def state_filters(df):
    col1,col2,col3 = st.columns(3)
    fils = get_filters(df)
    
    with col1:
        year1 = st.selectbox("Year ",fils[0])
        off1 = st.selectbox("Officer Race ",fils[3])
    
    with col2:
        race1 = st.selectbox("Victim Race ",fils[2])
        death1 = st.selectbox("Death Cause ",fils[4])
    
    with col3:
        gender1 = st.selectbox("Gender ",fils[1])
        armed1 = st.selectbox("Victim Armed ",fils[5])
        
    return year1,off1,race1,death1,armed1,gender1


#filter data for each map based on what is clicked in the filters
def filter_data(df,fils):
    #don't filter for unclicked filters, remove data that isn't part of selected group
    cols = ["year","officer_races","race","death_cause","v_armed","gender"]
    for v in fils:
        if v != "":
            pos = fils.index(v)
            df = df[df[cols[pos]] == v]
            
    return df    

#randomize what points chosen for individual case map, max out at 70
def randomize(df,fils=""):
    #filter through data based on inputted ind_filters
    if fils != "":
        df = filter_data(df,fils)
    
    #add row indices randomly to list to filter dataset for those rows only
    if df.shape[0] > 70:
        ind_list = []
        while True:
            rand_num = random.randint(0,df.shape[0])
            if rand_num not in ind_list:
                ind_list.append(rand_num)
                
            if len(ind_list) == 70:
                break
            
        return df.iloc[ind_list]
    
    return(df)

#generate popup using html and case information
def generate_pop(df,i):
    row = df.iloc[i]
    
    #!DOCTYPE html creates an html script in Python code, <p> creates normal body text, .format() allows me to use
    #variables specific to each row, and <head> and <h4 style> creates a header with space below and a given width.
    #have to close each tag after started to denote start and end of text section.
    html = """<!DOCTYPE html>
    <html>
    <head>
    <h4 style="margin-bottom:10"; width="200px">{}</h4>""".format(row["name"]) + """
    </head>
    
    <body>
    <p>Date: {}""".format(row["date"]) + """</p>
    <p>Location: {}, {}""".format(row["city"],row["state"]) + """</p>
    <p>Gender: {}""".format(row["gender"]) + """</p>
    <p>Race: {}""".format(row["race"]) + """</p>
    <p>Officer Race(s): {}""".format(row["officer_races"]) + """</p>
    <p>Victim Armed: {}""".format(row["v_armed"]) + """</p>
    <p>Decription: {}""".format(row["circumstances"]) + """</p>
    
    </body>
    </html>
    """
    return html

#create map with popups and markers for individual cases
def ind_map(df):
    #if no points meet criteria for filter, display that
    if df.empty:
        st.write("No data matches these filters.")
    
    #create Folium map object
    map = folium.Map(location=[38,-96.5], zoom_start=4)
    
    #get coordinates in list format to use to tell Folium where each marker should go
    df.reset_index(drop=True,inplace=True)
    cords = df[["lat","lon"]]
    cord_list = cords.values.tolist()
    
    #loop through DataFrame, generate popup and add marker for each point, and add it to the map
    for i in range(df.shape[0]):    
        pop = folium.Popup(generate_pop(df,i), min_width=600, max_width=600)
        folium.Marker(cord_list[i], popup=pop).add_to(map)
    
    #build Folium map in streamlit
    i_map = st_folium(map, width=700, height=450)

    
def state_map(df,fils):
    #have to reimport streamlit or won't recognize
    import streamlit as st
    
    #apply filters, error message if filters have no results
    df = filter_data(df,fils)
    if df.empty:
        st.write("No data matches these filters.")
    
    #get count for each state, put into new dataframe
    df_state = df.groupby("state").count().rename({"Unnamed: 0":"count"},axis=1)["count"]
    df_st = pd.DataFrame({"state":df_state.index, "count":df_state.values})
    
    #create Folium map
    map = folium.Map(location=[38,-96.5], zoom_start=4)
    
    #add Folium chloropleth object which adds layer over map highlighting state boundaries using geojson file, and 
    #shades in states based on relative count value with different darkness
    #code for chloropleth adapted from https://www.youtube.com/watch?v=uXj76K9Lnqc tutorial
    chloropleth = folium.Choropleth(geo_data="us-state-boundaries.geojson", data=df_st, columns=("state","count"),
                                  key_on="feature.properties.name",line_opacity=0.7,highlight=True)
    
    chloropleth.geojson.add_to(map)
    
    #create new part of geojson file with the number of incidents that each state has from dataframe created earlier.
    #This is so that map has access to incidents, as it can't directly grab it from dataframe
    for feature in chloropleth.geojson.data["features"]:
        st = feature["properties"]["name"]
        if st in list(df_state.index):
            feature["properties"]["incident"] = "Incidents: " + str("{:,}".format(df_state.loc[st]))
        else:
            feature["properties"]["incident"] = "0"
    
    #add hover tool that shows incidents for each state and name
    chloropleth.geojson.add_child(folium.features.GeoJsonTooltip(["name","incident"], labels=False))
    
    #create folium map in streamlit
    st_map = st_folium(map, width=700, height=450)
    
#run main code
main()
