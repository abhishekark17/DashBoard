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
x=df['x']
y=df['stride frequency']
stride_duration=df['stride duration (secs)']*1000
index=df.index
##print(index)
#video getFilePath
video_path='static/IMG_4114.mp4'

fig=go.Figure(
    data=[go.Scatter(
                        x=x,
                        y=y,
                        name='Moving Line',
                        visible=True,
                        line=dict(color='blue')
    ),go.Scatter(
                        x=x,
                        y=y,
                        name='First Plot',
                        visible=True,
                        line=dict(color='#bf00ff')
    )],
    layout=go.Layout(
        xaxis=dict(range=[x.min()-100,x.max()+100],autorange=False,tickwidth=2,title='Distance From Start'),
        yaxis=dict(range=[y.min()-20,y.max()+20],autorange=False,title='Stride Frequency'),
        title='My-Graph'
    ),
    frames=[
        go.Frame(
            data=[
                go.Scatter(
                    x=[x[k],x[k]],
                    y=[y.min()-20,y.max()+20],
                    mode='lines',
                    marker=dict(color="blue", size=10)
                )
            ]
        ) for k in range(index[0],index[-1]+1)
    ]
)

fig.update_layout(
    updatemenus=[
    {
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 500, "redraw": False},
                                "fromcurrent": True, "transition": {"duration": 300,
                                                                    "easing": "quadratic-in-out"}}],
                "label": "Play",
                "method": "animate",
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"
            }
        ]
        }
    ]
)

app = dash.Dash()

app.layout = html.Center(html.Div([
            dcc.Graph(id='my-graph',figure=fig,
                    style={'display':'inline-block','width':'50%','height':'10%'}),
            html.Div([daq.Gauge(
                id='my-Gauge',
                showCurrentValue=True,
                units="stride_frequency",
                value=y.min(),
                label='Default',
                max=300,
                min=150,
            )],style={'display':'inline-block'}),
            html.Div([daq.Gauge(
                id='my-Gauge1',
                showCurrentValue=True,
                units="stride Duration",
                value=stride_duration.min(),
                label='Default',
                color={"gradient":True,"ranges":{"green":[150,200],"yellow":[200,250],"red":[250,300]}},
                max=300,
                min=150,
            )],style={'display':'inline-block','background-color': '#F4F2F1'})
            ,
            html.H1(id='my-output'),
            html.Center([
                dash_player.DashPlayer(
                    id='video-player',
                    url=video_path,
                    controls=True
                ),
                ])
]))

'''@app.callback(Output('my-output','children'),
            [Input('my-graph','figure')])
def outwsr(fig):
    if fig['layout']['updatemenus'][0]['active']==0:
        #fig['layout']['updatemenus'][0]['active']=0
        return "RAm"
    else:
        #fig['layout']['updatemenus'][0]['active']=1
        return "Abs"
    #return fig
'''
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


if __name__ == '__main__':
    app.run_server(debug=False)
