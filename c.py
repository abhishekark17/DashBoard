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
import moviepy.editor

def encode_image(image_file):
    encoded = base64.b64encode(open(image_file,'rb').read())
    return 'data:image/png;base64,{}'.format(encoded.decode())

#video getFilePath
video_path='static/video.mp4'
video_duration=(moviepy.editor.VideoFileClip(video_path).duration)*1000
# reading xlsx file
df_graph=pd.read_csv('id-1-pose-26.csv')
frames=df_graph['Frame']
y_graph=df_graph['LAnkle_Y']
min_frames=frames.min()
max_frames=frames.max()
y_graph_min=y_graph.min()
y_graph_max=y_graph.max()
total_frames=len(frames)

#For gauges
df_gauge=pd.read_csv('touch_downs_4114.csv')
df_gauge=df_gauge.dropna()
first_gauge=df_gauge['stride frequency']
second_gauge=df_gauge['stride duration (secs)']*1000
first_gauge=first_gauge.tolist()
second_gauge=second_gauge.tolist()
#Creating extra data for smoothness of gauges
linspace_value=int(total_frames/(len(first_gauge)-1))
##extra_linspace_value=total_frames % (len(first_gauge)-1)
a=[]
b=[]
for i in range(len(first_gauge)-1):
    to_be_added=np.linspace(first_gauge[i],first_gauge[i+1],linspace_value).tolist()
    a+=to_be_added
for i in range(len(second_gauge)-1):
    to_be_added=np.linspace(second_gauge[i],second_gauge[i+1],linspace_value).tolist()
    b+=to_be_added
first_gauge=np.array(a)
second_gauge=np.array(b)

total_gauge_value=len(first_gauge)
one_gauge_time=video_duration/total_gauge_value
##print(index)


one_frame_time=video_duration/total_frames

fig=go.Figure(
    data=[go.Scattergl(
                        x=frames,
                        y=y_graph,
                        visible=True,
                        line=dict(color='blue')
    ),go.Scattergl(
                        x=frames,
                        y=y_graph,
                        visible=True,
                        line=dict(color='#bf00ff')
    )],
    layout=go.Layout(
        xaxis=dict(range=[min_frames-100,max_frames+100],autorange=False,title='Frame Number'),
        yaxis=dict(range=[y_graph_min-20,y_graph_max+20],autorange=False,title='Left Ankle'),
        title='My-Graph'
    ),
)

app = dash.Dash(__name__)

app.layout = html.Div([
                dcc.Graph(id='my-graph',figure=fig,
                        style={'display':'inline-block','width':'50%','height':'10%'}),
                dcc.Interval(id='interval-component',
                            interval=one_frame_time,
                            n_intervals=0,
                            max_intervals=-1,
                            disabled=True),
                html.Div([daq.Gauge(
                    id='my-Gauge',
                    showCurrentValue=True,
                    value=first_gauge[0],
                    label='Stride Frequecy',
                    color={"gradient":True,"ranges":{"green":[150,200],"yellow":[200,250],"red":[250,300]}},
                    max=300,
                    min=150,
                )],style={'display':'inline-block'}),
                html.Div([daq.Gauge(
                    id='my-Gauge1',
                    showCurrentValue=True,
                    units='ms',
                    value=second_gauge[0],
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
                            controls=True,
                            width='100%',
                            loop=True,
                        )
                    ]
                ),

                html.Div(
                    style={
                        'width': '30%',
                        'float': 'left',
                        'color':'red'
                    },
                    children=[
                        dcc.Checklist(
                            id='radio-bool-props',
                            options=[{'label':'Play','value':'playing'},
                                    {'label':'mute','value':'muted'}
                            ],
                            value=['controls'],
                            labelStyle={'size':'100px','display':'inline-block'}
                        ),
                    ]
                ),
            ])
'''
@app.callback(Output('video-player', 'playing'),
              [Input('radio-bool-props', 'value')])
def update_prop_playing(values):
    return 'playing' in values

@app.callback(Output('video-player', 'muted'),
              [Input('radio-bool-props', 'value')])
def update_prop_muted(values):
    return 'muted' in values

@app.callback(Output('interval-component','disabled'),
                    [Input('radio-bool-props', 'value')])
def start_stop_update(value):
    if 'playing' in value:
        return False
    else:
        return True
'''
@app.callback(Output('my-graph','figure'),
            [Input('video-player','currentTime')])
def outwsr(currentTime):
    index1=0
    if(currentTime is not None):
        index1=int((currentTime*1000)/one_frame_time)
    if(index1>=total_frames):
        index1=total_frames
    fig['data'][0]['x']=[index1,index1]
    fig['data'][0]['y']=[y_graph_min-20,y_graph_max+20]
    return fig

@app.callback([Output('my-Gauge','value'),
                Output('my-Gauge1','value')],
                [Input('video-player','currentTime')]
                )
def output_value(currentTime):
    index1=0
    if(currentTime is not None):
        index1=int((currentTime*1000)/one_gauge_time)
    if (index1>=total_gauge_value-1):
        index1=total_gauge_value-1
    return (first_gauge[index1],second_gauge[index1])

if __name__ == '__main__':
    app.run_server(debug=False,threaded=True)
