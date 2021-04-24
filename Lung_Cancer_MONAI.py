# -*- coding: utf-8 -*-
"""sreamlit_lung_cancer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sw0GW4h_1IuuPM8Mgbgl4UjMRFJfeceW
"""
import numpy as np
import streamlit as st
import pickle
import torch
import torchvision
import torch.nn as nn
from torchvision import transforms
 
import cv2
from PIL import Image,ImageOps
import dill as dill
import matplotlib.pyplot as plt
import matplotlib.patches as patches
sm=torch.nn.Softmax()

st.set_page_config(layout="wide")
page_bg_img = '''
<style>
body {
background-image: url("https://i.imgur.com/D0IOa1W.jpg?format=png");
background-size: cover;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)


st.title("""
Lung Cancer Prediction from X-Ray image
""")

st.write("""
Lung cancer, also known as lung carcinoma, is a malignant lung tumor characterized
by uncontrolled cell growth in tissues of the lung. This growth can spread
beyond the lung by the process of metastasis into nearby tissue or other parts of the body. Most
cancers that start in the lung, known as primary lung cancers, are carcinomas. \n
In the United States, lung cancer is the second most common cancer in both men and women.
It’s also the leading cause of death from cancer.
If lung cancer is found at an earlier stage, when it is small and before it has spread, it is more likely to be successfully treated.

### The standard digital image database with and without chest lung nodules (JSRT database) was created by the Japanese Society of Radiological Technology (JSRT) in cooperation with the Japanese Radiological Society (JRS) in 1998.

#### Tumors can be benign (noncancerous) or malignant (cancerous). Benign tumors tend to grow slowly and do not spread. Malignant tumors can grow rapidly, invade and destroy nearby normal tissues, and spread throughout the body. Benign tumor is considered is Normal as they are not cancerous.
 """)

img = cv2.imread(r'JPCLN022.png',0)  
img=Image.fromarray(img)
c2 ,c3  = st.beta_columns(( 0.3, 0.3))
c2.header("Malignant")
c3.header("Normal")
c2.image(img, use_column_width=True)
imgc2 = cv2.imread(r'JPCLN060.png',0)  
imgc2=Image.fromarray(imgc2)
c3.image(imgc2, use_column_width=True)


c5, c6,  = st.beta_columns(( 2, 1))
c5.header('User Input image')
c5.markdown("""
[Sample image](img)""")
c5.button("Upload your X-Ray below")
uploaded_file=c5.file_uploader("", type = ["png"])
transformations_new=transforms.Compose([
    transforms.Resize(255),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=torch.tensor(0.5950) , std=torch.tensor(0.2735))
])
if uploaded_file is not None:
  uploaded_image=ImageOps.grayscale(Image.open(uploaded_file))
  input_new=  transformations_new(uploaded_image)
  input_new=input_new.unsqueeze(0)
  input_image=transforms.Resize(255)(uploaded_image)

else :
  input_image=transforms.Resize(255)(img)
  input_new=  transformations_new(input_image)
  input_new=input_new.unsqueeze(0)


if uploaded_file is not None:
  c6.image(input_image,channel='BGR')
else:
    c6.button("""Awaiting X_ray image to be uploaded. Currently using sample X_Ray image (shown below)""")
    c6.image(input_image)
    
import monai
from monai.networks.nets import densenet121
model = densenet121(spatial_dims=2, in_channels=1,out_channels=2)#.to(device)#spatial_dims=2, in_channels=1,out_channels=num_classes
model.eval()
output = model.load_state_dict(torch.load("best_metric_model_400epochs.pth",map_location=torch.device('cpu')))
output=model(input_new)

malignant_probability=nn.Softmax()(output.data[0])[1].cpu().numpy()


st.subheader('Predicted Malignant Probability')
st.write(np.around(malignant_probability*100,2),'%')

localisation_model=densenet121(spatial_dims=2,in_channels=1,out_channels=3)
localisation_model.eval()
if malignant_probability >0.5:
  bbox=localisation_model.load_state_dict(torch.load("localisation_model.pth",map_location=torch.device('cpu')))
  bbox=localisation_model(input_new)
  x,y,size=bbox[0][0],bbox[0][1],bbox[0][2]

  predicted_x=(x.detach()*244).numpy().astype(int)
  predicted_y=(y.detach()*244).numpy().astype(int)
  predicted_size=size.detach().numpy()*244/34

  fig, ax = plt.subplots(figsize=(10,10))
  ax.imshow(input_new[0][0].numpy(),cmap='gray')
  rect = patches.Rectangle((int(predicted_x-predicted_size*10/2), int(predicted_y-predicted_size*10/2)), predicted_size*10, predicted_size*10, linewidth=2, edgecolor='r', facecolor='none')
  ax.add_patch(rect)

  #fig.savefig('xray_with_bbox.png',bbox_inches='tight', cmap='gray')

  c7, c8,  = st.beta_columns(( 2, 1))
  c8.pyplot(fig)
  #c8.image('xray_with_bbox.png')
             

st.markdown("""<style>h1{color: #F9FF33;}</style>""", unsafe_allow_html=True)
st.markdown("""<style>h2{color: orange;}</style>""", unsafe_allow_html=True)
st.markdown("""<style>h3{color: #08FC58;}</style>""", unsafe_allow_html=True)
st.markdown("""<style>p{color: white;}</style>""", unsafe_allow_html=True)
st.markdown("""<style>h4{color: white;}</style>""", unsafe_allow_html=True)