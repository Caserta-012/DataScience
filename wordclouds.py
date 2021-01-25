from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np
import re

def word_cloud():
    path = 'C:\\Users\Caserta\Desktop\阶段4 TF_IDF.txt'
    img_path = 'C:\\Users\Caserta\Desktop\BG.jpg'
    f = open(path,'r',encoding='utf-8').read()
    bg = np.array(Image.open(img_path))
    pattern = re.compile('.*?:')
    text = re.findall(pattern, f)
    for i in range(len(text)):
        text[i] = text[i][:-1]
    cut_text = " ".join(text[:101])
    wordcloud = WordCloud(
        font_path='C:/Windows/Fonts/msyh.ttc',
        background_color="white",mask=bg).generate(cut_text)
    img_color = ImageColorGenerator(bg)
    plt.imshow(wordcloud.recolor(color_func=img_color), interpolation="bilinear")
    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    word_cloud()