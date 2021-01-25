import  numpy as np
import pandas as pd
import plotly.offline as pyo
import plotly.graph_objs as go
import dash_daq as daq
import dash_player
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

def encode_image(image_file):
    encoded = base64.b64encode(open(image_file,'rb').read())
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
        xaxis=dict(range=[x_min-100,x_max+100],autorange=False,tickwidth=2,title='Distance From Start'),
        yaxis=dict(range=[y_min-20,y_max+20],autorange=False,title='Stride Frequency'),
        title='My-Graph'
    ),
)

app = dash.Dash(__name__)

app.layout = html.Div([
                dcc.Graph(id='my-graph',figure=fig,
                        style={'display':'inline-block','width':'50%','height':'10%'}),
                dcc.Interval(id='interval-component',
                            interval=3450/(length+1),
                            n_intervals=0,
                            max_intervals=-1,
                            disabled=True),
                html.Div([daq.Gauge(
                    id='my-Gauge',
                    showCurrentValue=True,
                    value=y[0],
                    label='Stride Frequecy',
                    color={"gradient":True,"ranges":{"green":[150,200],"yellow":[200,250],"red":[250,300]}},
                    max=300,
                    min=150,
                )],style={'display':'inline-block'}),
                html.Div([daq.Gauge(
                    id='my-Gauge1',
                    showCurrentValue=True,
                    units='ms',
                    value=z[0],
                    label='Stride Duration',
                    color={"gradient":True,"ranges":{"green":[150,200],"yellow":[200,250],"red":[250,300]}},
                    max=300,
                    min=150,
                )],style={'display':'inline-block'}),
                html.Div(
                    style={
                        'width': '40%',
                        'float': 'left',
                        'margin': '0% 5% 1% 5%'
                    },
                    children=[
                        dash_player.DashPlayer(
                            id='video-player',
                            url=video_path,
                            controls=False,
                            width='100%',
                            loop=True
                        )
                    ]
                ),

                html.Div(
                    style={
                        'width': '30%',
                        'float': 'left'
                    },
                    children=[
                        dcc.Checklist(
                            id='radio-bool-props',
                            options=[{'label':'Play','value':'playing'},
                                    {'label':'mute','value':'muted'}
                            ],
                            value=['controls']
                        ),
                    ]
                ),
            ])

@app.callback(Output('video-player', 'playing'),
              [Input('radio-bool-props', 'value')])
def update_prop_playing(values):
    return 'playing' in values

@app.callback(Output('video-player', 'muted'),
              [Input('radio-bool-props', 'value')])
def update_prop_muted(values):
    return 'muted' in values

@app.callback(Output('my-graph','figure'),
            [Input('interval-component','n_intervals')])
def outwsr(n_intervals):
    n_intervals=n_intervals%length
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
            xaxis=dict(range=[x_min-100,x_max+100],autorange=False,tickwidth=2,title='Distance From Start'),
            yaxis=dict(range=[y_min-20,y_max+20],autorange=False,title='Stride Frequency'),
            title='My-Graph'
        ),
    )
    if(n_intervals>0 and n_intervals<=length-1):
        fig=go.Figure(
            data=[go.Scatter(
                                x=[x[n_intervals],x[n_intervals]],
                                y=[y_min-20,y_max+20],
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
                xaxis=dict(range=[x_min-100,x_max+100],autorange=False,tickwidth=2,title='Distance From Start'),
                yaxis=dict(range=[y_min-20,y_max+20],autorange=False,title='Stride Frequency'),
                title='My-Graph'
            ),
        )
    return fig

@app.callback([Output('my-Gauge','value'),
                Output('my-Gauge1','value')],
                [Input('interval-component','n_intervals')]
                )
def output_value(n_intervals):
    index1=0
    n_intervals=n_intervals%length
    if(n_intervals>=0 and n_intervals<=length-1):
        index1=n_intervals
    return (y[index1],z[index1])

@app.callback(Output('interval-component','disabled'),
                    [Input('radio-bool-props', 'value')])
def start_stop_update(value):
    if 'playing' in value:
        return False
    else:
        return True


if __name__ == '__main__':
    app.run_server(debug=False)
