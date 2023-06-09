import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from PIL import Image
import numpy as np
import tensorflow as tf
import argparse
from tensorflow.keras.preprocessing.image import img_to_array
from utils import get_lowres_image
import time 
import tqdm, glob 
import cv2 
import numpy as np 
import matplotlib.pyplot as plt 
from models import get_zero_dce

parser = argparse.ArgumentParser()

parser.add_argument('--model_path', type=str, default='pretrained_weights/best_model.h5')
parser.add_argument('--test_data_path', type=str, default='test/LIME/')
parser.add_argument('--result_data_path', type=str, default='results/LIME/')
parser.add_argument('--mode', type=str, default="super_resolution")
parser.add_argument('--file_extension', type=str, default='bmp')
parser.add_argument('--visualize_result', type=bool, default=True)
parser.add_argument('--model_type', type=str, default='zerodce')
parser.add_argument('--num_filters', type=int, default=32)

args = parser.parse_args()

def test(model):

    lowlight_test_images_path = args.test_data_path
    test_files = glob.glob(lowlight_test_images_path + f"*.{args.file_extension}")

    for test_file in tqdm.tqdm(test_files, total=len(test_files)):
        filename = test_file.split("/")[-1]        
        lr_img = Image.open(test_file)

        inputs = (np.asarray(lr_img)/255.0).astype(np.float32)
        inputs = get_lowres_image(inputs, mode=args.mode)
        
        inputs = np.expand_dims(inputs, axis=0)
        t = time.time()
        
        # inputs_shape = inputs.shape
        # inferrer_input_dims = (1, inputs_shape[0], inputs_shape[1], inputs_shape[2])
        enhanced_image = model(inputs)
       
        print("Time taken for inference: ", time.time() - t)

        if args.visualize_result:
            plt.figure()
            plt.subplot(121)
            plt.title("Low Resolution Image")
            plt.imshow(lr_img)
            
            plt.subplot(122)
            plt.title("Low Resolution Image")
            plt.imshow(enhanced_image[0])
            
            plt.show()
        
        save_file_path = args.result_data_path  + filename
        enhanced_image = tf.cast((enhanced_image[0,:,:,:] * 255), dtype=np.uint8)
        enhanced_image = Image.fromarray(enhanced_image.numpy())
        enhanced_image.save(save_file_path)


if __name__ == '__main__':
    
    if args.model_type == "zerodce":
        model = get_zero_dce(n_filters=args.num_filters)
        model.load_weights(args.model_path)
    
    test(model)