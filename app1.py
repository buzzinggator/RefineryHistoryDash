import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np


#app = Dash()
app1 = Dash(__name__, suppress_callback_exceptions=True)

CSScolors = ['#AA0DFE', '#3283FE', '#85660D', '#782AB6', '#565656', '#1C8356', '#16FF32', '#F7E1A0', '#E2E2E2', '#1CBE4F', '#C4451C', '#DEA0FD', '#FE00FA', '#325A9B', '#FEAF16', '#F8A19F', '#90AD1C', '#F6222E', '#1CFFCE', '#2ED9FF', '#B10DA1', '#C075A6', '#FC1CBF', '#B00068', '#FBE426', '#FA0087']

url = "https://raw.githubusercontent.com/buzzinggator/RefineryHistoryDash/refs/heads/main/python%20refinery%20history.csv"
df = pd.read_csv(url)
tempPADD=df.copy()
tempPADD['PADD'] = tempPADD['PADD'].astype(str)
tempPADD['PADD Sum'] = tempPADD.groupby(['Year','PADD'])['Quantity'].transform(lambda x: x.sum())
tempPADD2 = tempPADD[['PADD Sum','Year','PADD']].drop_duplicates().sort_values(by=[ 'PADD'], ascending=True)
fig3 = px.bar(tempPADD2, x="PADD Sum", y="Year", color='PADD', orientation='h')

df['Parent Company']=df['Parent Company'].fillna("")
parents = df['Parent Company'].unique().tolist()
parents.sort()




app1.layout = html.Div([
    html.H1("History of US Refining (Scroll down for more figures)"),
    html.Div([
        dcc.Graph(id='mapWithSlider',
                style={'height': '90vh'}, 
                figure={"layout": {
                    }}
                ),
        dcc.Slider(
            df['Year'].min(),
            df['Year'].max(),
            
            tooltip={"placement": "bottom", "always_visible": True},
            
            #marks=None,
            value=df['Year'].min(),
            #marks={str(year): str(year) for year in df['year'].unique()},
            marks={1880:"1880",
                   1900:'1900',
                   1920:"1920",
                   1940:"1940",
                   1960:"1960",
                   1980:"1980",
                   2000:"2000",
                   2020:"2020"},
            id='yearSlider'
        )
    ]),
    html.Div([
        dcc.Dropdown(
            parents,
            'Select Parent Company',
            id='parentDropdown',
            #value=selectedParent,
            style={'width': '20vh'}
        ),
        dcc.Graph(id='timeSeries',
                  style={'height': '80vh'})
    ]),
    html.Div([
        dcc.Graph(id='stackedBar',
                  style={'height': '80vh'},
                  figure=fig3)
    ]),
    html.Div([
        html.Ul("The data summarized here primarily comes from the following sources:"),
        html.Li("Petroleum refineries in the United States...(1926,1928-1932)"),
        html.Li("Petroleum refineries, including cracking plants, in the United States...(1933-1961)")
    ])
])


@callback(
    Output('mapWithSlider', 'figure'),
    Input('yearSlider', 'value')
)

def updateFigure(selectedYear):
    dfYearTemp = df[df['Year'] == selectedYear]
    dfYearTemp['Total Parent Capacity'] = dfYearTemp.groupby('Parent Company')['Quantity'].transform('sum')

    dfYear = dfYearTemp.sort_values(by=['Total Parent Capacity'], ascending=False)
    #print(dfYear)

    fig=px.scatter_geo(dfYear, 
                       lat='Lat', 
                       lon='Long', 
                       color='Parent Company',
                       scope='usa',
                       size='Quantity',
                       color_discrete_sequence=CSScolors
                       )
    
    fig.update_layout(
        title_text = str(selectedYear)+' Refineries'
    )

    return fig


@callback(
    Output('timeSeries', 'figure'),
    Input('parentDropdown','value')
)

def update_time_series(selectedParent):
    temp1 = df[df['Parent Company'] == selectedParent]
    temp2 = temp1.groupby('Year')['Quantity'].sum().reset_index()
    temp2['Site'] = "Fleet"
    temp3 = temp1.merge(temp2, on = ['Year','Site','Quantity'], how = 'outer')
    dfTimeSeries = temp3.sort_values(by=['Parent Company','Year'], ascending=True)    
    fig2 = px.scatter(dfTimeSeries, x='Year', y='Quantity', color='Site')
    fig2.update_traces(mode='lines+markers')

    return fig2




if __name__ == '__main__':
    #app.run_server()
    server = app1.server
    app1.run_server(debug=False, port=10000, host='0.0.0.0')





