import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm, RecaptchaField
from PIL import Image, ImageChops
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

UPLOAD_FOLDER = 'images' #папка для загрузки
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])#возможные форматы

#конфигурация приложения
app = Flask(__name__, template_folder="templates", static_folder="images")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "dsf"
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LdHWLkaAAAAAFJioRgnPe-YNl4xxUhNaLTkCZno"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LdHWLkaAAAAANYhxdrrw7ujYb-3g4aZGOZcWcN8"

class ReCaptcha(FlaskForm):#форма для капчи
    recaptcha = RecaptchaField()

def make_plot(img,name):#функция для создания графика распределения цветов
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot()
    data = np.random.randint(0, 255, (100, 100))
    ax.imshow(img, cmap='plasma')
    b = ax.pcolormesh(data, edgecolors='black', cmap='plasma')
    fig.colorbar(b, ax=ax)
    sns.displot(data)
    plt.savefig("./images/plots/"+name+".png")
    plt.close()




@app.route('/img/<source_name>+<float:bright>')
def uploaded_file(source_name, bright):
    print(source_name, bright)#получаем название, тип, и цвет ргб
    source = Image.open('images/'+source_name)
    result = Image.new('RGB', source.size)
    for x in range(source.size[0]):
        for y in range(source.size[1]):
            r, g, b = source.getpixel((x, y))
            red = int(r * bright)
            red = min(255, max(0, red))
            green = int(g * bright)
            green = min(255, max(0, green))
            blue = int(b * bright)
            blue = min(255, max(0, blue))
            result.putpixel((x, y), (red, green, blue))
    result.save("images/new"+source_name, "PNG")
    make_plot(source, source_name)
    make_plot(result, "new"+source_name)
    return render_template("image.html", old_image=source_name)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = ReCaptcha()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename) and form.validate_on_submit():##занести в условие, когда капчу настроишь
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            bright=request.form['bright']
            return redirect(url_for('uploaded_file', source_name=filename, bright=bright))
    return render_template('index.html', form = form)

import lxml.etree as ET
@app.route("/apixml",methods=['GET', 'POST'])
def apixml():
    dom = ET.parse("./static/xml/file.xml")
    xslt = ET.parse("./static/xml/file.xslt")
    transform = ET.XSLT(xslt)
    newhtml = transform(dom)
    strfile = ET.tostring(newhtml)
    return strfile

if __name__ == '__main__':
    app.run(debug=True)
