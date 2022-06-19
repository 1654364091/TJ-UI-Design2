#!flask/bin/python
################################################################################################################################
#------------------------------------------------------------------------------------------------------------------------------                                                                                                                             
# This file implements the REST layer. It uses flask micro framework for server implementation. Calls from front end reaches 
# here as json and being branched out to each projects. Basic level of validation is also being done in this file. #                                                                                                                                  	       
#-------------------------------------------------------------------------------------------------------------------------------                                                                                                                              
################################################################################################################################
from flask import Flask, jsonify, abort, request, make_response, url_for,redirect, render_template,json
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
import shutil 
import numpy as np
from search import recommend
import tarfile
from datetime import datetime
from scipy import ndimage
#from scipy.misc import imsave
# from flask_cors import *

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
from tensorflow.python.platform import gfile
app = Flask(__name__, static_url_path = "")
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)   # 配置跨域
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
auth = HTTPBasicAuth()

#==============================================================================================================================
#                                                                                                                              
#    Loading the extracted feature vectors for image retrieval                                                                 
#                                                                          						        
#
#==============================================================================================================================
image_num = len(os.listdir("database/dataset"))
extracted_features=np.zeros((image_num,2048),dtype=np.float32)
with open('saved_features_recom.txt') as f:
    		for i,line in enumerate(f):
        		extracted_features[i,:]=line.split()
print("loaded extracted_features") 


#==============================================================================================================================
#                                                                                                                              
#  This function is used to do the image search/image retrieval
#                                                                                                                              
#==============================================================================================================================
def allowed_file(filename):
   return '.' in filename and \
          filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/imgUpload', methods=['GET', 'POST'])
def upload_img():
    print(request.url)
    print(request.form['k'])
    print("image upload")
    result = 'static/result'
    if not gfile.Exists(result):
          os.mkdir(result)
    shutil.rmtree(result)

    print(request.method)
    # check if the post request has the file part
    if 'file' not in request.files:
        print('No file part')
        return {"code":0,"data":None,"message":"No file part"}

    file = request.files['file']
    print(file.filename)
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        print('No selected file')
        return {"code":0,"data":None,"message":"No selected file"}
    # 检测是否是图片文件
    if allowed_file(file.filename) is False:
        print("Not image")
        return {"code":0,"data":None,"message":"Not image"}
    if file:
        filename = secure_filename(file.filename)

        k = int(request.form["k"])
        print(request.form["tag_list"])
        tag_str = request.form["tag_list"]
        print(tag_str)
        tag_list = tag_str.split(",")
        if tag_str == "":
            tag_list = []

        # k =5
        print(k)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        inputloc = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        recommend(inputloc, extracted_features,k,tag_list)
        os.remove(inputloc)
        image_path = "/result"
        image_list =[os.path.join(image_path, file) for file in os.listdir(result)
                          if not file.startswith('.')]
        # 图片
        return {"code":200,"data":image_list,"message":""}


FAVORITE_IMAGES_DIR = "static/favorite" # 每行存储用户收藏的图片位置情况，如：{“/result\im15.jpg”:1，“/result\im2283.jpg”:0}

@app.route("/viewMyFavoriteImages",methods=["GET"])
def viewMyFavoriteImages():
    images = []
    # 若不存在就创建一个"static/favorite"
    if os.path.exists(FAVORITE_IMAGES_DIR) is False:
        os.makedirs(FAVORITE_IMAGES_DIR)

    # 读取文件夹中的图片名
    file_name_list = os.listdir(FAVORITE_IMAGES_DIR)
    count = 0
    for file_name in file_name_list:
        images.append(os.path.join("/favorite",file_name))
        print(os.path.join("/favorite",file_name))
        count+=1
    return {"code":200,"data":images,"message":""}


@app.route("/addOneFavoriteImage",methods = ["POST"])
def addOneFavoriteImage():
    data = request.get_data()
    json_data = json.loads(data.decode("UTF-8"))
    image = json_data.get("image")

    # 检查是否已存在
    file_name_list = os.listdir(FAVORITE_IMAGES_DIR)
    path, image_name = os.path.split(image)     # 如：将"/result\\im21.jpg"拆成”/result“、”im21.jpg“
    for file_name in file_name_list:
        if image_name == file_name:
            return {"code":0,"data":None,"message":"您已经收藏过了"}
    # 不存在则复制图片到favorite
    source_path = os.path.join("static/result",image_name)
    target_path = os.path.join("static/favorite",image_name)
    shutil.copyfile(source_path,target_path)
    return {"code":200,"data":None,"message":""}


@app.route("/removeOneFavoriteImage",methods=["POST"])
def removeOneFavoriteImage():
    data = request.get_data()
    json_data = json.loads(data.decode("UTF-8"))
    image = json_data.get("image")

    # 检查是否已存在
    file_name_list = os.listdir(FAVORITE_IMAGES_DIR)
    path, image_name = os.path.split(image)
    exists = True   # 默认收藏夹存在想要删除的图片
    if image_name not in file_name_list:
        return {"code":0,"data":None,"message":"您已经取消收藏了"}
    else:
        os.remove(os.path.join("static/favorite",image_name))

    file_name_list = os.listdir(FAVORITE_IMAGES_DIR)
    images = []
    count = 0
    for file_name in file_name_list:
        images.append(os.path.join("/favorite", file_name))
        print(os.path.join("/favorite", file_name))
        count += 1
    return {"code":200,"data":images,"message":""}


#==============================================================================================================================
#                                                                                                                              
#                                           Main function                                                        	            #						     									       
#  				                                                                                                
#==============================================================================================================================
@app.route("/")
def main():
    return render_template("index.html")

@app.route("/favorite")
def favorite():
    return render_template("favorite.html")

if __name__ == '__main__':
    app.run(debug = True, host= '0.0.0.0')
