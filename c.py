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
import cv2
import bb_video_gen as bb
import argparse
import os
from tqdm import tqdm
import glob


def encode_image(image_file):
    encoded = base64.b64encode(open(image_file,'rb').read())
    return 'data:image/png;base64,{}'.format(encoded.decode())

def create_dash(video_path,csv_dir,id_another_csv,bb_video_path):
#video getFilePath
    vid=cv2.VideoCapture(video_path)
    fps = int(vid.get(cv2.CAP_PROP_FPS))
    # reading xlsx file
    df_graph=pd.read_csv(csv_dir)
    frames=df_graph['Frame']
    y_graph=df_graph['LAnkle_Y']
    min_frames=frames.min()
    max_frames=frames.max()
    range_frame=int((max_frames-min_frames)/10)

    y_graph_min=y_graph.min()
    y_graph_max=y_graph.max()
    y_range=int((y_graph_max-y_graph_min)/10)
    total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

    #For gauges
    df_gauge=pd.read_csv(id_another_csv)
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
    ##print(index)

    fig=go.Figure(
        data=[go.Scattergl(
                            x=frames,
                            y=y_graph,
                            name='Moving Plot',
                            visible=True,
                            line=dict(color='blue')
        ),go.Scattergl(
                            x=frames,
                            y=y_graph,
                            name='Original Plot',
                            visible=True,
                            line=dict(color='#bf00ff')
        )],
        layout=go.Layout(
            xaxis=dict(range=[min_frames-range_frame,max_frames+range_frame],autorange=False,title='Frame Number'),
            yaxis=dict(range=[y_graph_min-y_range,y_graph_max+y_range],autorange=False,title='Left Ankle'),
            title={
            'text': "My Graph",
            'y':0.9,
            'x':0.4,
            'xanchor': 'center',
            'yanchor': 'top'}
        ),
    )

    app = dash.Dash(__name__)

    app.layout = html.Div([
                    dcc.Graph(id='my-graph',figure=fig,
                            style={'display':'inline-block','width':'50%','height':'10%'}),
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
                                controls=False,
                                width='100%',
                                loop=True,
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            'width': '40%',
                            'float': 'left',
                            'margin': '0% 5% 1% 5%'
                        },
                        children=[
                            dash_player.DashPlayer(
                                id='bounding_box',
                                url=bb_video_path,
                                controls=False,
                                width='50%',
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
                                 options=[{'label': val.capitalize(), 'value': val} for val in [
                                'playing'
                                ]],
                                value=['controls'],
                                labelStyle={'size':'0px','display':'inline-block'}
                            ),
                        ]
                    ),
            ])

    #I dont know what it does but without it code doesnot work
    @app.callback([Output('video-player', 'playing'),
                    Output('bounding_box', 'playing')],
                  [Input('radio-bool-props', 'value')])
    def update_prop_playing(values):
        return ('playing' in values,'playing' in values)
    @app.callback(Output('bounding_box', 'currentTime'),
                  [Input('video-player', 'currentTime')])
    def update_prop_play(values):
        return values


    @app.callback(Output('my-graph','figure'),
                [Input('video-player','currentTime')])
    def outwsr(currentTime):
        index1=0
        if(currentTime is not None):
            index1=int((currentTime*fps))
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
            index1=int((currentTime*fps))
        if (index1>=total_gauge_value-1):
            index1=total_gauge_value-1
        return (first_gauge[index1],second_gauge[index1])
    return app

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_dir",help="Relative Path with extension to directory of CSV which is used for main graph")
    parser.add_argument("--video_path",help="Relative Path to Original Video")
    parser.add_argument('--id_another_csv',type=str,help='TRelative path with extension of stride frequency csv')
    parser.add_argument("--out_dir",help="Relative Path where video need to be saved")
    parser.add_argument("--res",default=360,type=int,help="Resolution of Output Video - High Value may result in larger Pixelation")
    opt = parser.parse_args()

    csv_dir = opt.csv_dir
    video_path = opt.video_path
    id_another_csv=opt.id_another_csv
    output_dir = opt.out_dir
    res = opt.res

    #all_id_csv_path = glob.glob(csv_dir+"/*.csv")

    #for id_csv_path in all_id_csv_path:

    bb.generate_bb_video(video_path,csv_dir,output_dir,res)

    video_name = os.path.basename(video_path)[:-4]
    id_number = os.path.basename(csv_dir).split("-")[-3]
    out_dir = os.path.join(output_dir[:-1]+"/","ID_BB_VIDEOS/")
    #Relative path of the video so created with converted to mp4 format.
    outputFile = out_dir+"VM-" + video_name + "-" + str(id_number) + ".mp4"

    #print(out_dir)
    #print(outputFile)
    app=create_dash(video_path,csv_dir,id_another_csv,outputFile)
    app.run_server(debug=False,threaded=True)
