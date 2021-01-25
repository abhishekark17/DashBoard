import dash
import numpy as np
import pandas as pd
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import base64
import dash_daq as daq
import dash_player
import json

## encode image to be able to show on browser
def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded.decode())
# reading xlsx file
df=pd.read_excel('touch_downs_4114.xlsx')
df=df.dropna()
x_=df['x']
x_min=x_.min()
x_max=x_.max()
x_=x_.tolist()
x1=[]
index=df.index
y_=df['stride frequency']
y_min=y_.min()
y_max=y_.max()
y_=y_.tolist()
y1=[]
z_=df['stride duration (secs)']*1000
z_min=z_.min()
z_max=z_.max()
z_=z_.tolist()
z1=[]

#creating extra data
for i in range(0,len(x_)-1):
    a=np.linspace(x_[i],x_[i+1],5).tolist()
    x1+=a
for i in range(0,len(y_)-1):
    b=np.linspace(y_[i],y_[i+1],5).tolist()
    y1+=b
for i in range(0,len(z_)-1):
    c=np.linspace(z_[i],z_[i+1],5).tolist()
    z1+=c
x=np.array(x1)
y=np.array(y1)
z=np.array(z1)
length=len(x1)
#video getFilePath
video_path='static/IMG_4114.mp4'


#styling for guage


app = dash.Dash()

app.layout = html.Center(html.Div([
            dcc.Graph(id='my-graph',
                    style={'display':'inline-block','width':'50%','height':'10%'}),
            html.Div([daq.Gauge(
                id='my-Gauge',
                showCurrentValue=True,
                value=y.min(),
                label='Stride Frequecy',
                color={"gradient":True,"ranges":{"green":[150,200],"yellow":[200,250],"red":[250,300]}},
                max=300,
                min=150,
            )],style={'display':'inline-block'}),
            html.Div([daq.Gauge(
                id='my-Gauge1',
                showCurrentValue=True,
                units="ms",
                value=z[0],
                label='Stride Duration',
                color={"gradient":True,"ranges":{"green":[150,200],"yellow":[200,250],"red":[250,300]}},
                max=300,
                min=150,
            )],style={'display':'inline-block'})
            ,
            html.Center([
                dash_player.DashPlayer(
                    id='video-player',
                    url=video_path,
                    controls=True
                ),
                ])
]))

@app.callback(Output('my-graph','figure'),
                [Input('video-player','currentTime'),
                Input('video-player','secondsLoaded')]
                )
def graph_ouput(currentTime,secondsLoaded):
    x_range=(x.max()-x.min())/secondsLoaded
    x_start=x.min()
    dist=x_start+currentTime*x_range
    figure={
    'data':[go.Scatter(x=x,y=y,mode='lines')],
    'layout':go.Layout(title='Stride Frequency Vs Distance Travelled',
                        hovermode='closest',
                        xaxis={'title':'Distance from Start'},
                        yaxis={'title':'Stride Frequency'})}
    fig=go.Figure(data=figure['data'],layout=figure['layout'])
    fig.add_vline(x=dist,line_width=2,line_color='green')
    return fig



@app.callback(Output('my-Gauge','value'),
                [Input('video-player','currentTime'),
                Input('video-player','secondsLoaded')]
                )
def output_value(currentTime,secondsLoaded):
    x_range=(x.max()-x.min())/secondsLoaded
    x_start=x.min()
    dist=x_start+currentTime*x_range
    index = (np.abs(x-dist)).argmin()
    return y[index]

@app.callback(Output('my-Gauge1','value'),
                [Input('video-player','currentTime'),
                Input('video-player','secondsLoaded')]
                )
def output_value(currentTime,secondsLoaded):
    x_range=(x.max()-x.min())/secondsLoaded
    x_start=x.min()
    dist=x_start+currentTime*x_range
    index = (np.abs(x-dist)).argmin()
    return z[index]

if __name__ == '__main__':
    app.run_server(debug=False)
