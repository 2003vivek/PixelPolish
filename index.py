from flask import Flask,render_template,jsonify,request,flash
import cv2
from werkzeug.utils import secure_filename
import os
import numpy as np

UPLOAD_FOLDER="edited_img"
ALLOWED_EXTENSIONS={'png','webp','jpg','jpeg','gif'}
app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.secret_key=('super secret key')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename,operation):
    # ret=f"the file name is {filename} and the file operationis {operation}"
    # return ret
    img=cv2.imread(f"edited_img/{filename}")
    
    match operation:
        case "cgray":
            img_gray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY) # or BGR2GRAY might also work
                    
            cv2.imwrite(f"static/{filename}",img_gray)
            new_file_path=f"static/{filename}"
            return new_file_path
        
        case "ccolor":
            img2=cv2.imread(f"edited_img/{filename}",cv2.IMREAD_GRAYSCALE)
            
            # img_COLORED=cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR) # or BGR2GRAY might also work
            img_COLORED = cv2.applyColorMap(img2, cv2.COLORMAP_JET)
                    
            cv2.imwrite(f"static/{filename}",img_COLORED)
            new_file_path=f"static/{filename}"
            return new_file_path
        
        case "cpng":
            cv2.imwrite(f"static/{filename.split('.')[0]}.png",img)
            new_file_path=f"static/{filename.split('.')[0]}.png"
            return new_file_path
        
        
        case "cwebp":
            cv2.imwrite(f"static/{filename.split('.')[0]}.webp",img)
            new_file_path=f"static/{filename.split('.')[0]}.webp"
            return new_file_path
        
        
        case "cjpg":
            cv2.imwrite(f"static/{filename.split('.')[0]}.jpg",img)
            new_file_path=f"static/{filename.split('.')[0]}.jpg"
            return new_file_path
        
        case "cCartoonize":
            # cv2.imwrite(f"static/{filename.split('.')[0]}.jpg",img)
            # new_file_path=f"static/{filename.split('.')[0]}.jpg"
            # return new_file_path
            
            img=cv2.imread(f"edited_img/{filename}")
            img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            
            gray_image=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
            gray_blur=cv2.medianBlur(gray_image,9,7)
            
            edges=cv2.adaptiveThreshold(gray_blur,300,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,9,7) #output 1
            
            data=np.float32(img).reshape((-1,3))
            criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,30,0.01)
            
            ret,label,center=cv2.kmeans(data,10,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
            center=np.uint8(center)
            result=center[label.flatten()]
            result=result.reshape(img.shape) #output 2
            blurred=cv2.bilateralFilter(img,d=0,sigmaColor=0,sigmaSpace=0)
            c=cv2.bitwise_and(blurred,blurred,mask=edges)


            cv2.imwrite(f"static/{filename}",c)
            new_file_path=f"static/{filename}"
            return new_file_path
            

        


    pass
    
    
    
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/edit", methods=['GET','POST'])
def edit():
    file=request.files['file']
    operation=request.form['operation']
    if request.method=="POST":
        if not request.files:
            flash('No file part')
            return "Error"
        if file.filename=='':
            flash("NO file name?")
            return "error..."
        # if request.files['file']:
        #     return "post request is here"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new=processImage(file.filename,operation)
            flash(f"your image is processed and you can find it : <a href='/{new}' target='_blank'> here</a>")
            
            return render_template("index.html")
           
            # return redirect(url_for('download_file', name=filename))
        
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)