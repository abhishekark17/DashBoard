import pandas as pd
import os
import numpy as np
import cv2
from tqdm import tqdm
import argparse
import glob

def generate_bb_video(video_path,id_csv_path,out_dir,res):
    
    id_metrics = pd.read_csv(id_csv_path)
    cam = cv2.VideoCapture(video_path)

    video_name = os.path.basename(video_path)[:-4]
    id_number = os.path.basename(id_csv_path).split("-")[-3]
    fps = cam.get(cv2.CAP_PROP_FPS)
    number_of_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    print("Visualizing ID : {}".format(id_number))
    pbar = tqdm(number_of_frames)

    out_dir = os.path.join(out_dir,"ID_BB_VIDEOS/")
    os.makedirs(out_dir,exist_ok=True)

    frame_count = 0
    buffer_pixels_around_box = 40

    outputFile = "VM-" + video_name + "-" + str(id_number) + ".avi"

    if res==360:
        size = (360,640)
    elif res==480:
        size = (480,852)
    elif res==720:
        size = (720,1280)
    
    output_video_file = cv2.VideoWriter(out_dir + outputFile, fourcc, fps, size)

    while frame_count < number_of_frames:
        ret_val, image = cam.read()
        height, width, layers = image.shape
        pbar.update(1)
        frame_count += 1

        missing_data = False

        try:
            row = id_metrics.loc[id_metrics['Frame'] == frame_count].iloc[0]

        except:
            missing_data = True

        if missing_data:
            resized_img = np.ones((size[1],size[0],3), np.uint8) * 64      
        else:
            bbox = [int(row['TL_X'])-buffer_pixels_around_box,int(row['TL_Y'])-buffer_pixels_around_box,
                    int(row['BR_X'])+buffer_pixels_around_box,int(row['BR_Y'])+buffer_pixels_around_box]
            
            if bbox[0]<0:
                bbox[0] = 0
            if bbox[1]<0:
                bbox[1] = 0
            if bbox[2]> width:
                bbox[2] = width
            if bbox[3]>height:
                bbox[3] = height
                     
            bb_image = image[bbox[1]:bbox[3],bbox[0]:bbox[2]]

            resized_img = cv2.resize(bb_image, size, interpolation = cv2.INTER_AREA)

        output_video_file.write(resized_img)

    pbar.close()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_dir",help="Path to directory of CSVs of IDs to create BB video for")
    parser.add_argument("--video_path",help="Path to Original Video")
    parser.add_argument("--out_dir",help="Path to Directory to Save BB Videos at")
    parser.add_argument("--res",default=360,type=int,help="Resolution of Output Video - High Value may result in larger Pixelation")
    opt = parser.parse_args()

    csv_dir = opt.csv_dir
    video_path = opt.video_path
    output_dir = opt.out_dir
    res = opt.res

    all_id_csv_path = glob.glob(csv_dir+"/*.csv")

    for id_csv_path in all_id_csv_path:

        generate_bb_video(video_path,id_csv_path,output_dir,res)

