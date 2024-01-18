import ifcopenshell
import ifcopenshell.util.element as Element
import ifcopenshell.api
import streamlit as st
import pandas as pd
import math
import numpy as np
import io
import qrcode
from PIL import Image
from reportlab.pdfgen import canvas
from io import BytesIO
import os
from fpdf import FPDF
import tempfile
from reportlab.lib.pagesizes import letter  
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime  #thư viện datetime
import re
import pytz
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
from st_aggrid.shared import ColumnsAutoSizeMode

def createList(n):
    list = []
    for i in range(1,n + 1):
        list.append(i)
    return list
#################################################################
# text đổi màu
def change_color(text):
    # Tìm chuỗi con từ 'G' đến '@C'
    start_index = text.find('G') + 1 
    end_index = text.find('@w0')

    if start_index != -1 and end_index != -1:
        # Thay đổi màu của chuỗi con
        colored_text = f'<span style="color: red;">{text[start_index:end_index]}</span>'
        # Thay thế chuỗi con gốc bằng chuỗi con đã đổi màu
        new_text = text[:start_index] + colored_text + text[end_index:]
        return new_text
    else:
        return text
##################################################################
def process_input_string(input_string):
    # Tìm tất cả các chuỗi từ "G" đến "w0" trong input_string
    matches = re.findall(r'G(.*?)w0', input_string)
    l_values = []
    w_values = []
    w_values_after_change = []

    for match in matches:
        data = re.findall(r'l(\d+)|w(-?\d+)', match)
        for item in data:
            if item[0]:  # Nếu là số sau "l"
                l_values.append(int(item[0]))
            elif item[1]:  # Nếu là số sau "w"
                w_value = int(item[1])
                w_values.append(w_value)
                if w_value < 0:
                    new_w_value = abs(w_value)
                else:
                    new_w_value = -w_value
                w_values_after_change.append(new_w_value)

    # Kiểm tra giá trị cuối cùng của "w" và chỉ đổi dấu nếu nó là số âm
    if len(w_values_after_change) == 0: #nếu w không có
        print("")
    elif w_values_after_change[-1] < 0:
        w_values_after_change = [-w for w in w_values_after_change]
    # Đảo ngược giá trị của các số "l"
    reversed_l_values = list(reversed(l_values))
    # Đảo ngược giá trị của các số "w" và in ra sau khi đã đổi dấu
    reversed_w_values = list(reversed(w_values_after_change))
    new_matches = []
    for match in matches:
        match = re.sub(r'l(\d+)', lambda x: f'l{reversed_l_values.pop(0)}', match)
        match = re.sub(r'w(-?\d+)', lambda x: f'w{reversed_w_values.pop(0)}', match)
        new_matches.append(match)
    # In ra chuỗi mới
    if "PtSEGOPT;o0;o1;o1;o0;o0@" in input_string:
        new_input_string = 'G' + 'w0'.join(new_matches) + 'w0@PtSEGOPT;o0;o1;o1;o0;o0'
    else:
        new_input_string = 'G' + 'w0'.join(new_matches) + 'w0'
    start_index = input_string.find('G')
    end_index = input_string.find('@C')  # Để bao gồm cả '@C'
    # Tạo chuỗi mới bằng cách kết hợp các phần của input_string và new_code
    new_input_string1 = input_string[:start_index] + new_input_string + input_string[end_index:]
    # Tìm vị trí của ký tự "C" trong chuỗi
    index_of_c = new_input_string1.index('C')
    # Lấy chuỗi từ trái sang phải đến ký tự "C" bằng cách sử dụng cắt chuỗi
    substring = new_input_string1[:index_of_c + 1]
    # Tính tổng giá trị ASCII của từng ký tự trong chuỗi
    ascii_sum = sum(ord(char) for char in substring)
    IP = 96 - (ascii_sum % 32)
    start_index = new_input_string1.find('C')
    end_index = new_input_string1.find(r'C(\d+)')  # Để bao gồm cả '@C'
    # Tạo chuỗi mới bằng cách kết hợp các phần của input_string và new_code
    new_input_string2 = new_input_string1[:start_index] + "C" + str(IP) + new_input_string1[end_index:]
    return new_input_string2
###########################################################################################
code_string3 = """
p.drawString(14 * 28.3465, (y1 + 1.52) * 28.3465 , '1') #l1.rjust(5)
p.drawString(14.5 * 28.3465, (y1 + 1.52) * 28.3465 , '2') #l4.center(6)
p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , '3') #

p.drawString(14.5 * 28.3465, (y1 + 1.1) * 28.3465 , '4') #l4.center(6)
p.drawString(14.5 * 28.3465, (y1 + 0.65) * 28.3465 , '5') #l4.center(6)

p.drawString(14 * 28.3465, (y1 + 0.15) * 28.3465 , '6') #1.rjust(5)
p.drawString(14.5 * 28.3465, (y1 + 0.15) * 28.3465 , '7') #l4.center(6)
p.drawString(15 * 28.3465, (y1 + 0.15) * 28.3465 , '8') #

p.drawString(13.8 * 28.3465, (y1 + 1.02) * 28.3465 , '9') #1.rjust(5)

p.drawString(15.2 * 28.3465, (y1 + 1.02) * 28.3465 , '0') #1.rjust(5)

p.drawString(13.3 * 28.3465, (y1 + 1.23) * 28.3465 , '1.') #1.rjust(5)
p.drawString(13.3 * 28.3465, (y1 + 0.8) * 28.3465 , '2.') #1.rjust(5)
p.drawString(13.3 * 28.3465, (y1 + 0.41) * 28.3465 , '3.') #1.rjust(5)

p.drawString(15.7 * 28.3465, (y1 + 1.23) * 28.3465 , '4.') #
p.drawString(15.7 * 28.3465, (y1 + 0.8) * 28.3465 , '5.') #
p.drawString(15.7 * 28.3465, (y1 + 0.41) * 28.3465 , '6.') #
"""
#######################################################################################
code_string2 = """
for x_cm, y_cm, width_cm, height_cm in rectangles1:
    # Chèn hình ảnh vào hình chữ nhật tại tọa độ và điều chỉnh kích thước
    p.setLineWidth(border_width1)
    p.drawImage(img_path, (12.6 + 0.95) * 28.3465  , (y1 + 0.43) * 28.3465  , new_width, new_height, preserveAspectRatio=True)
    # Vẽ các hình chữ nhật khác
    p.rect(x_cm * 28.3465, y1 * 28.3465, width_cm * 28.3465, height_cm * 28.3465)
    p.setFont('msmincho.ttc', 16) 
    # Vẽ văn bản tiếng Nhật và tiếng Anh với kích thước font khác nhau
    p.drawCentredString(1.6 * 28.3465, (y1 + 0.7) * 28.3465 , (f'No.{NO1}'))  #1
    p.drawCentredString(3.6 * 28.3465, (y1 + 0.7) * 28.3465 , ("D" + result['d']))  #2 
    p.drawCentredString(5.6 * 28.3465, (y1 + 0.7) * 28.3465 , (result['l']))  #3 
    p.drawCentredString(7.6 * 28.3465, (y1 + 0.7) * 28.3465 , (result['n']))  #4 
    p.drawCentredString(9.65 * 28.3465, (y1 + 0.7) * 28.3465 , "")  #5 
    p.drawCentredString(11.65 * 28.3465, (y1 + 0.7) * 28.3465 , ("SD" + 数量1[0]))  #6 
    p.drawCentredString(17.47 * 28.3465, (y1 + 0.7) * 28.3465 , (result['s']))  #8 
    p.drawCentredString(19.35 * 28.3465, (y1 + 0.7) * 28.3465 , ee1)   #9 
"""
#########_PDF2_###############
code_string1 = """
for x_cm, y_cm, width_cm, height_cm in rectangles: 
    p.setLineWidth(border_width1)
    p.rect(x_cm * 28.3465, y_cm * 28.3465, width_cm * 28.3465, height_cm * 28.3465) 
    p.setFont('msmincho.ttc', 20)
    p.drawString(9.3 * 28.3465, 28.7 * 28.3465, "> 加工帳 <")  # 
    y2 = 27.2
    p.setFont('msmincho.ttc', 10)
    AM = 'AM'
    PM = 'PM'
    x_text44 = (0.7 * 28.3465)
    y_text44 = (28.1 * 28.3465)
    p.setFont('msmincho.ttc', 12)
    p.drawString(0.7 * 28.3465, 28.9 * 28.3465, f"工事名: {text11}")    #f"工事名: {text11}"
    p.drawString(x_text44, y_text44, f"使用場所: {text44}    運搬日: {text55} {text66}")  #f"使用場所: {text44}"
    p.drawRightString(20.3 * 28.3465, 28.1 * 28.3465, f"協力会社: {text22}") #ナイトウ建商
    
    # In ngày tháng năm hiện tại
    # Thiết lập múi giờ
    desired_timezone = 'Asia/Tokyo'
    # Tạo đối tượng múi giờ
    desired_tz = pytz.timezone(desired_timezone)
    # Lấy thời gian hiện tại theo múi giờ đã thiết lập
    current_time = datetime.now(desired_tz)
    # Định dạng và hiển thị thời gian
    formatted_time = current_time.strftime("%Y/%m/%d")
    #p.drawString(13.2 * 28.3465, 28.9 * 28.3465, f"作成日: {formatted_time}")

    so_hang = len(dfsnet['BVBS'])
    KK = so_hang / 14
    if KK % 2 == 0:
        p.drawRightString(20.3 * 28.3465, 28.9 * 28.3465, f"作成日: {formatted_time}" "   " f"ページ: {K}/{int(KK)}")
    elif KK < 1:
        p.drawRightString(20.3 * 28.3465, 28.9 * 28.3465, f"作成日: {formatted_time}" "   " f"ページ: {K}")
    elif KK > 1:
        KK += 1
        p.drawRightString(20.3 * 28.3465, 28.9 * 28.3465, f"作成日: {formatted_time}" "   " f"ページ: {K}/{int(KK)}")

    p.setFont('msmincho.ttc', 16)
    p.drawString(1 * 28.3465, y2 * 28.3465, "番号")     # 1
    p.drawString(3 * 28.3465, y2 * 28.3465, "直径")     # 2
    p.drawString(5 * 28.3465, y2 * 28.3465, "切寸")     # 3
    p.drawString(7 * 28.3465, y2 * 28.3465, "数量")     # 4
    p.drawString(9 * 28.3465, y2 * 28.3465, "定尺")     # 5
    p.drawString(11 * 28.3465, y2 * 28.3465, "鋼種")    # 6
    p.drawString(13.8 * 28.3465, y2 * 28.3465, "加工図")  # 7
    p.drawString(16.9 * 28.3465, y2 * 28.3465, "ピン")    # 8
    p.drawString(18.8 * 28.3465, y2 * 28.3465, "重量")    # 9
"""
##############################################################################
# Đặt toàn bộ mã lệnh vào một biến (ví dụ: code_string)
code_string = """
img = PILImage.open(img_path)
img_width, img_height = img.size
aspect_ratio = img_height / img_width
img_width = 100  # Chiều rộng hình ảnh trong hình chữ nhật (chỉnh sửa tùy ý)
img_height = img_width * aspect_ratio
img_x_position = rect_x_position + rect_width / 2 - img_width / 1.09
img_y_position = rect_y_position + rect_height / 1.92 - img_height / 1.1
c.drawImage(ImageReader(img), img_x_position, img_y_position, width=img_width, height=img_height)

# Thêm văn bản vào
c.setFont('msmincho.ttc', 10)
c.drawString(rect_x_position + 110, rect_y_position + 134, 'mm'.rjust(5))
c.drawString(rect_x_position + 165, rect_y_position + 132, '本'.rjust(5))
if result['s'] == "":
    c.drawString(rect_x_position + 210, rect_y_position + 128, '')
else:
    c.drawString(rect_x_position + 210, rect_y_position + 128, 'ピン＝')
c.setFont('msmincho.ttc', 14)
c.drawString(rect_x_position + 110, rect_y_position + 8, "SD" + str(数量1[0]))

c.setFont('msmincho.ttc', 16)
c.drawString(rect_x_position + 15, rect_y_position + 120, "D" + result['d'])
c.drawRightString(rect_x_position + 125, rect_y_position + 120, result['l'])
c.drawRightString(rect_x_position + 187, rect_y_position + 120, result['n'])

c.setFont('msmincho.ttc', 10)
c.drawString(rect_x_position + 243, rect_y_position + 128, result['s'])
c.setFont('msmincho.ttc', 11)
"""
###############################################################################
def process_data1(value001_str):
    index_of_G = value001_str.find('G')
    index_of_C = value001_str.find('C', index_of_G)

    if index_of_G == -1:
        print("Không tìm thấy ký tự 'G' trong chuỗi.")
        return (None, None, None, None, None, None)
    elif index_of_C == -1:
        print("Không tìm thấy ký tự 'C' trong chuỗi sau ký tự 'G'.")
        return (None, None, None, None, None, None)
    
    substring = value001_str[index_of_G + 1:index_of_C]
    w_numbers = []

    current_w_number = ""
    found_w = False

    for char in substring:
        if char == 'w':
            found_w = True
        elif found_w:
            if char.isdigit() or char == '-':
                current_w_number += char
            else:
                if current_w_number:
                    w_numbers.append(current_w_number)
                    current_w_number = ""
                found_w = False

    if current_w_number:
        w_numbers.append(current_w_number)

    w_numbers.extend([None] * (7 - len(w_numbers)))
    return tuple(w_numbers[:7])

########################################################################
def process_data(value001_str):
    # Tìm vị trí của 'G' trong chuỗi
    index_of_G = value001_str.find('G')
    index_of_C = value001_str.find('C', index_of_G)

    if index_of_G == -1:
        print("Không tìm thấy ký tự 'l' trong chuỗi.")
        return (None, None, None, None, None, None)
    elif index_of_C == -1:
        print("Không tìm thấy ký tự 'l' trong chuỗi sau ký tự 'l'.")
        return (None, None, None, None, None, None)
    
    substring = value001_str[index_of_G + 1:index_of_C]
    l_numbers = []

    current_l_number = ""
    found_l = False

    for char in substring:
        if char == 'l':
            found_l = True
        elif found_l:
            if char.isdigit() or char == '-':
                current_l_number += char
            else:
                if current_l_number:
                    l_numbers.append(current_l_number)
                    current_l_number = ""
                found_l = False

    if current_l_number:
        l_numbers.append(current_l_number)

    l_numbers.extend([None] * (7 - len(l_numbers)))
    return tuple(l_numbers[:7])
   
########################################################
def extract_numbers(value001_str):
    # Tìm vị trí của ký tự 'G' trong chuỗi
    index_of_G = value001_str.find('G')

    # Kiểm tra nếu 'G' không tồn tại trong chuỗi
    if index_of_G == -1:
        print("Không tìm thấy ký tự 'G' trong chuỗi.")
        return None

    # Lấy chuỗi từ đầu đến 'G'
    substring = value001_str[:index_of_G]

    # Khởi tạo các biến để lưu số sau khi gặp 'l', 'n', 'd', 's'
    l_number = ""
    n_number = ""
    d_number = ""
    s_number = ""

    # Biến để xác định khi nào ta gặp các ký tự 'l', 'n', 'd', 's'
    found_l = False
    found_n = False
    found_d = False
    found_s = False

    # Duyệt qua chuỗi từ đầu đến 'G' để tìm các số sau khi gặp 'l', 'n', 'd', 's'
    for char in substring:
        if char == 'l':
            found_l = True
        elif char == 'n':
            found_n = True
        elif char == 'd':
            found_d = True
        elif char == 's':
            found_s = True
        elif char.isdigit():
            if found_l:
                l_number += char
            elif found_n:
                n_number += char
            elif found_d:
                d_number += char
            elif found_s:
                s_number += char
        else:
            # Nếu gặp ký tự khác, đặt lại biến found_ để bắt đầu lấy số mới
            found_l = False
            found_n = False
            found_d = False
            found_s = False

    return {
        'l': l_number,
        'n': n_number,
        'd': d_number,
        's': s_number
    }

########################################################################
def get_objects_data_by_class(file, class_type):

    objects = file.by_type(class_type)
    objects_data = []
    pset_attributes = set()

    for object in objects:
        objects_data.append(
            {
                "Id": object.id(),
                "クラス": object.is_a(),
                "タイプ": object.Name,
                "直径": object.NominalDiameter,
                "切寸": round(object.BarLength),
            }
        )
    return objects_data, list(pset_attributes)

def get_attribute_value(object_data, attribute):
        return object_data[attribute]

def create_pandas_dataframe(data, pset_attributes):
    import pandas as pd

    ## List of Attributes
    attributes = [
        "Id",
        "クラス",
        "タイプ",
        "直径",
        "切寸",
    ]
    ## Export Data to Pandas
    pandas_data = []
    for object_data in data:
        row = []
        for attribute in attributes:
            value = get_attribute_value(object_data, attribute)
            row.append(value)
        pandas_data.append(tuple(row))
    df = pd.DataFrame.from_records(pandas_data, columns=attributes)
    df_copy = pd.DataFrame({'直径': [6, 10, 13, 16, 19, 22, 25, 29, 32, 35, 38, 41, 51],
                   'Model Bar Radius': [3.5, 5.5, 7, 9, 10.5, 12.5, 14, 16.5, 18, 20, 21.5, 23, 29]})
    dictionary = dict(zip(df_copy['直径'],df_copy['Model Bar Radius']))
    df['Model Bar Radius'] = df['直径'].map(dictionary)
    DF_sort = df.sort_values(by=['Id'])
    return DF_sort
    
def get_objects_data_by_class_1(file, class_type):
    objects_data = []
    pset_attributes = set()
    OBJECTS = file.by_type(class_type)
    for OBJECT in OBJECTS:
        object = OBJECT.Representation[2][0][3][0][0]

        objects_data.append(
            {
                "Id": object.id(),
                "IfcCompositeCurve": object,
                "CountSegments": len(object.Segments),
            }
        )
    return objects_data, list(pset_attributes)

def get_attribute_value_1(object_data, attribute):
        return object_data[attribute]

def create_pandas_dataframe_1(data, pset_attributes):
    import pandas as pd

    ## List of Attributes
    attributes = [
        "Id",
        "IfcCompositeCurve",
        "CountSegments",
    ]
    ## Export Data to Pandas
    pandas_data = []
    for object_data in data:
        row = []
        for attribute in attributes:
            value = get_attribute_value_1(object_data, attribute)
            row.append(value)
        pandas_data.append(tuple(row))
    df1 = pd.DataFrame.from_records(pandas_data, columns=attributes)
    DF_sort1 =  df1.sort_values(by=['Id'])
    return DF_sort1

def get_objects_data_by_class_2(file, class_type):
    objects_data = []
    pset_attributes = set()
    OBJECTS = file.by_type(class_type)
    for OBJECT in OBJECTS:
        objects = OBJECT.Representation[2][0][3][0][0][0]

        for object in objects:
            objects_data.append(
                {
                    "Id": object.id(),
                    "直線 Point1_x": round(object.ParentCurve[0][0][0][0],2)
                    if object.ParentCurve.is_a('IfcPolyline')
                    else 0,
                    "直線 Point1_y": round(object.ParentCurve[0][0][0][1],2)
                    if object.ParentCurve.is_a('IfcPolyline')
                    else 0,
                    "直線 Point1_z": round(object.ParentCurve[0][0][0][2],2)
                    if object.ParentCurve.is_a('IfcPolyline')
                    else 0,
                    "直線 Point2_x": round(object.ParentCurve[0][1][0][0],2)
                    if object.ParentCurve.is_a('IfcPolyline')
                    else 0,
                    "直線 Point2_y": round(object.ParentCurve[0][1][0][1],2)
                    if object.ParentCurve.is_a('IfcPolyline')
                    else 0,
                    "直線 Point2_z": round(object.ParentCurve[0][1][0][2],2)
                    if object.ParentCurve.is_a('IfcPolyline')
                    else 0,
                    "曲線 Center_x": round(object.ParentCurve[0][0][0][0][0],2)
                    if object.ParentCurve.is_a('IfcTrimmedCurve')
                    else 0,
                    "曲線 Center_y": round(object.ParentCurve[0][0][0][0][1],2)
                    if object.ParentCurve.is_a('IfcTrimmedCurve')
                    else 0,
                    "曲線 Center_z": round(object.ParentCurve[0][0][0][0][2],2)
                    if object.ParentCurve.is_a('IfcTrimmedCurve')
                    else 0,
                    "曲線 半径": round(object.ParentCurve[0][1],1)
                    if object.ParentCurve.is_a('IfcTrimmedCurve')
                    else 0,
                    "曲げ角度w1": round(object.ParentCurve[1][0][0])
                    if object.ParentCurve.is_a('IfcTrimmedCurve')
                    else 0,
                    "曲げ角度w2": round(object.ParentCurve[2][0][0])
                    if object.ParentCurve.is_a('IfcTrimmedCurve')
                    else 0,
                    "w2-w1(1)": round(abs(object.ParentCurve[2][0][0] - object.ParentCurve[1][0][0]))
                    if object.ParentCurve.is_a('IfcTrimmedCurve') and round(abs(object.ParentCurve[2][0][0] - object.ParentCurve[1][0][0]))<=180
                    else 0,
                    "w2-w1(2)": round(360-abs(object.ParentCurve[2][0][0] - object.ParentCurve[1][0][0]))
                    if object.ParentCurve.is_a('IfcTrimmedCurve') and round(abs(object.ParentCurve[2][0][0] - object.ParentCurve[1][0][0]))>180
                    else 0,
                }
            )
    return objects_data, list(pset_attributes)

def get_attribute_value_2(object_data, attribute):
        return object_data[attribute]

def create_pandas_dataframe_2(data, pset_attributes):
    import pandas as pd

    ## List of Attributes
    attributes = [
        "Id",
        "直線 Point1_x",
        "直線 Point1_y",
        "直線 Point1_z",
        "直線 Point2_x",
        "直線 Point2_y",
        "直線 Point2_z",
        "曲線 Center_x",
        "曲線 Center_y",
        "曲線 Center_z",
        "曲線 半径",
        "曲げ角度w1",
        "曲げ角度w2",
        "w2-w1(1)",
        "w2-w1(2)",
    ]
    ## Export Data to Pandas
    pandas_data = []
    for object_data in data:
        row = []
        for attribute in attributes:
            value = get_attribute_value_2(object_data, attribute)
            row.append(value)
        pandas_data.append(tuple(row))
        df2 = pd.DataFrame.from_records(pandas_data, columns=attributes)
        DF_sort2 =  df2.sort_values(by=['Id'])
    return DF_sort2


def callback_upload():
    if st.session_state.uploaded_file is not None:
        session["file_name"] = session["uploaded_file"].name
        session["array_buffer"] = session["uploaded_file"].getvalue()
        session["ifc_file"] = ifcopenshell.file.from_string(session["array_buffer"].decode("utf-8"))
        session["is_file_loaded"] = True
        session["DataFrame"] = None
        session["DataFrame_1"] = None
        session["DataFrame_2"] = None
        session["IsDataFrameLoaded"] = False

def initialize_session_state():
    session["DataFrame"] = None
    session["Classes"] = []
    session["IsDataFrameLoaded"] = False

def load_data():
    if "ifc_file" in session:
        session["DataFrame"] = get_ifc_pandas()
        session["DataFrame_1"] = get_ifc_pandas_1()
        session["DataFrame_2"] = get_ifc_pandas_2()
        session["IsDataFrameLoaded"] = True

def get_ifc_pandas():
    data, pset_attributes = get_objects_data_by_class(
        session.ifc_file,
        "IfcReinforcingBar"
    )
    return create_pandas_dataframe(data, pset_attributes)

def get_ifc_pandas_1():
    data, pset_attributes = get_objects_data_by_class_1(
        session.ifc_file,
        "IfcReinforcingBar"
    )
    return create_pandas_dataframe_1(data, pset_attributes)

def get_ifc_pandas_2():
    data, pset_attributes = get_objects_data_by_class_2(
        session.ifc_file,
        "IfcReinforcingBar"
    )
    return create_pandas_dataframe_2(data, pset_attributes)
def download_excel(dataframe):
    return dataframe

def download_excel(file_name):
    file_name = file_name.replace('.ifc', '.xlsx')
    return file_name

def download_bvbs(dataframe):
    return dataframe

def download_bvbs(file_name):
    file_name = file_name.replace('.ifc', '.abs')
    return file_name

############################################################################################

def main():
    
    st.set_page_config(
    layout= "wide",
    page_title="DBAS ZERO v1.0",
    page_icon="🌐",
    #initial_sidebar_state="expanded",
    ) 
    #st.title("DBAS ZERO ➡ BIM データ IFCファイル連携")
    st.markdown("<h1 style='text-align: center;'>鉄筋BIMモデルを自動加工機へデータ連携</h1>", unsafe_allow_html=True)
    st.write("")
    #st.sidebar.write("")
    ## Add File uploader
    st.header('モデルのアップロード')
    st.file_uploader("IFCデータを選択してください", type=['ifc'], key="uploaded_file", on_change=callback_upload)
##############################################################################################
    if not "IsDataFrameLoaded" in session:
        initialize_session_state()
    if not session.IsDataFrameLoaded:
        load_data()
    if session.IsDataFrameLoaded:  
        
            ## DATAFRAME REVIEW           

            ## DATAFRAME REVIEW            
            df_1 = download_excel(session.DataFrame_1)
            buf = io.BytesIO()
            df_1.to_excel(buf, index=False, header=True)
            file_name_1 = download_excel(session.file_name)

            ## DATAFRAME REVIEW            
            df_2 = download_excel(session.DataFrame_2)
            buf = io.BytesIO()
            df_2.to_excel(buf, index=False, header=True)
            file_name_2 = download_excel(session.file_name)
            df_2_length = np.sqrt((df_2['直線 Point1_x']-df_2['直線 Point2_x'])**2+(df_2['直線 Point1_y']-df_2['直線 Point2_y'])**2+(df_2['直線 Point1_z']-df_2['直線 Point2_z'])**2)
            df_2_w2w1=df_2['w2-w1(1)']+df_2['w2-w1(2)']
            df_sort = download_excel(session.DataFrame)
            DF=df_sort['Model Bar Radius']
            DF_kei=df_sort['直径']
            DF_length=df_sort['切寸']
            DF_type=df_sort['タイプ'] #memno
            df_r=DF.loc[DF.index.repeat(df_1.CountSegments)].reset_index(drop=True)
            df_2.loc[:, 'INDEX'] = df_2.index
            df_2.reset_index(inplace = True, drop = True)
            df_2['R'] = df_r
            df_2['PLUS']= df_2['R']+df_2['曲線 半径']
            df_2['DIAMETER']= (df_2['曲線 半径'] - df_2['R'])*2
            df_2 = df_2.set_index('INDEX')
            df_kei=DF_kei.loc[DF.index.repeat(df_1.CountSegments)].reset_index(drop=True)
            df_length=DF_length.loc[DF.index.repeat(df_1.CountSegments)].reset_index(drop=True)
            df_type=DF_type.loc[DF.index.repeat(df_1.CountSegments)].reset_index(drop=True) #memno
            df_dropcol1=df_2.drop(['Id','曲線 Center_x','曲線 Center_y','曲線 Center_z','曲線 半径','曲げ角度w1','曲げ角度w2','w2-w1(1)','w2-w1(2)'], axis=1)
            df_dropcol2=df_2.drop(['Id','直線 Point1_x','直線 Point1_y','直線 Point1_z','直線 Point2_x','直線 Point2_y','直線 Point2_z','曲線 半径','曲げ角度w1','曲げ角度w2','w2-w1(1)','w2-w1(2)'], axis=1)
            df_downrow1=df_dropcol1.shift(periods=1, fill_value=0)
            df_downrow2=df_dropcol2.shift(periods=2, fill_value=0)
            df_downrow3=df_dropcol1.shift(periods=3, fill_value=0)
            df_downrow6=df_dropcol2.shift(periods=6, fill_value=0)
            df_2.loc[round(abs(np.sqrt((df_2['曲線 Center_x']-df_downrow2['曲線 Center_x'])**2+(df_2['曲線 Center_y']-df_downrow2['曲線 Center_y'])**2+(df_2['曲線 Center_z']-df_downrow2['曲線 Center_z'])**2))) == round(abs(np.sqrt((df_downrow1['直線 Point1_x']-df_downrow1['直線 Point2_x'])**2+(df_downrow1['直線 Point1_y']-df_downrow1['直線 Point2_y'])**2+(df_downrow1['直線 Point1_z']-df_downrow1['直線 Point2_z'])**2))), 'check1']= "True"
            df_2.loc[round(abs(np.sqrt((df_2['曲線 Center_x']-df_downrow2['曲線 Center_x'])**2+(df_2['曲線 Center_y']-df_downrow2['曲線 Center_y'])**2+(df_2['曲線 Center_z']-df_downrow2['曲線 Center_z'])**2))) != round(abs(np.sqrt((df_downrow1['直線 Point1_x']-df_downrow1['直線 Point2_x'])**2+(df_downrow1['直線 Point1_y']-df_downrow1['直線 Point2_y'])**2+(df_downrow1['直線 Point1_z']-df_downrow1['直線 Point2_z'])**2))), 'check1']= "False"  
            df_2.loc[round(abs(np.sqrt((df_downrow1['直線 Point1_x']-df_downrow1['直線 Point2_x'])**2+(df_downrow1['直線 Point1_y']-df_downrow1['直線 Point2_y'])**2+(df_downrow1['直線 Point1_z']-df_downrow1['直線 Point2_z'])**2+((2*df_2['曲線 半径'])**2))),1) != round(abs(np.sqrt((df_2['曲線 Center_x']-df_downrow2['曲線 Center_x'])**2+(df_2['曲線 Center_y']-df_downrow2['曲線 Center_y'])**2+(df_2['曲線 Center_z']-df_downrow2['曲線 Center_z'])**2)),1), 'check3d']= "True"
            df_2.loc[round(abs(np.sqrt((df_downrow1['直線 Point1_x']-df_downrow1['直線 Point2_x'])**2+(df_downrow1['直線 Point1_y']-df_downrow1['直線 Point2_y'])**2+(df_downrow1['直線 Point1_z']-df_downrow1['直線 Point2_z'])**2+((2*df_2['曲線 半径'])**2))),1) == round(abs(np.sqrt((df_2['曲線 Center_x']-df_downrow2['曲線 Center_x'])**2+(df_2['曲線 Center_y']-df_downrow2['曲線 Center_y'])**2+(df_2['曲線 Center_z']-df_downrow2['曲線 Center_z'])**2)),1), 'check3d']= "False"
            df_2['check3D']=round(abs(np.sqrt((df_2['曲線 Center_x']-df_downrow6['曲線 Center_x'])**2+(df_2['曲線 Center_y']-df_downrow6['曲線 Center_y'])**2+(df_2['曲線 Center_z']-df_downrow6['曲線 Center_z'])**2)-np.sqrt((df_downrow3['直線 Point1_x']-df_downrow3['直線 Point2_x'])**2+(df_downrow3['直線 Point1_y']-df_downrow3['直線 Point2_y'])**2+(df_downrow3['直線 Point1_z']-df_downrow3['直線 Point2_z'])**2)-2*df_2['曲線 半径']))
            df_2.loc[df_2['曲線 半径'] != 0, 'check1'] = df_2['check1']
            df_2.loc[df_2['曲線 半径'] != 0, 'check3d'] = df_2['check3d']
            df_2.loc[df_2['曲線 半径'] != 0, 'check3D'] = df_2['check3D']
            df_2.loc[df_2['曲線 半径'] == 0, 'check1'] = ""
            df_2.loc[df_2['曲線 半径'] == 0, 'check3d'] = ""
            df_2.loc[df_2['曲線 半径'] == 0, 'check3D'] = ""
            df_2.loc[:, 'check4'] = df_2_w2w1
            df_2.loc[df_2['check1'] =="", 'check4'] = 0
            df_2.loc[:, 'index'] = df_2.index
            df_2.reset_index(inplace = True, drop = True)
            for i in range(2,len(df_2)):
                df_2.at[i,'check4'] = df_2.at[i,'check4'] if ((df_2.at[i-2,'check4'] ==0) or(df_2.at[i,'check1'] == "True" and df_2.at[i-2,'check4'] >0) or (df_2.at[i,'check1'] == "False" and df_2.at[i-2,'check4'] <0)) else 0 - df_2.at[i,'check4']
            df_2 = df_2.set_index('index')
            df_downrow4=df_2.shift(periods=4, fill_value=0)
            df_downrow222=df_2.shift(periods=-2, fill_value=0)
            df_downrow444=df_2.shift(periods=-4, fill_value=0)
            df_downrow666=df_2.shift(periods=-6, fill_value=0)
            df_2.loc[(df_2['check1'] == "False") & (df_2['check3d'] == "True") & (df_2['check3D'] != 0) & (df_downrow4['check4'] == 0) & (df_2['check4'] == -90) & (df_downrow222['check4'] == -90) & (df_downrow444['check4'] == 90) & (df_downrow666['check4'] == 0), 'check4'] = df_2['check4'].astype(str) + "(3D)"
            df_downrow44=df_2.shift(periods=4, fill_value=0)
            df_2.loc[(df_2['check1'] == "False") & (df_2['check3d'] == "True") & (df_2['check3D'] == 0) & (df_downrow44['check4'] == "-90(3D)") & (df_2['check4'] == 90), 'check4'] = df_2['check4'].astype(str) + "(3D)"
            df_2.loc[(df_2['check1'] == "False") & (df_2['check3d'] == "True") & (df_2['check3D'] != 0) & (df_downrow44['check4'] == "-90(3D)") & (df_2['check4'] == 90), 'check4'] = df_2['check4'].astype(str) + "(3d)"
            df_downrow2top=df_2.shift(periods=2, fill_value=0)
            df_downrow2bottom=df_2.shift(periods=-2, fill_value=0)
            df_2.loc[((df_downrow2top['check4'] == "-90(3D)") & (df_downrow2bottom['check4'] == "90(3D)")) | ((df_downrow2top['check4'] == "-90(3D)") & (df_downrow2bottom['check4'] == "90(3d)")), 'check4'] = "90"
            df_2.loc[df_2['check4'] == "90(3D)", 'check4'] = "90"
            df_2.loc[df_2['check4'] == "90(3d)", 'check4'] = "-90"
            df_2.loc[df_2['check4'] == "-90(3D)", 'check4'] = "90threeD"
            df_2.loc[df_2['check4'] == 0, 'check4'] = ""
            df_2.loc[(180-df_2_w2w1>90), 'plus'] = df_2['PLUS']/(np.tan(np.radians(90-df_2_w2w1/2)))
            df_2.loc[(180-df_2_w2w1<=90), 'plus'] = df_2['PLUS']
            df_2.loc[df_2_w2w1==00, 'plus'] = 0
            shif_1= df_2['plus'].shift(periods=1, fill_value=0)
            shif_2= df_2['plus'].shift(periods=-1, fill_value=0)
            df_2.loc[:, 'LENGTH'] = round(df_2_length+shif_1+shif_2)
            df_2.loc[:, 'length'] = round(df_2_length+shif_1+shif_2)

            #st.write("------------------------------------------------------")
            st.subheader(' ', divider='rainbow')
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.header("集計表")

            with col2:
                with st.expander("丸めの設定"):
                    marume_ON = st.toggle('丸め ON/OFF')
                    if marume_ON:
                        col2_1, col2_2 = st.columns(2)
                        with col2_1:
                            marume_mm = st.radio("丸め単位",["5mm", "10mm"],index=None)
                        with col2_2:
                            marume_type = st.radio("丸め種類",["切り捨て", "切り上げ", "四捨五入"],index=None)
                        if marume_ON and marume_type == "四捨五入" and marume_mm == "5mm":
                            df_2['length'] = ((df_2['LENGTH']*2).round(-1))/2
                            st.success('丸め単位 : 5mm , 丸め種類 : 四捨五入 を設定しました。')
                            st.write('例 :  1823 :arrow_right: 1825')
                        elif marume_ON and marume_type == "切り捨て" and marume_mm == "5mm":
                            df_2['length'] = (((df_2['LENGTH']*2)//10)*10)/2
                            st.success('丸め単位 : 5mm , 丸め種類 : 切り捨て を設定しました。')
                            st.write('例 :  1823 :arrow_right: 1820')
                        elif marume_ON and marume_type == "切り上げ" and marume_mm == "5mm":
                            df_2['length'] = ((((df_2['LENGTH']*2) / 10).apply(np.ceil)) * 10)/2
                            st.success('丸め単位 : 5mm , 丸め種類 : 切り上げ を設定しました。')
                            st.write('例 :  1823 :arrow_right: 1825')
                        elif marume_ON and marume_type == "四捨五入" and marume_mm == "10mm":
                            df_2['length'] = df_2['LENGTH'].round(-1)
                            st.success('丸め単位 : 10mm , 丸め種類 : 四捨五入 を設定しました。')
                            st.write('例 :  1823 :arrow_right: 1820')
                        elif marume_ON and marume_type == "切り捨て" and marume_mm == "10mm":
                            df_2['length'] = df_2['LENGTH']//10*10
                            st.success('丸め単位 : 10mm , 丸め種類 : 切り捨て を設定しました。')
                            st.write('例 :  1823 :arrow_right: 1820')
                        elif marume_ON and marume_type == "切り上げ" and marume_mm == "10mm":
                            df_2['length'] = (df_2['LENGTH'] / 10).apply(np.ceil) * 10
                            st.success('丸め単位 : 10mm , 丸め種類 : 切り上げ を設定しました。')
                            st.write('例 :  1823 :arrow_right: 1830')

            with col3:
                with st.expander("セルの編集モードの設定"):
                    edit_ON = st.toggle('セルのロックを解除する')
                    if edit_ON:
                        st.success('集計表のセールが編集できるようになりました。')
                    else: 
                        st.write('デフォルト : セルの編集が不可能の状態になっています。')
            df_2.loc[df_2['length']==0, 'l and w'] = '@w'+df_2['check4'].astype(str).str.replace('.0', '', regex=False)+'@'
            df_2.loc[df_2['length']!=0, 'l and w'] = 'l'+df_2['length'].astype(str).str.replace('.0', '', regex=False)
            df_2.loc[df_2['LENGTH']==0, 'L AND W'] = '@w'+df_2['check4'].astype(str).str.replace('.0', '', regex=False)+'@'
            df_2.loc[df_2['LENGTH']!=0, 'L AND W'] = 'l'+df_2['LENGTH'].astype(str).str.replace('.0', '', regex=False)
            shif_s= df_2['曲線 半径'].shift(periods=-2, fill_value=0)
            df_2.loc[:, 'help s'] = shif_s
            df_2.loc[(df_2_w2w1!=0) & (df_2['help s']==0) , 's'] = df_2['DIAMETER'].astype(str).str.replace('.0', '', regex=False)
            df_2.loc[(df_2_w2w1!=0) & (df_2['help s']!=0) , 's'] = ""
            df_2.loc[df_2_w2w1==0, 's'] = ""
            df_help = df_1.loc[df_1.index.repeat(df_1.CountSegments)].reset_index(drop=True)
            df_2.reset_index(inplace = True, drop = True)
            df_2.loc[:, 'help id'] = df_help['Id']
            df_2.loc[:, '直径'] = df_kei
            df_2.loc[:, '切寸'] = df_length
            df_2.loc[:, 'タイプ'] = df_type #memno
            df_concate=df_2.groupby(['help id','直径','切寸','タイプ'], sort=False)[['l and w','s']].agg(''.join).reset_index() #memno
            df_CONCATE=df_2.groupby(['help id','直径','切寸','タイプ'], sort=False)[['L AND W','s']].agg(''.join).reset_index() #memno
            df_last=df_concate.groupby(['直径','切寸','タイプ','l and w','s'])['l and w'].size().reset_index(name='数量') #memno
            df_LAST=df_CONCATE.groupby(['直径','切寸','タイプ','L AND W','s'])['L AND W'].size().reset_index(name='数量') #memno
            df_last_copy1 = pd.DataFrame({'鉄筋': [6, 10, 13, 16, 19,22,25,29,32,35,38,41,51],
                   'kg per m': [0.249, 0.56, 0.995, 1.56, 2.25, 3.04, 3.98, 5.04, 6.23, 7.51, 8.95, 10.5, 15.9]})
            dictionary1 = dict(zip(df_last_copy1['鉄筋'],df_last_copy1['kg per m']))
            df_last['重量(kg)'] = round(df_last['数量'] * df_last['切寸'] * df_last['直径'].map(dictionary1) / 1000,2)
            df_last_copy2 = pd.DataFrame({'鉄筋': [6, 10, 13, 16, 19,22,25,29,32,35,38,41,51],
                   '材質': ['SD295','SD295','SD295','SD295','SD345','SD345','SD345','SD390','SD390','SD390','SD390','SD390','SD390']})
            dictionary2 = dict(zip(df_last_copy2['鉄筋'],df_last_copy2['材質']))
            df_last['材質'] = df_last['直径'].map(dictionary2)
            df_last['番号'] = (df_last.index + 1)
            df_last['番号'] = "No." + df_last['番号'].astype(str)
            
            df_last['private'] = "@w0@C"
            df_last.loc[df_last['l and w'].str.contains('threeD')==True, 'private'] = "@w0@PtSEGOPT;o0;o1;o1;o0;o0@C"
            df_last['count'] = df_last['l and w'].str.count("w")
            max_count = df_last['count'].max()
            max_count_plus2 = max_count + 2
            for i in range(1,max_count_plus2):
                df_last['l'+str(i)] = df_last['l and w'].str.split("l").str[i]
                df_last['l'+str(i)] = df_last['l'+str(i)].str.split("@").str[0]
                df_last['l'+str(i)].fillna(0,inplace=True)
            df_list_l = df_last.iloc[:,-(max_count+1):]
            df_list_l = df_list_l.astype(int)
            df_sum_l = df_list_l.sum(axis = 1)
            df_last.loc[:, 'sum_before'] = df_sum_l.astype(str) ###############
            df_sum_l1 = df_last['sum_before'] ###############

            for i in range(1,max_count_plus2):
                df_LAST['L'+str(i)] = df_LAST['L AND W'].str.split("l").str[i]
                df_LAST['L'+str(i)] = df_LAST['L'+str(i)].str.split("@").str[0]
                df_LAST['L'+str(i)].fillna(0,inplace=True)
            df_list_L = df_LAST.iloc[:,-(max_count+1):]
            df_list_L = df_list_L.astype(int)
            df_sum_L = df_list_L.sum(axis = 1)
            df_delta = df_sum_l - df_sum_L
            df_last['切寸'] = df_last['切寸'].astype(int) +  df_delta.astype(int)
            if marume_ON and marume_type == "四捨五入" and marume_mm == "5mm":
                df_last['切寸'] = ((df_last['切寸']*2).round(-1))/2 
            elif marume_ON and marume_type == "切り捨て" and marume_mm == "5mm":
                df_last['切寸'] = (((df_last['切寸']*2)//10)*10)/2
            elif marume_ON and marume_type == "切り上げ" and marume_mm == "5mm":
                df_last['切寸'] = ((((df_last['切寸']*2) / 10).apply(np.ceil)) * 10)/2
            elif marume_ON and marume_type == "四捨五入" and marume_mm == "10mm":
                df_last['切寸'] = df_last['切寸'].round(-1)
            elif marume_ON and marume_type == "切り捨て" and marume_mm == "10mm":
                df_last['切寸'] = df_last['切寸']//10*10
            elif marume_ON and marume_type == "切り上げ" and marume_mm == "10mm":
                df_last['切寸'] = (df_last['切寸'] / 10).apply(np.ceil) * 10
            df_last['切寸helper'] = df_last['切寸']
            df_last['径'] = "D"+df_last['直径'].astype(str).str.replace('.0', '', regex=False)
            df_last['タイプ'] = df_last['タイプ'].str.replace('Rebar Bar:', '', regex=False) #memno
            df_table0 = df_last.loc[:, ["番号","タイプ","径","切寸","切寸helper","数量","材質","重量(kg)","s","l and w","private"]] #memno
            left_part = df_table0.iloc[:, :3]
            right_part = df_table0.iloc[:, 3:]
            df_table1 = pd.concat([left_part,right_part,df_sum_l1,df_list_l], axis=1) ###############
#############################
            ob = GridOptionsBuilder.from_dataframe(df_table1)

            ob.configure_column("番号", headerCheckboxSelection = True)

            #  Update selection.
            ob.configure_selection(selection_mode="multiple", use_checkbox=True, pre_selected_rows=createList(len(df_table1)))

            #  Update row height.
            ob.configure_grid_options(rowHeight=30)
            if edit_ON:
                ob.configure_default_column(sorteable=False,groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
            else:   ob.configure_default_column(sorteable=False,groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False)
            #  Build the options.
            grid_options = ob.build()
            column_defs = grid_options["columnDefs"]
            columns_to_hide = ["切寸helper","重量(kg)","s","l and w","private","sum_before"] ###############

            # update the column definitions to hide the specified columns
            for col in column_defs:
                if col["headerName"] in columns_to_hide:
                    col["hide"] = True

            # Add custom css to center the values
            grid_return = AgGrid(
                df_table1,
                grid_options,
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
                custom_css={'.ag-row .ag-cell': {'display': 'flex',
                                     'justify-content': 'center',
                                     'align-items': 'center'},
                            '.ag-header-cell-label': {'justify-content': 'center'}
                            }
            )
            selected_rows = grid_return["selected_rows"]
            dfs = pd.DataFrame(selected_rows)
            #st.write(dfs)
            if len(selected_rows):
                
                dfsnet = dfs.drop(columns=['_selectedRowNodeInfo'])

                dfsnet['径'] = dfsnet['径'].astype(str).str.replace('D', '', regex=False)
                #dfsnet['番号'] = dfsnet['番号'].astype(str).str.replace('No.', '', regex=False) #
                df_l_after = dfsnet.iloc[:,-(max_count+1):] ###############
                df_sum_before = dfsnet['sum_before']
                dfsnet.loc[:, 'sum_after'] = df_l_after.astype(int).sum(axis = 1)
                df_sum_after = dfsnet.loc[:, 'sum_after']
                df_DELTA = df_sum_after.astype(int) - df_sum_before.astype(int)            
                dfsnet['切寸'] = dfsnet['切寸helper'].astype(int) +  df_DELTA.astype(int)
                dfsnet['重量(kg)'] = round(dfsnet['数量'].astype(int) * dfsnet['切寸'].astype(int) * dfsnet['径'].astype(int).map(dictionary1) / 1000,2) 
                for i in range(1,max_count_plus2):
                    dfsnet['l'+str(i)+'help'] = dfsnet['l and w'].astype(str).str.split("l").str[i]
                    dfsnet['l'+str(i)+'help'] = dfsnet['l'+str(i)+'help'].astype(str).str.split("@").str[1]
                    dfsnet['l'+str(i)+'help'].fillna("",inplace=True)
                    dfsnet['l'+str(i)+'help'] = "@" + dfsnet['l'+str(i)+'help'] + "@"
                    dfsnet['l'+str(i)+'help'] = dfsnet['l'+str(i)+'help'].replace("@@","",regex=False)
                    dfsnet['l'+str(i)+'help'] = "l" + dfsnet['l'+str(i)].astype(str) + dfsnet['l'+str(i)+'help']
                    dfsnet['l'+str(i)+'help'] = dfsnet['l'+str(i)+'help'].replace("l0","", regex=False)
                df_l_help = dfsnet.iloc[:,-(max_count+1):]
                dfsnet['l and w'] = df_l_help.astype(str).values.sum(axis=1) ###############
                
                dfsnet['searchIP'] = "BF2D@Hj@r@i@p"+ (dfsnet.index+1).astype(str)+"@l"+dfsnet['切寸'].astype(str).str.replace('.0', '', regex=False)+"@n"+dfsnet['数量'].astype(str)+"@e"+dfsnet['重量(kg)'].astype(str)+"@d"+dfsnet['径'].astype(str).str.replace('.0', '', regex=False)+"@g"+dfsnet['材質']+"@s"+dfsnet['s']+"@v@a@G"+dfsnet['l and w'].str.replace('threeD', '', regex=False)+dfsnet['private']
                dfsnet['IP'] = [96-(sum([ord(ele) for ele in sub]))%32 for sub in dfsnet['searchIP']]
                dfsnet['BVBS'] = dfsnet['searchIP'] + dfsnet['IP'].astype(str) + "@"

                zz = 0
                with st.expander("鉄筋を左右反転にしたい場合は、該当箇所のチェックボックスにチェックを入れてください"):
                    for value000 in dfsnet['BVBS']:
                        zz += 1
                        is_checked = st.checkbox(f" No.{zz} : {value000}")
                        if is_checked:
                            value002 = process_input_string(value000)
                            dfsnet.at[zz - 1, 'BVBS'] = value002
                            colored_text = change_color(value002)
                            st.markdown('<span style="color: red; font-size: 15px;"> 左右反転後: </span>' + colored_text, unsafe_allow_html=True)
                col000, col111, col222, col333, col444, col555 = st.columns(6)
                ###_#Download Excel_###
                dfsnet1 = dfsnet.drop(columns=["切寸helper","重量(kg)","s","l and w","private",'searchIP','IP','BVBS','sum_before','sum_after']) ###############
                dfsnet1['番号'] = "No." + (dfsnet.index+1).astype(str)
                dfsnet1 = dfsnet1.iloc[:, :(5+max_count+1)] ###############
                dfsnet1['径'] = 'D' + dfsnet1['径']
                buf = io.BytesIO()
                dfsnet1.to_excel(buf, index=False, header=True)
                file_name_0 = download_excel(session.file_name)
                col222.download_button("Download Excel",buf.getvalue(),file_name_0,"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                ###_Download BVBS_###

                df_BVBS = dfsnet['BVBS']
                buf = io.BytesIO()
                df_BVBS.to_csv(buf, index=False, header=False)
                file_name_3 = download_bvbs(session.file_name)
                col333.download_button("Download BVBS",buf.getvalue(),file_name_3)
            
#####################################################################                                                        ##########################################################
            # Cài đặt phông chữ hỗ trợ tiếng Nhật
            pdfmetrics.registerFont(TTFont('msmincho.ttc', 'form/MSMINCHO.TTF'))  ###########################################################
                                                                                                                             ###########################################################
            # Hàm để tạo mã QR với kích thước cố định
            def create_qr_code(df_bvbs, size=100):
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(df_bvbs)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white").resize((size, size))

                # Chuyển đổi ảnh QR thành đối tượng PIL
                img_pil = PILImage.new("RGB", img.size, "white")
                img_pil.paste(img)
                
                return img_pil

            def create_pdf(bbvs_list, image_list,text11,text22,text33,text44):
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize = A4)  # Sử dụng trang giấy A4

                # Kích thước trang A4
                page_width , page_height = A4

                right_margin = 50
                # Kích thước cố định cho mã QR code và hình chữ nhật
                qr_size = 95
                rect_width = 269.3  # Chiều dài 10cm chuyển thành pixel (1 cm = 28.35 pixel)
                rect_height = 181.9  # Chiều rộng 7cm chuyển thành pixel

                # Vị trí ban đầu của mã QR code trên hình chữ nhật
                qr_x_offset = 165
                qr_y_offset = 27

                # Vị trí ban đầu của hình chữ nhật
                initial_rect_x_position = 14.175
                initial_rect_y_position = page_height - rect_height - 14.175

                # Khoảng cách giữa các hình
                x_spacing = 28.45
                y_spacing = 28.45
                
                # Đặt độ dày cho đường kẻ và đường viền (thay đổi giá trị tùy ý)
                line_width = 0.5  # Độ dày của đường kẻ
                border_width = 0.25  # Độ dày của đường viền
                
                # Vị trí hiện tại của hình chữ nhật
                rect_x_position = initial_rect_x_position
                rect_y_position = initial_rect_y_position

                # Biến để theo dõi số lượng hình đã in trên trang hiện tại
                rects_on_page = 0

                # Tạo biến NO ban đầu
                no = 1
###############################################################
                for index, row in dfsnet.iterrows():
                    value001 = row["BVBS"]
                    タイプ = row["タイプ"]
                    #st.write(value001)
                    # Sử dụng biểu thức chính quy để tìm số sau "SD" đến ký tự "@"
                    数量 = r'SD(\d+\.\d+|\d+)@'
                    # Tìm tất cả các kết quả phù hợp với biểu thức chính quy
                    数量1 = re.findall(数量 , value001)
                    qr_image = create_qr_code(value001, size=qr_size)
################################################################
                    # Vẽ hình chữ nhật trắng với đường viền đen
                    c.setLineWidth(border_width)
                    c.rect(rect_x_position, rect_y_position, rect_width, rect_height, stroke=1, fill=0)
                    # Thêm đường gạch ngang 0.5 cm từ đường viền phía trên của hình chữ nhật
                    c.setLineWidth(line_width)
                    c.line(rect_x_position, rect_y_position + rect_height - (20), rect_x_position + rect_width, rect_y_position + rect_height - (20))
                    # Thêm đường gạch ngang 1 cm từ đường viền phía trên của hình chữ nhật
                    c.line(rect_x_position, rect_y_position + rect_height - (40), rect_x_position + rect_width, rect_y_position + rect_height - (40))
                    # Đặt hình QR lên trang PDF với tọa độ đã điều chỉnh
                    c.drawImage(ImageReader(qr_image), rect_x_position + qr_x_offset, rect_y_position + qr_y_offset, width=qr_size, height=qr_size)
                    # Thêm văn bản "NO" và số thứ tự vào hình chữ nhật
                    c.setFont('msmincho.ttc', 15)
                    c.drawString(rect_x_position + 10, rect_y_position + 8, f'No.{no}')
                    c.setFont('msmincho.ttc', 10)
                    c.drawCentredString(rect_x_position + 95, rect_y_position + 23, タイプ)
                    
                    value001_str = str(value001)
                    count_l = value001.count('l')
                    count_w = value001.count('w')
                    w1, w2, w3, w4, w5, w6, w7 = process_data1(value001_str)
                    l1, l2, l3, l4, l5, l6, l7 = process_data(value001_str)  
                    ERROR = - 5  
            #TH60   BF2D@Hj@r@i@p1@l11680@n5@e58.11@d13@gSD295@s52@v@a@Gl1500@w90@l1300@w76@l2250@w14@l1680@w14@l2250@w76@l1300@w90@l1500@w0@C82@
                    if count_l == 8 and count_w == 7 and w1=="90" and 0 < int(w2) < 90 and 0 < int(w3) < 90 and 0 < int(w4) < 90 and 0 < int(w5) < 90 and w6=="90" and w7=="0":
                        value001_str = str(value001)  
                        result = extract_numbers(value001_str)      
                        img_path = image_list[60]

                        exec(code_string)

                        c.drawString(rect_x_position + 126, rect_y_position + 42 + ERROR, l1) #phải trên
                        c.drawString(rect_x_position + 144, rect_y_position + 68 + ERROR, l2) #phải
                        c.drawString(rect_x_position + 125, rect_y_position + 97 + ERROR, l3) #trên
                        c.drawCentredString(rect_x_position + 93, rect_y_position + 105 + ERROR, l4)  #trái 
                        c.drawRightString(rect_x_position + 60, rect_y_position + 97 + ERROR, l5) #phải trên
                        c.drawRightString(rect_x_position + 42, rect_y_position + 68 + ERROR, l6) #phải trên
                        c.drawRightString(rect_x_position + 60, rect_y_position + 43 + ERROR, l7) #phải trên
                        
            #TH59   BF2D@Hj@r@i@p1@l1480@n1@e2.31@d16@gSD295@s80@v@a@Gl218@w90@l400@w90@l400@w90@l400@w-90@l218@w0@PtSEGOPT;o0;o1;o1;o0;o0@C82@
                    elif count_l == 6 and count_w == 5 and (w1=="90" and w2=="90" and w3=="90" and w4=="-90" and w5=="0" and "PtSEGOPT" in value001 or w1=="90" and w2=="-90" and w3=="-90" and w4=="-90" and w5=="0" and "PtSEGOPT" in value001):
                        value001_str = str(value001)  
                        result = extract_numbers(value001_str) 
                        img_path = image_list[59]
                        exec(code_string)
                        c.drawString(rect_x_position + 115, rect_y_position + 50 + ERROR, l1) #phải trên
                        c.drawString(rect_x_position + 110, rect_y_position + 75 + ERROR, l2) #phải
                        c.drawCentredString(rect_x_position + 96, rect_y_position + 99 + ERROR, l3) #trên
                        c.drawRightString(rect_x_position + 74, rect_y_position + 81 + ERROR, l4)  #trái 
                        c.drawRightString(rect_x_position + 65, rect_y_position + 60 + ERROR, l5) #phải trên
                            
            #TH58   BF2D@Hj@r@i@p1@l1480@n1@e2.31@d16@gSD295@s80@v@a@Gl218@w90@l400@w90@l400@w90@l400@w90@l218@w0@PtSEGOPT;o0;o1;o1;o0;o0@C95@
                    elif count_l == 6 and count_w == 5 and w1=="90" and w2=="90" and w3=="90" and w4=="90" and w5=="0" and "PtSEGOPT" in value001:
                        value001_str = str(value001)  
                        result = extract_numbers(value001_str) 
                        img_path = image_list[58]
                        exec(code_string)
                        c.drawString(rect_x_position + 98, rect_y_position + 45 + ERROR, l1) #phải trên
                        c.drawString(rect_x_position + 113, rect_y_position + 75 + ERROR, l2) #phải
                        c.drawCentredString(rect_x_position + 100, rect_y_position + 101 + ERROR, l3) #trên
                        c.drawRightString(rect_x_position + 77, rect_y_position + 81 + ERROR, l4)  #trái 
                        c.drawRightString(rect_x_position + 66, rect_y_position + 60 + ERROR, l5) #phải trên
      
            #TH57   BF2D@Hj@r@i@p1@l1825@n1@e1.02@d10@gSD295@s30@v@a@Gl140@w101@l455@w79@l640@w90@l460@w-90@l200@w0@C96@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4=="-90" and w5=="0" or w1=="90" and w2=="-90" and -90 < int(w3) < 0 and -180 < int(w4) < -90  and w5=="0"):
                        value001_str = str(value001)  
                        result = extract_numbers(value001_str) 
                        img_path = image_list[57]
                        exec(code_string)
                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4=="-90" and w5=="0":
                            c.drawRightString(rect_x_position + 138, rect_y_position + 105 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 117, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 91, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 52, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawString(rect_x_position + 49, rect_y_position + 105 + ERROR, l1) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 138, rect_y_position + 105 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 117, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 91, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 52, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawString(rect_x_position + 49, rect_y_position + 105 + ERROR, l5) #phải trên

            #TH56   BF2D@Hj@r@i@p1@l1865@n5@e5.22@d10@gSD295@s30@v@a@Gl140@w101@l455@w79@l640@w90@l460@w90@l240@w0@C91@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4=="90" and w5=="0" or w1=="90" and w2=="90" and 0 < int(w3) < 90 and 90 < int(w4) < 180  and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[56]

                        exec(code_string)

                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4=="90" and w5=="0":
                            c.drawRightString(rect_x_position + 137, rect_y_position + 105 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 106, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 53, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawString(rect_x_position + 49, rect_y_position + 105 + ERROR, l1) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 137, rect_y_position + 105 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 106, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 53, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawString(rect_x_position + 49, rect_y_position + 105 + ERROR, l5) #phải trên

            #TH55   BF2D@Hj@r@i@p1@l1841@n1@e1.03@d10@gSD295@s30@v@a@Gl150@w79@l460@w-79@l640@w-90@l460@w90@l200@w0@C89@
                    elif count_l == 6 and count_w == 5 and (0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4=="90" and w5=="0" or w1=="90" and w2=="-90" and -90 < int(w3) < 0 and 0 < int(w4) < 90  and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[55]

                        exec(code_string)

                        if 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4=="90" and w5=="0":
                            c.drawString(rect_x_position + 118, rect_y_position + 105 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 117, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 97, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 66, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawRightString(rect_x_position + 62, rect_y_position + 105 + ERROR, l1) #phải trên
                        else:
                            c.drawString(rect_x_position + 118, rect_y_position + 105 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 117, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 97, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 66, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawRightString(rect_x_position + 62, rect_y_position + 105 + ERROR, l5) #phải trên
                            

            #TH54   BF2D@Hj@r@i@p1@l2031@n1@e1.14@d10@gSD295@s30@v@a@Gl200@w90@l460@w90@l830@w79@l460@w-79@l150@w0@C75@
                    elif count_l == 6 and count_w == 5 and (0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4=="-90" and w5=="0" or w1=="90" and w2=="90" and 0 < int(w3) < 90 and -90 < int(w4) < 0  and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[54]

                        exec(code_string)

                        if 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4=="-90" and w5=="0":
                            c.drawRightString(rect_x_position + 137, rect_y_position + 105 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 108, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 66, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawRightString(rect_x_position + 63, rect_y_position + 105 + ERROR, l1) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 137, rect_y_position + 105 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 108, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 66, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawRightString(rect_x_position + 63, rect_y_position + 105 + ERROR, l5) #phải trên

            #TH53   BF2D@Hj@r@i@p1@l1924@n1@e1.08@d10@gSD295@s30@v@a@Gl200@w106@l470@w74@l700@w79@l460@w-79@l150@w0@C81@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and 0 < int(w3) < 90 and -90 < int(w4) < 0 and w5=="0" or 0 < int(w1) < 90 and -90 < int(w2) < 0 and -90 < int(w3) < 0 and -180 < int(w4) < -90 and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[53]

                        exec(code_string)

                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and 0 < int(w3) < 90 and -90 < int(w4) < 0 and w5=="0":
                            c.drawRightString(rect_x_position + 137, rect_y_position + 105 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 135, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 102, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 70, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawRightString(rect_x_position + 66, rect_y_position + 105 + ERROR, l5) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 137, rect_y_position + 105 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 135, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 102, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 70, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawRightString(rect_x_position + 66, rect_y_position + 105 + ERROR, l1) #phải trên

            #TH52   BF2D@Hj@r@i@p1@l1770@n2@e1.98@d10@gSD295@s30@v@a@Gl87@w180@l450@w90@l650@w90@l450@w-90@l180@w0@C85@
                    elif count_l == 6 and count_w == 5 and (w1=="180" and w2=="90" and w3=="90" and w4=="-90" and w5=="0" or w1=="90" and w2=="-90" and w3=="-90" and w4=="-180" and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[52]

                        exec(code_string)

                        if w1=="180" and w2=="90" and w3=="90" and w4=="-90" and w5=="0":
                            c.drawRightString(rect_x_position + 128, rect_y_position + 87 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 108, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 70, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawRightString(rect_x_position + 68, rect_y_position + 105 + ERROR, l5) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 128, rect_y_position + 87 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 108, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 70, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawRightString(rect_x_position + 68, rect_y_position + 105 + ERROR, l1) #phải trên

            #TH51   BF2D@Hj@r@i@p1@l1766@n3@e2.97@d10@gSD295@s30@v@a@Gl100@w135@l450@w90@l650@w90@l450@w-90@l180@w0@C77@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="-90" and w5=="0" or w1=="90" and w2=="-90" and w3=="-90" and -180 < int(w4) < -90 and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[51]

                        exec(code_string)

                        if 90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="-90" and w5=="0":
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 108, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 70, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawRightString(rect_x_position + 68, rect_y_position + 105 + ERROR, l5) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 108, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 70, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawRightString(rect_x_position + 68, rect_y_position + 105 + ERROR, l1) #phải trên

            #TH50   BF2D@Hj@r@i@p1@l1740@n3@e2.92@d10@gSD295@s30@v@a@Gl87@w180@l450@w90@l650@w90@l450@w90@l150@w0@C76@
                    elif count_l == 6 and count_w == 5 and (w1=="180" and w2=="90" and w3=="90" and w4=="90" and w5=="0" or w1=="90" and w2=="90" and w3=="90" and w4=="180" and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[50]

                        exec(code_string)

                        if w1=="180" and w2=="90" and w3=="90" and w4=="90" and w5=="0":
                            c.drawRightString(rect_x_position + 128, rect_y_position + 87 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawRightString(rect_x_position + 68, rect_y_position + 105 + ERROR, l5) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 128, rect_y_position + 87 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawRightString(rect_x_position + 68, rect_y_position + 105 + ERROR, l1) #phải trêni

            #TH49   BF2D@Hj@r@i@p1@l1736@n1@e0.97@d10@gSD295@s30@v@a@Gl100@w135@l450@w90@l650@w90@l450@w90@l150@w0@C68@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="90" and w5=="0" or w1=="90" and w2=="90" and w3=="90" and 90 < int(w4) < 180 and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[49]

                        exec(code_string)

                        if 90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="90" and w5=="0":
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawRightString(rect_x_position + 68, rect_y_position + 105 + ERROR, l5) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawRightString(rect_x_position + 68, rect_y_position + 105 + ERROR, l1) #phải trên

            #TH48   BF2D@Hj@r@i@p1@l1706@n1@e0.96@d10@gSD295@s30@v@a@Gl100@w135@l450@w90@l650@w90@l450@w180@l87@w0@C95@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="180" and w5=="0" or w1=="180" and w2=="90" and w3=="90" and 90 < int(w4) < 180 and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[48]

                        exec(code_string)

                        if 90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="180" and w5=="0":
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l4)  #trái 
                            c.drawRightString(rect_x_position + 67, rect_y_position + 88 + ERROR, l5) #phải trên
                        else:
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l5) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l4) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l2)  #trái 
                            c.drawRightString(rect_x_position + 67, rect_y_position + 88 + ERROR, l1) #phải trên
            #TH47   BF2D@Hj@r@i@p1@l1377@n1@e0.77@d10@gSD295@s30@v@a@Gl87@w180@l400@w90@l500@w76@l410@w0@C84@
                    elif count_l == 5 and count_w == 4 and (w1 =="180" and w2 =="90" and 0 < int(w3) < 90 and w4 =="0" or 0 < int(w1) < 90 and w2 =="90" and w3=="180" and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[47]

                        exec(code_string)

                        if w1 =="180" and w2 =="90" and 0 < int(w3) < 90 and w4 =="0":
                            c.drawRightString(rect_x_position + 128, rect_y_position + 87 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 105, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 55, rect_y_position + 70 + ERROR, l4)  #trái 
                        else:
                            c.drawRightString(rect_x_position + 128, rect_y_position + 87 + ERROR, l4) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l3) #phải
                            c.drawCentredString(rect_x_position + 105, rect_y_position + 43 + ERROR, l2) #trên
                            c.drawRightString(rect_x_position + 55, rect_y_position + 70 + ERROR, l1)  #trái 

            #TH46    BF2D@Hj@r@i@p1@l1373@n1@e0.77@d10@gSD295@s30@v@a@Gl100@w135@l400@w90@l500@w76@l410@w0@C86@
                    elif count_l == 5 and count_w == 4 and (90 < int(w1) < 180 and w2 =="90" and 0 < int(w3) < 90 and w4 =="0" or 0 < int(w1) < 90 and w2 =="90" and 90 < int(w3) < 180 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[46]

                        exec(code_string)

                        if 90 < int(w1) < 180 and w2 =="90" and 0 < int(w3) < 90 and w4 =="0":
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 105, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 55, rect_y_position + 70 + ERROR, l4)  #trái 
                        else:
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l4) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l3) #phải
                            c.drawCentredString(rect_x_position + 105, rect_y_position + 43 + ERROR, l2) #trên
                            c.drawRightString(rect_x_position + 55, rect_y_position + 70 + ERROR, l1)  #trái 
            #TH45   BF2D@Hj@r@i@p1@l1460@n1@e0.82@d10@gSD295@s30@v@a@Gl87@w180@l400@w90@l600@w90@l400@w0@C67@
                    elif count_l == 5 and count_w == 4 and (w1=="180" and w2 =="90" and w3=="90" and w4 =="0" or w1=="90" and w2 =="90" and w3=="180" and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[45]

                        exec(code_string)

                        if w1=="180" and w2 =="90" and w3=="90" and w4 =="0":
                            c.drawRightString(rect_x_position + 128, rect_y_position + 88 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l4)  #trái 
                        else:
                            c.drawRightString(rect_x_position + 128, rect_y_position + 88 + ERROR, l4) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l3) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l2) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l1)  #trái 

            #TH44   BF2D@Hj@r@i@p1@l1456@n1@e0.82@d10@gSD295@s30@v@a@Gl100@w135@l400@w90@l600@w90@l400@w0@C92@
                    elif count_l == 5 and count_w == 4 and (90 < int(w1) < 180 and w2 =="90" and w3=="90" and w4 =="0" or w1=="90" and w2 =="90" and 90 < int(w3) < 180 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[44]

                        exec(code_string)

                        if 90 < int(w1) < 180 and w2 =="90" and w3=="90" and w4 =="0":
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l1) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l3) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l4)  #trái 
                        else:
                            c.drawRightString(rect_x_position + 130, rect_y_position + 94 + ERROR, l4) #phải trên
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l3) #phải
                            c.drawCentredString(rect_x_position + 90, rect_y_position + 43 + ERROR, l2) #trên
                            c.drawRightString(rect_x_position + 40, rect_y_position + 75 + ERROR, l1)  #trái 


            #TH43   BF2D@Hj@r@i@p1@l1539@n1@e0.86@d10@gSD295@s30@v@a@Gl231@w25@l500@w-90@l350@w-90@l500@w0@C69@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and w2 =="-90" and w3=="-90" and w4 =="0" or w1=="90" and w2 =="90" and -90 < int(w3) < 0 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[43]

                        exec(code_string)

                        if 0 < int(w1) < 90 and w2 =="-90" and w3=="-90" and w4 =="0":
                            c.drawString(rect_x_position + 120, rect_y_position + 62 + ERROR, l1)  
                            c.drawCentredString(rect_x_position + 78, rect_y_position + 52 + ERROR, l2) 
                            c.drawRightString(rect_x_position + 41, rect_y_position + 80 + ERROR, l3) 
                            c.drawCentredString(rect_x_position + 78, rect_y_position + 105 + ERROR, l4)
                        else:
                            c.drawString(rect_x_position + 120, rect_y_position + 62 + ERROR, l4)  
                            c.drawCentredString(rect_x_position + 78, rect_y_position + 52 + ERROR, l3) 
                            c.drawRightString(rect_x_position + 41, rect_y_position + 80 + ERROR, l2 )
                            c.drawCentredString(rect_x_position + 78, rect_y_position + 105 + ERROR, l1)

            #TH42   BF2D@Hj@r@i@p1@l1508@n1@e0.84@d10@gSD295@s30@v@a@Gl200@w23@l500@w90@l350@w90@l500@w0@C75@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and w2 =="90" and w3=="90" and w4 =="0" or w1=="90" and w2 =="90" and 0 < int(w3) < 90 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[42]

                        exec(code_string)

                        if 0 < int(w1) < 90 and w2 =="90" and w3=="90" and w4 =="0":
                            c.drawRightString(rect_x_position + 120, rect_y_position + 65 + ERROR, l1)  
                            c.drawString(rect_x_position + 58, rect_y_position + 56 + ERROR, l2) 
                            c.drawRightString(rect_x_position + 41, rect_y_position + 75 + ERROR, l3) 
                            c.drawCentredString(rect_x_position + 78, rect_y_position + 105 + ERROR, l4)
                        else:
                            c.drawRightString(rect_x_position + 120, rect_y_position + 65 + ERROR, l4)  
                            c.drawString(rect_x_position + 58, rect_y_position + 56 + ERROR, l3) 
                            c.drawRightString(rect_x_position + 41, rect_y_position + 75 + ERROR, l2) 
                            c.drawCentredString(rect_x_position + 78, rect_y_position + 105 + ERROR, l1)

            #TH41   BF2D@Hj@r@i@p1@l1268@n1@e0.71@d10@gSD295@s30@v@a@Gl450@w65@l150@w25@l200@w90@l500@w0@C70@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and 0 < int(w2) < 90 and w3=="90" and w4 =="0" or w1=="90" and 0 < int(w2) < 90 and 0 < int(w3) < 90 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[41]

                        exec(code_string)

                        if 0 < int(w1) < 90 and 0 < int(w2) < 90 and w3=="90" and w4 =="0":
                            c.drawString(rect_x_position + 98, rect_y_position + 43 + ERROR, l1)  
                            c.drawString(rect_x_position + 58, rect_y_position + 64 + ERROR, l2) 
                            c.drawRightString(rect_x_position + 41, rect_y_position + 82 + ERROR, l3) 
                            c.drawCentredString(rect_x_position + 80, rect_y_position + 105 + ERROR, l4)
                        else:
                            c.drawString(rect_x_position + 98, rect_y_position + 43 + ERROR, l4)  
                            c.drawString(rect_x_position + 58, rect_y_position + 64 + ERROR, l3) 
                            c.drawRightString(rect_x_position + 41, rect_y_position + 82 + ERROR, l2) 
                            c.drawCentredString(rect_x_position + 80, rect_y_position + 105 + ERROR, l1)
                              

            #TH40   BF2D@Hj@r@i@p1@l1180@n1@e0.66@d10@gSD295@s30@v@a@Gl400@w106@l394@w74@l302@w90@l130@w0@C82@
                    elif count_l == 5 and count_w == 4 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4 =="0" or w1=="90" and 0 < int(w2) < 90 and 90 < int(w3) < 180 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[40]

                        exec(code_string)

                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4 =="0":
                            c.drawString(rect_x_position + 142, rect_y_position + 75 + ERROR, l1) 
                            c.drawRightString(rect_x_position + 100, rect_y_position + 98 + ERROR, l2)  
                            c.drawRightString(rect_x_position + 41, rect_y_position + 69 + ERROR, l3) 
                            c.drawString(rect_x_position + 50, rect_y_position + 56 + ERROR, l4)
                        else:
                            c.drawString(rect_x_position + 142, rect_y_position + 75 + ERROR, l4) 
                            c.drawRightString(rect_x_position + 100, rect_y_position + 98 + ERROR, l3)  
                            c.drawRightString(rect_x_position + 41, rect_y_position + 69 + ERROR, l2) 
                            c.drawString(rect_x_position + 50, rect_y_position + 56 + ERROR, l1) 

            #TH39   BF2D@Hj@r@i@p1@l1058@n1@e0.59@d10@gSD295@s30@v@a@Gl400@w113@l250@w67@l300@w-90@l150@w0@C72@
                    elif count_l == 5 and count_w == 4 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="-90" and w4 =="0" or w1=="90" and -90 < int(w2) < 0 and -180 < int(w3) < -90 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[39]

                        exec(code_string)

                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="-90" and w4 =="0":
                            c.drawString(rect_x_position + 142, rect_y_position + 75 + ERROR, l1) 
                            c.drawRightString(rect_x_position + 117, rect_y_position + 98 + ERROR, l2)  
                            c.drawString(rect_x_position + 84, rect_y_position + 69 + ERROR, l3) 
                            c.drawRightString(rect_x_position + 67, rect_y_position + 56 + ERROR, l4)
                        else:
                            c.drawString(rect_x_position + 142, rect_y_position + 75 + ERROR, l4) 
                            c.drawRightString(rect_x_position + 117, rect_y_position + 98 + ERROR, l3)  
                            c.drawString(rect_x_position + 84, rect_y_position + 69 + ERROR, l2) 
                            c.drawRightString(rect_x_position + 70, rect_y_position + 56 + ERROR, l1) 

            #TH38   BF2D@Hj@r@i@p1@l1210@n1@e1.2@d13@gSD295@s39@v@a@Gl200@w90@l300@w-45@l250@w45@l500@w0@C84@
                    elif count_l == 5 and count_w == 4 and (w1=="90" and -90 < int(w2) < 0 and 0 < int(w3) < 90 and w4 =="0" or 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="90" and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[38]

                        exec(code_string)

                        if w1=="90" and -90 < int(w2) < 0 and 0 < int(w3) < 90 and w4 =="0":
                            c.drawCentredString(rect_x_position + 120, rect_y_position + 56 + ERROR, l4)  
                            c.drawRightString(rect_x_position + 82, rect_y_position + 60 + ERROR, l3) 
                            c.drawString(rect_x_position + 50, rect_y_position + 80 + ERROR, l2) 
                            c.drawRightString(rect_x_position + 40, rect_y_position + 85 + ERROR, l1) 
                        else:
                            c.drawCentredString(rect_x_position + 120, rect_y_position + 56 + ERROR, l1)  
                            c.drawRightString(rect_x_position + 82, rect_y_position + 60 + ERROR, l2) 
                            c.drawString(rect_x_position + 50, rect_y_position + 80 + ERROR, l3) 
                            c.drawRightString(rect_x_position + 40, rect_y_position + 85 + ERROR, l4)  

            #TH37   BF2D@Hj@r@i@p1@l1238@n1@e1.23@d13@gSD295@s39@v@a@Gl400@w66@l300@w-66@l250@w-59@l325@w0@C88@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and -90 < int(w2) < 0 and -90 < int(w3) < 0 and w4 =="0" or 0 < int(w1) < 90 and 0 < int(w2) < 90 and -90 < int(w3) < 0 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[37]

                        exec(code_string)

                        if 0 < int(w1) < 90 and -90 < int(w2) < 0 and -90 < int(w3) < 0 and w4 =="0":
                            c.drawCentredString(rect_x_position + 126, rect_y_position + 105 + ERROR, l1)  
                            c.drawString(rect_x_position + 107, rect_y_position + 75 + ERROR, l2) 
                            c.drawCentredString(rect_x_position + 76, rect_y_position + 42 + ERROR, l3) 
                            c.drawRightString(rect_x_position + 47, rect_y_position + 76 + ERROR, l4)   
                        else:
                            c.drawCentredString(rect_x_position + 126, rect_y_position + 105 + ERROR, l4)  
                            c.drawString(rect_x_position + 107, rect_y_position + 75 + ERROR, l3) 
                            c.drawCentredString(rect_x_position + 76, rect_y_position + 42 + ERROR, l2) 
                            c.drawRightString(rect_x_position + 47, rect_y_position + 76 + ERROR, l1)  

            #TH36   BF2D@Hj@r@i@p1@l1187@n1@e1.18@d13@gSD295@s39@v@a@Gl400@w66@l308@w-66@l250@w-90@l280@w0@C78@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4 =="0" or w1=="90" and 0 < int(w2) < 90 and -90 < int(w3) < 0 and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[36]

                        exec(code_string)
                        if 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4 =="0":
                            c.drawString(rect_x_position + 112, rect_y_position + 105 + ERROR, l1)  
                            c.drawString(rect_x_position + 92, rect_y_position + 75 + ERROR, l2) 
                            c.drawCentredString(rect_x_position + 58, rect_y_position + 42 + ERROR, l3) 
                            c.drawRightString(rect_x_position + 41, rect_y_position + 76 + ERROR, l4)   
                        else:
                            c.drawString(rect_x_position + 112, rect_y_position + 105 + ERROR, l4)  
                            c.drawString(rect_x_position + 92, rect_y_position + 75 + ERROR, l3) 
                            c.drawCentredString(rect_x_position + 58, rect_y_position + 42 + ERROR, l2) 
                            c.drawRightString(rect_x_position + 41, rect_y_position + 76 + ERROR, l1)  
                            
            #TH35   BF2D@Hj@r@i@p1@l2738@n1@e2.72@d13@gSD295@s39@v@a@Gl112@w135@l650@w90@l650@w90@l650@w90@l650@w135@l111@w0@C95@
                    elif count_l == 7 and count_w == 6 and w1=="135" and w2=="90" and w3=="90" and w4=="90" and w5=="135" and w6=="0":
 
                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                                  
                        img_path = image_list[35]

                        exec(code_string)

                        if int(l2) > int(l3):
                            c.drawString(rect_x_position + 95, rect_y_position + 82 + ERROR, l1.rjust(6))  #giữa .rjust(6)
                            c.drawString(rect_x_position + 78, rect_y_position + 105 + ERROR, l2.center(6)) #trên
                            c.drawString(rect_x_position + 9, rect_y_position + 76 + ERROR, l3.rjust(6))  #trái .center(6)
                            c.drawString(rect_x_position + 78, rect_y_position + 42 + ERROR, l4.center(6))  #dưới
                            c.drawString(rect_x_position + 144, rect_y_position + 76 + ERROR, l5) #phải
                        else:
                            c.drawString(rect_x_position + 95, rect_y_position + 82 + ERROR, l1.rjust(6))  #giữa .rjust(6)
                            c.drawString(rect_x_position + 78, rect_y_position + 105 + ERROR, l5.center(6)) #trên
                            c.drawString(rect_x_position + 9, rect_y_position + 76 + ERROR, l4.rjust(6))  #trái .center(6)
                            c.drawString(rect_x_position + 78, rect_y_position + 42 + ERROR, l3.center(6))  #dưới
                            c.drawString(rect_x_position + 144, rect_y_position + 76 + ERROR, l2) #phải
                            
            #TH34   BF2D@Hj@r@i@p1@l1151@n1@e1.15@d13@gSD295@s39@v@a@Gl190@w64@l310@w-64@l220@w-75@l290@w75@l200@w0@C93@
                    elif count_l == 6 and count_w == 5 and 0 < int(w1) < 90 and -90 < int(w2) < 0 and -90 < int(w3) < 0 and 0 < int(w4) < 90 and w5=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[34]

                        exec(code_string)

                        c.drawString(rect_x_position + 114, rect_y_position + 105 + ERROR, l5) #phải trên
                        c.drawString(rect_x_position + 114, rect_y_position + 72 + ERROR, l4) #phải
                        c.drawString(rect_x_position + 78, rect_y_position + 42 + ERROR, l3.center(6)) #trên
                        c.drawString(rect_x_position + 38, rect_y_position + 72 + ERROR, l2.rjust(6))  #trái
                        c.drawString(rect_x_position + 38, rect_y_position + 105 + ERROR, l1.rjust(6))  #trái trÊN

            #TH33   BF2D@Hj@r@i@p1@l1719@n1@e1.71@d13@gSD295@s39@v@a@Gl530@w90@l360@w90@l300@w90@l280@w-90@l350@w0@C95@   
                    elif count_l == 6 and count_w == 5 and (w1=="90" and w2=="90" and w3=="90" and w4=="-90" and w5=="0" or w1=="90" and w2=="-90" and w3=="-90" and w4=="-90" and w5=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        
                                    
                        img_path = image_list[33]

                        exec(code_string)

                        if w1=="90" and w2=="90" and w3=="90" and w4=="-90" and w5=="0":
                            c.drawString(rect_x_position + 100, rect_y_position + 86 + ERROR, l5.rjust(6))  #giữa
                            c.drawString(rect_x_position + 75, rect_y_position + 65 + ERROR, l4) #phải
                            c.drawString(rect_x_position + 43, rect_y_position + 43 + ERROR, l3.center(6))  #dưới
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l2.rjust(6))  #trái
                            c.drawString(rect_x_position + 65, rect_y_position + 105 + ERROR, l1.rjust(6)) #trên
                        else: 
                            c.drawString(rect_x_position + 100, rect_y_position + 86 + ERROR, l1.rjust(6))  #giữa
                            c.drawString(rect_x_position + 75, rect_y_position + 65 + ERROR, l2) #phải
                            c.drawString(rect_x_position + 43, rect_y_position + 43 + ERROR, l3.center(6))  #dưới
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l4.rjust(6))  #trái
                            c.drawString(rect_x_position + 65, rect_y_position + 105 + ERROR, l5.rjust(6)) #trên
             #TH32  BF2D@Hj@r@i@p1@l1376@n1@e1.37@d13@gSD295@s39@v@a@Gl164@w90@l200@w90@l750@w90@l200@w90@l164@w0@C75@
                    elif count_l == 6 and count_w == 5 and w1=="90" and w2=="90" and w3=="90" and w4=="90" and w5=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[32]

                        exec(code_string)

                        c.drawString(rect_x_position + 111, rect_y_position + 43 + ERROR, l1) #phải trên
                        c.drawString(rect_x_position + 144, rect_y_position + 63 + ERROR, l2) #phải
                        c.drawString(rect_x_position + 78, rect_y_position + 81 + ERROR, l3.center(6))  #giữa 
                        c.drawString(rect_x_position + 9, rect_y_position + 63 + ERROR, l4.rjust(6))  #trái
                        c.drawString(rect_x_position + 40, rect_y_position + 43 + ERROR, l5.rjust(6))  #trái trÊN
          
            #TH31   BF2D@Hj@r@i@p1@l1202@n1@e0.67@d10@gSD295@s30@v@a@Gl100@w135@l210@w90@l630@w90@l210@w135@l100@w0@C86@
                    elif count_l == 6 and count_w == 5 and 90 < int(w1) < 180 and w2=="90" and w3=="90" and 90 < int(w4) < 180 and w5=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[31]

                        exec(code_string)

                        c.drawString(rect_x_position + 97, rect_y_position + 93 + ERROR, l1.rjust(6)) #phải trên
                        c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                        c.drawString(rect_x_position + 77, rect_y_position + 43 + ERROR, l3.center(6)) #trên
                        c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l4.rjust(6))  #trái 
                        c.drawString(rect_x_position + 55, rect_y_position + 93 + ERROR, l5)  #trái trÊN
   
            #TH30   BF2D@Hj@r@i@p1@l1140@n1@e0.64@d10@gSD295@s30@v@a@Gl87@w180@l340@w90@l300@w90@l340@w180@l87@w0@C90@
                    elif count_l == 6 and count_w == 5 and w1=="180" and w2=="90" and w3=="90" and w4=="180" and w5=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[30]

                        exec(code_string)

                        c.drawString(rect_x_position + 95, rect_y_position + 88 + ERROR, l1.rjust(6)) #phải trên
                        c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l2) #phải
                        c.drawString(rect_x_position + 77, rect_y_position + 43 + ERROR, l3.center(6)) #trên
                        c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l4.rjust(6))  #trái 
                        c.drawString(rect_x_position + 56, rect_y_position + 88 + ERROR, l5)  #trái trÊN

            #TH29   BF2D@Hj@r@i@p1@l1369@n1@e1.36@d13@gSD295@s39@v@a@Gl220@w90@l300@w-90@l300@w-90@l300@w90@l350@w0@C84@
                    elif count_l == 6 and count_w == 5 and w1=="90" and w2=="-90" and w3=="-90" and w4=="90" and w5=="0":
                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[29]

                        exec(code_string)

                        c.drawString(rect_x_position + 112, rect_y_position + 41 + ERROR, l5) #phải dưới
                        c.drawString(rect_x_position + 114, rect_y_position + 75 + ERROR, l4) #phải trên
                        c.drawString(rect_x_position + 79, rect_y_position + 105 + ERROR, l3.center(6)) #trên
                        c.drawString(rect_x_position + 37, rect_y_position + 75 + ERROR, l2.rjust(6))  #trái
                        c.drawString(rect_x_position + 39, rect_y_position + 41 + ERROR, l1.rjust(6))  #trái dưới
                        
            #TH28   BF2D@Hj@r@i@p1@l1181@n1@e0.66@d10@gSD295@s30@v@a@Gl150@w90@l300@w-90@l230@w90@l560@w0@C88@
                    elif count_l == 5 and count_w == 4 and w1 == "90" and w2 == "-90" and w3 == "90" and w4 == "0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[28]

                        exec(code_string)

                        if int(l1) > int(l4):
                            c.drawString(rect_x_position + 8, rect_y_position + 57 + ERROR, l4.rjust(6))  #trái
                            c.drawString(rect_x_position + 36, rect_y_position + 73 + ERROR, l3.rjust(6))  #dưới
                            c.drawString(rect_x_position + 75, rect_y_position + 81 + ERROR, l2) #phải
                            c.drawString(rect_x_position + 90, rect_y_position + 104 + ERROR, l1.rjust(6)) #trên 
                        else:
                            c.drawString(rect_x_position + 8, rect_y_position + 57 + ERROR, l1.rjust(6))  #trái
                            c.drawString(rect_x_position + 36, rect_y_position + 73 + ERROR, l2.rjust(6))  #dưới
                            c.drawString(rect_x_position + 75, rect_y_position + 81 + ERROR, l3) #phải
                            c.drawString(rect_x_position + 90, rect_y_position + 104 + ERROR, l4.rjust(6)) #trên 

            #TH27   BF2D@Hj@r@i@p1@l1204@n1@e1.2@d13@gSD295@s39@v@a@Gl350@w90@l300@w90@l280@w-90@l350@w0@C69@
                    elif count_l == 5 and count_w == 4 and (w1=="90" and w2=="90" and w3=="-90" and w4=="0" or w1=="90" and w2=="-90" and w3=="-90" and w4=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        
                        img_path = image_list[27]

                        exec(code_string)

                        if w1=="90" and w2=="90" and w3=="-90" and w4=="0":
                            c.drawString(rect_x_position + 90, rect_y_position + 105 + ERROR, l4.rjust(6)) #trên
                            c.drawString(rect_x_position + 75, rect_y_position + 75 + ERROR, l3) #phải
                            c.drawString(rect_x_position + 44, rect_y_position + 43 + ERROR, l2.center(6))  #dưới
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l1.rjust(6))  #trái
                        else:
                            c.drawString(rect_x_position + 90, rect_y_position + 105 + ERROR, l1.rjust(6)) #trên
                            c.drawString(rect_x_position + 75, rect_y_position + 75 + ERROR, l2) #phải
                            c.drawString(rect_x_position + 44, rect_y_position + 43 + ERROR, l3.center(6))  #dưới
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l4.rjust(6))  #trái
                            
            #TH26   BF2D@Hj@r@i@p1@l1721@n1@e2.68@d16@gSD295@s80@v@a@Gl218@w90@l1070@w90@l300@w90@l250@w0@C66@
                    elif count_l == 5 and count_w == 4 and w1=="90" and w2=="90" and w3=="90" and w4=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[26]

                        exec(code_string)

                        if int(l2) > int(l3):
                            c.drawString(rect_x_position + 143, rect_y_position + 63 + ERROR, l1) #phải
                            c.drawString(rect_x_position + 75, rect_y_position + 43 + ERROR, l2.center(6))  #dưới
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l3.rjust(6))  #trái
                            c.drawString(rect_x_position + 41, rect_y_position + 105 + ERROR, l4.rjust(6)) #trên
                        else:
                            c.drawString(rect_x_position + 143, rect_y_position + 63 + ERROR, l4) #phải
                            c.drawString(rect_x_position + 75, rect_y_position + 43 + ERROR, l3.center(6))  #dưới
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l2.rjust(6))  #trái
                            c.drawString(rect_x_position + 41, rect_y_position + 105 + ERROR, l1.rjust(6)) #trên

            #TH25   BF2D@Hj@r@i@p1@l1164@n1@e1.16@d13@gSD295@s39@v@a@Gl112@w135@l950@w-135@l111@w0@C79@
                    elif count_l == 4 and count_w == 3 and 90 < int(w1) < 180 and -180 < int(w2) < -90 and w3=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[25]

                        exec(code_string)

                        c.drawString(rect_x_position + 22, rect_y_position + 58 + ERROR, l1.rjust(6))  #trái
                        c.drawString(rect_x_position + 78, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                        c.drawString(rect_x_position + 130, rect_y_position + 90 + ERROR, l3) #phải
                        
            #TH24   BF2D@Hj@r@i@p1@l1987@n1@e6.04@d22@gSD345@s88@v@a@Gl204@w180@l1500@w-180@l204@w0@C83@
                    elif count_l == 4 and count_w == 3 and w1=="180" and w2=="-180" and w3=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[24]

                        exec(code_string)

                        c.drawString(rect_x_position + 41, rect_y_position + 105 + ERROR, l1.rjust(6))  #trái
                        c.drawString(rect_x_position + 75, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                        c.drawString(rect_x_position + 109, rect_y_position + 43 + ERROR, l3) #phải

            #TH23   BF2D@Hj@r@i@p1@l1961@n1@e3.06@d16@gSD295@s80@v@a@Gl450@w67@l1050@w-67@l500@w0@C83@
                    elif count_l == 4 and count_w == 3 and 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[23]

                        exec(code_string)

                        c.drawString(rect_x_position + 36, rect_y_position + 105 + ERROR, l1.rjust(6))  #trái
                        c.drawString(rect_x_position + 61, rect_y_position + 70 + ERROR, l2.center(6))  #giữa           
                        c.drawString(rect_x_position + 115, rect_y_position + 57 + ERROR, l3) #phải

            #TH22   BF2D@Hj@r@i@p1@l2458@n1@e3.83@d16@gSD295@s80@v@a@Gl218@w90@l2100@w-90@l218@w0@C79@
                    elif count_l == 4 and count_w == 3 and w1=="90" and w2=="-90" and w3=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[22]

                        exec(code_string)

                        c.drawString(rect_x_position + 8, rect_y_position + 86 + ERROR, l1.rjust(6))  #trái
                        c.drawString(rect_x_position + 77, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                        c.drawString(rect_x_position + 142, rect_y_position + 63 + ERROR, l3) #phải

            #TH21   BF2D@Hj@r@i@p1@l1644@n1@e2.56@d16@gSD295@s80@v@a@Gl154@w135@l1300@w-45@l200@w0@C77@
                    elif count_l == 4 and count_w == 3 and (90 < int(w1) < 180 and -90 < int(w2) < 0 and w3=="0" or 0 < int(w1) < 90 and -180 < int(w2) < -90 and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[21]

                        exec(code_string)

                        if 90 < int(w1) < 180:
                            c.drawString(rect_x_position + 128, rect_y_position + 90 + ERROR, l1) #phải
                            c.drawString(rect_x_position + 85, rect_y_position + 67 + ERROR, l2.center(6))  #giữa 
                            c.drawString(rect_x_position + 25, rect_y_position + 67 + ERROR, l3.rjust(6))  #trái
                        else:
                            c.drawString(rect_x_position + 128, rect_y_position + 90 + ERROR, l3) #phải
                            c.drawString(rect_x_position + 85, rect_y_position + 67 + ERROR, l2.center(6))  #giữa 
                            c.drawString(rect_x_position + 25, rect_y_position + 67 + ERROR, l1.rjust(6))  #trái

            #TH20   BF2D@Hj@r@i@p1@l1944@n1@e3.03@d16@gSD295@s80@v@a@Gl400@w78@l1000@w102@l600@w0@C67@
                    elif count_l == 4 and count_w == 3 and (0 < int(w1) < 90 and 90 < int(w2) < 180 and w3=="0" or 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[20]  
                               
                        exec(code_string)

                        if 0 < int(w1) < 90:
                            c.drawString(rect_x_position + 8, rect_y_position + 68 + ERROR, l1.rjust(6))  #trái 
                            c.drawString(rect_x_position + 75, rect_y_position + 100 + ERROR, l2.center(6)) #trên     
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l3) #phải
                        else:
                            c.drawString(rect_x_position + 8, rect_y_position + 68 + ERROR, l3.rjust(6))  #trái 
                            c.drawString(rect_x_position + 75, rect_y_position + 100 + ERROR, l2.center(6)) #trên     
                            c.drawString(rect_x_position + 143, rect_y_position + 75 + ERROR, l1) #phải

            #TH19   BF2D@Hj@r@i@p1@l1970@n1@e3.07@d16@gSD295@s80@v@a@Gl122@w180@l1600@w-45@l220@w0@C78@
                    elif count_l == 4 and count_w == 3 and (w1=="180" and -90 < int(w2) < 0 and w3=="0" or 0 < int(w1) < 90 and w2=="-180" and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[19]

                        exec(code_string)

                        if w1=="180":
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l1) #phải
                            c.drawString(rect_x_position + 82, rect_y_position + 81 + ERROR, l2.center(6))  #giữa
                            c.drawString(rect_x_position + 21, rect_y_position + 66 + ERROR, l3.rjust(6))  #trái 
                        else:
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l3) #phải
                            c.drawString(rect_x_position + 82, rect_y_position + 81 + ERROR, l2.center(6))  #giữa
                            c.drawString(rect_x_position + 21, rect_y_position + 66 + ERROR, l1.rjust(6))  #trái 

                        #c.drawString(rect_x_position + 75, rect_y_position + 40, l5)  #dưới
            #TH18   BF2D@Hj@r@i@p1@l2441@n1@e7.42@d22@gSD345@s88@v@a@Gl204@w180@l2000@w45@l210@w0@C66@
                    elif count_l == 4 and count_w == 3 and (w1=="180" and 0 < int(w2) < 90 and w3=="0" or 0 < int(w1) < 90 and w2=="180" and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[18]

                        exec(code_string)

                        if w1=="180":
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l1) #phải
                            c.drawString(rect_x_position + 82, rect_y_position + 67 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 21, rect_y_position + 83 + ERROR, l3.rjust(6))  #trái 
                        else:
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l3) #phải
                            c.drawString(rect_x_position + 82, rect_y_position + 67 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 21, rect_y_position + 83 + ERROR, l1.rjust(6))  #trái                       

            #TH17   BF2D@Hj@r@i@p1@l1477@n1@e1.47@d13@gSD295@s39@v@a@Gl86@w180@l1200@w135@l180@w0@C76@
                    elif count_l == 4 and count_w == 3 and (w1=="180" and 90 < int(w2) < 180 and w3=="0" or 90 < int(w1) < 180 and w2=="180" and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[17]

                        exec(code_string)

                        if w1=="180":
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l1) #phải
                            c.drawString(rect_x_position + 80, rect_y_position + 67 + ERROR, l2.center(6))  #giữa
                            c.drawString(rect_x_position + 21, rect_y_position + 90 + ERROR, l3.rjust(6))  #trái        
                        else:
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l3) #phải
                            c.drawString(rect_x_position + 80, rect_y_position + 67 + ERROR, l2.center(6))  #giữa
                            c.drawString(rect_x_position + 21, rect_y_position + 90 + ERROR, l1.rjust(6))  #trái 

            #TH16   BF2D@Hj@r@i@p1@l1267@n1@e1.26@d13@gSD295@s39@v@a@Gl86@w180@l1000@w-135@l170@w0@C72@
                    elif count_l == 4 and count_w == 3 and (w1=="180" and -180 < int(w2) < -90 and w3=="0" or 90 < int(w1) < 180 and w2=="-180" and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[16]

                        exec(code_string)

                        if w1=="180":
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l1)  #trái
                            c.drawString(rect_x_position + 80, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 21, rect_y_position + 58 + ERROR, l3.rjust(6)) #phải
                        else:
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l3)  #trái
                            c.drawString(rect_x_position + 80, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 21, rect_y_position + 58 + ERROR, l1.rjust(6)) #phải

            #TH15   BF2D@Hj@r@i@p1@l1278@n1@e1.99@d16@gSD295@s80@v@a@Gl218@w90@l900@w-135@l200@w0@C78@
                    elif count_l == 4 and count_w == 3 and (w1=="90" and -180 < int(w2) < -90 and w3=="0" or 90 < int(w1) < 180 and w2=="-90" and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[15]

                        exec(code_string)

                        if w1=="90":
                            c.drawString(rect_x_position + 8, rect_y_position + 62 + ERROR, l1.rjust(6))  #trái
                            c.drawString(rect_x_position + 74, rect_y_position + 67 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 130, rect_y_position + 90 + ERROR, l3) #phải
                        else:
                            c.drawString(rect_x_position + 8, rect_y_position + 62 + ERROR, l3.rjust(6))  #trái
                            c.drawString(rect_x_position + 74, rect_y_position + 67 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 130, rect_y_position + 90 + ERROR, l1) #phải

            #TH14   BF2D@Hj@r@i@p1@l2489@n1@e3.88@d16@gSD295@s80@v@a@Gl218@w90@l1860@w-45@l460@w0@C91@
                    elif count_l == 4 and count_w == 3 and (w1=="90" and -90 < int(w2) < 0 and w3=="0" or 0 < int(w1) < 90 and w2=="-90" and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[14]

                        exec(code_string)
                    
                        if w1=="90":
                            c.drawString(rect_x_position + 8, rect_y_position + 62 + ERROR, l1.rjust(6))  #trái
                            c.drawString(rect_x_position + 65, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 127, rect_y_position + 80 + ERROR, l3) #phải
                        else:
                            c.drawString(rect_x_position + 8, rect_y_position + 62 + ERROR, l3.rjust(6))  #trái
                            c.drawString(rect_x_position + 65, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 127, rect_y_position + 80 + ERROR, l1) #phải

            #TH13   BF2D@Hj@r@i@p1@l2128@n1@e4.79@d19@gSD345@s114@v@a@Gl268@w90@l1700@w-180@l154@w0@C73@
                    elif count_l == 4 and count_w == 3 and (w1=="90" and w2=="-180" and w3=="0" or w1=="180" and w2=="-90" and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[13]
                    
                        exec(code_string)
                    
                        if  w1=="90":
                            c.drawString(rect_x_position + 8, rect_y_position + 62 + ERROR, l1.rjust(6))  #trái
                            c.drawString(rect_x_position + 75, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l3) #phải
                        else:
                            c.drawString(rect_x_position + 8, rect_y_position + 62 + ERROR, l3.rjust(6))  #trái
                            c.drawString(rect_x_position + 75, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 110, rect_y_position + 105 + ERROR, l1) #phải

            #TH12   BF2D@Hj@r@i@p1@l2248@n1@e3.51@d16@gSD295@s80@v@a@Gl218@w90@l1800@w135@l270@w0@C80@
                    elif count_l == 4 and count_w == 3 and (w1 == "90" and 90 < int(w2) < 180 and w3 == "0" or 90 < int(w1) < 180 and w2 == "90" and w3 == "0"):
                        
                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        
                        
                        img_path = image_list[12]
                    
                        exec(code_string)
                    
                        if w1 == "90":
                            c.drawString(rect_x_position + 142, rect_y_position + 85 + ERROR, l1) #phải
                            c.drawString(rect_x_position + 80, rect_y_position + 67 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 24, rect_y_position + 90 + ERROR, l3.rjust(6))  #trái
                        else:
                            c.drawString(rect_x_position + 142, rect_y_position + 85 + ERROR, l3) #phải
                            c.drawString(rect_x_position + 80, rect_y_position + 67 + ERROR, l2.center(6))  #giữa           
                            c.drawString(rect_x_position + 24, rect_y_position + 90 + ERROR, l1.rjust(6))  #trái

                        #c.drawString(rect_x_position + 75, rect_y_position + 40, l5)  #dưới
            #TH11   BF2D@Hj@r@i@p1@l2559@n1@e7.78@d22@gSD345@s88@v@a@Gl311@w90@l2100@w45@l210@w0@C95@
                    elif count_l == 4 and count_w == 3 and (w1 == "90" and 0 < int(w2) < 90 and w3 =="0" or 0 < int(w1) < 90 and w2 =="90"  and w3 =="0"):
                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[11]  #Thay hình
                    
                        exec(code_string)
                    
                        if w1=="90":
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l1.rjust(6))  #trái
                            c.drawString(rect_x_position + 65, rect_y_position + 105 + ERROR, l2.center(6)) #trên
                            c.drawString(rect_x_position + 130, rect_y_position + 75 + ERROR, l3) #phải
                        else:
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l3.rjust(6))  #trái
                            c.drawString(rect_x_position + 65, rect_y_position + 105 + ERROR, l2.center(6)) #trên
                            c.drawString(rect_x_position + 130, rect_y_position + 75 + ERROR, l1) #phải
                            
            #TH10   BF2D@Hj@r@i@p1@l2105@n1@e6.4@d22@gSD345@s88@v@a@Gl204@w180@l1600@w90@l311@w0@C81@
                    elif count_l == 4 and count_w == 3 and (w1=="90" and w2=="180" and w3=="0" or w1=="180" and w2=="90" and w3=="0"):

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[10]
                    
                        exec(code_string)
                    
                        if w1=="180":
                            c.drawString(rect_x_position + 110, rect_y_position + 67 + ERROR, l1) #phải
                            c.drawString(rect_x_position + 72, rect_y_position + 105 + ERROR, l2.center(6)) #trên        
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l3.rjust(6))  #trái
                        else:
                            c.drawString(rect_x_position + 110, rect_y_position + 67 + ERROR, l3) #phải
                            c.drawString(rect_x_position + 72, rect_y_position + 105 + ERROR, l2.center(6)) #trên        
                            c.drawString(rect_x_position + 8, rect_y_position + 75 + ERROR, l1.rjust(6))  #trái

            #TH9    BF2D@Hj@r@i@p1@l1514@n1@e2.36@d16@gSD295@s48@v@a@Gl138@w135@l1250@w135@l138@w0@C92@
                    elif count_l == 4 and count_w == 3 and 90 < int(w1) < 180 and 90 < int(w2) < 180 and w3=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[9]
                    
                        exec(code_string)
                    
                        c.drawString(rect_x_position + 21, rect_y_position + 58 + ERROR, l1.rjust(6))  #trái
                        c.drawString(rect_x_position + 77, rect_y_position + 81 + ERROR, l2.center(6))  #giữa           
                        c.drawString(rect_x_position + 130, rect_y_position + 58 + ERROR, l3) #phải

            #TH8    BF2D@Hj@r@i@p1@l2117@n1@e4.76@d19@gSD345@s114@v@a@Gl398@w85@l1509@w45@l265@w0@C89@
                    elif count_l == 4 and count_w == 3 and 0 < int(w1) < 90 and 0 < int(w2) < 90 and w3=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[8]
                    
                        exec(code_string)
                    
                        c.drawString(rect_x_position + 21, rect_y_position + 66 + ERROR, l1.rjust(6))  #trái
                        c.drawString(rect_x_position + 75, rect_y_position + 81 + ERROR, l2.center(6))  #giữa
                        c.drawString(rect_x_position + 130, rect_y_position + 66 + ERROR, l3) #phải

            #TH7 BF2D@Hj@r@i@p1@l2300@n1@e1.29@d10@gSD295@s30@v@a@Gl87@w180@l2100@w180@l87@w0@C79@
                    elif count_l == 4 and count_w == 3 and w1=="180" and w2=="180" and w3=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[7]
                    
                        exec(code_string)
                    
                        c.drawString(rect_x_position + 40, rect_y_position + 105 + ERROR, l1.rjust(6))  #trái
                        c.drawString(rect_x_position + 78, rect_y_position + 67 + ERROR, l2.center(6))  #giữa
                        c.drawString(rect_x_position + 111, rect_y_position + 105 + ERROR, l3) #phải

        #TH6    BF2D@Hj@r@i@p1@l2158@n1@e3.37@d16@gSD295@s80@v@a@Gl218@w90@l1800@w90@l218@w0@C90@ 
                    elif count_l == 4 and count_w == 3 and w1=="90" and w2=="90" and w3=="0":

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[6]
                    
                        exec(code_string)
                    
                        c.drawString(rect_x_position + 8, rect_y_position + 63 + ERROR, l1.rjust(6))  #trái
                        c.drawString(rect_x_position + 78, rect_y_position + 81 + ERROR, l2.center(6))  #giữa
                        c.drawString(rect_x_position + 142, rect_y_position + 63 + ERROR, l3) #phải 

            #TH5    BF2D@Hj@r@i@p1@l1057@n1@e1.05@d13@gSD295@s39@v@a@Gl111@w135@l950@w0@C77@    
                    elif count_l == 3 and count_w == 2 and 90 < int(w1) < 180 and int(w2) == 0: 

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[5]
                    
                        exec(code_string)
                    
                        if int(l1) > int(l2):
                            c.drawString(rect_x_position + 21, rect_y_position + 90 + ERROR, l2.rjust(6))
                            c.drawString(rect_x_position + 80, rect_y_position + 67 + ERROR, l1.center(6))
                        else:
                            c.drawString(rect_x_position + 21, rect_y_position + 90 + ERROR, l1.rjust(6))
                            c.drawString(rect_x_position + 80, rect_y_position + 67 + ERROR, l2.center(6))

            #TH4    BF2D@Hj@r@i@p1@l2088@n1@e4.7@d19@gSD345@s114@v@a@Gl600@w45@l1500@w0@C76@    
                    elif count_l == 3 and count_w == 2 and 0 < int(w1) < 90 and int(w2) == 0 :  

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[4]
                    
                        exec(code_string)
                    
                        if int(l1) > int(l2):
                            c.drawString(rect_x_position + 23, rect_y_position + 67 + ERROR, l2.rjust(6))
                            c.drawString(rect_x_position + 85, rect_y_position + 81 + ERROR, l1.center(6))
                        else:
                            c.drawString(rect_x_position + 23, rect_y_position + 67 + ERROR, l1.rjust(6))
                            c.drawString(rect_x_position + 85, rect_y_position + 81 + ERROR, l2.center(6))                  

            #TH3    BF2D@Hj@r@i@p1@l1744@n1@e5.3@d22@gSD345@s88@v@a@Gl204@w180@l1500@w0@C77@    
                    elif count_l == 3 and count_w == 2 and w1=="180" and w2=="0": 

                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        

                        img_path = image_list[3]
                    
                        exec(code_string)
                    
                        if int(l1) > int(l2):
                            c.drawString(rect_x_position + 80, rect_y_position + 67 + ERROR, l1.center(6))
                            c.drawString(rect_x_position + 40, rect_y_position + 105 + ERROR, l2.rjust(6))
                        else:
                            c.drawString(rect_x_position + 80, rect_y_position + 67 + ERROR, l2.center(6))
                            c.drawString(rect_x_position + 40, rect_y_position + 105 + ERROR, l1.rjust(6))

            #TH2    BF2D@Hj@r@i@p1@l1979@n1@e3.09@d16@gSD295@s80@v@a@Gl218@w90@l1800@w0@C88@    
                    elif count_l == 3 and count_w == 2 and w1=="90" and w2=="0": 
                        
                        value001_str = str(value001)  

                        result = extract_numbers(value001_str)

                        
                        
                        img_path = image_list[2]
                    
                        exec(code_string)
                        if int(l1) > int(l2):
                            c.drawString(rect_x_position + 8, rect_y_position + 62 + ERROR, l2.rjust(6))
                            c.drawString(rect_x_position + 79, rect_y_position + 81 + ERROR, l1.center(6))
                        else:
                            c.drawString(rect_x_position + 8, rect_y_position + 62 + ERROR, l1.rjust(6))
                            c.drawString(rect_x_position + 79, rect_y_position + 81 + ERROR, l2.center(6))

            #TH1    BF2D@Hj@r@i@p1@l2250@n1@e14.02@d32@gSD390@s@v@a@Gl2250@w0@C83@
                    elif count_l == 2 and count_w == 1 and w1=="0":                         

                        value001_str = str(value001)

                        result = extract_numbers(value001_str)
                        img_path = image_list[1]
                        exec(code_string)
                        c.drawString(rect_x_position + 79, rect_y_position + 81 + ERROR, l1.center(6))
            #TH0
                    else:
                        value001_str = str(value001) 
                        result = extract_numbers(value001_str)
                        c.setFont('msmincho.ttc', 10)
                        c.drawString(rect_x_position + 110, rect_y_position + 134, 'mm') #
                        c.drawString(rect_x_position + 165, rect_y_position + 132, '本')
                        if result['s'] == "":
                            c.drawString(rect_x_position + 210, rect_y_position + 128, '')
                        else:
                            c.drawString(rect_x_position + 210, rect_y_position + 128, 'ピン＝')
                        c.setFont('msmincho.ttc', 16)
                        c.drawString(rect_x_position + 15, rect_y_position + 120, "D" + result['d'])
                        c.drawString(rect_x_position + 80, rect_y_position + 120, result['l'])
                        c.drawString(rect_x_position + 152, rect_y_position + 120, result['n'])

                        c.setFont('msmincho.ttc', 10)
                        c.drawString(rect_x_position + 243, rect_y_position + 128, result['s'])
                        c.drawString(rect_x_position + 243, rect_y_position + 128, a)
                        c.setFont('msmincho.ttc', 20)
                        c.drawString(rect_x_position + 70, rect_y_position + 70, "非定型")  #giữa
#######################################################################################################           
                    # Thêm nội dung văn bản vào hình chữ nhật từ danh sách text_list
                    c.setFont('msmincho.ttc', 13)
                    c.drawString(rect_x_position + x1, rect_y_position + y1, text11)
                    c.drawString(rect_x_position + x2, rect_y_position + y2, text22)
                    #Lệnh canh lề phải trong pdf
                    c.drawRightString(rect_x_position + x3, rect_y_position + y3, text33)
                    c.drawRightString(rect_x_position + x4, rect_y_position + y4, text44)
                    

                    # Thiết lập múi giờ
                    desired_timezone = 'Asia/Tokyo'
                    # Tạo đối tượng múi giờ
                    desired_tz = pytz.timezone(desired_timezone)
                    # Lấy thời gian hiện tại theo múi giờ đã thiết lập
                    current_time = datetime.now(desired_tz)
                    # Định dạng và hiển thị thời gian
                    formatted_time = current_time.strftime("%Y/%m/%d")
                    time1 = current_time.strftime("%H:%M:%S")
                    c.setFont('msmincho.ttc', 10)
                    c.drawString(rect_x_position + 202, rect_y_position + 8, formatted_time)

                    # Di chuyển đến vị trí tiếp theo
                    rect_x_position += rect_width + x_spacing
                    rects_on_page += 1

                    # Kiểm tra nếu đã in đủ 2 hình từ trái sang phải, thì xuống hàng mới
                    if rects_on_page % 2 == 0:
                        rect_x_position = initial_rect_x_position
                        rect_y_position -= rect_height + y_spacing

                    # Tăng biến đếm NO
                    no += 1

                    # Kiểm tra nếu đã in đủ 4 hình từ trên xuống dưới, thì thêm trang mới
                    if rects_on_page >= 8:
                        c.showPage()  # Thêm trang mới
                        
                        rect_x_position = initial_rect_x_position
                        rect_y_position = initial_rect_y_position
                        rects_on_page = 0
                        
                        #no = 1  # Đặt lại biến đếm NO

                # Đặt vị trí và in văn bản
                #c.drawString(-10, -10, text_content)
                # Lưu PDF
                c.save()
                buffer.seek(0)
                return buffer
            
            # Hàm để tạo PDF với hình chữ nhật và hình ảnh
            def create_pdf1(text11,text22, text44, text55, text66):
                buffer = BytesIO()
                p = canvas.Canvas(buffer, pagesize=A4)
                # Kích thước mới của hình ảnh (đơn vị điểm)
                new_width = 60  # Đặt chiều rộng mới
                new_height = 30  # Đặt chiều cao mới
                rects_on_page1 = 0
                E = 0
                y1 = 25
                cao = 1.9
                NO1 = 1
                border_width1 = 1.5
                K = 1
                # Tạo danh sách các hình chữ nhật: (x_cm, y_cm, width_cm, height_cm)
                rectangles = [
                    (0.6, 27.9, 19.85, 1.5),
                    (0.6, 26.9, 2, 1),
                    (2.6, 26.9, 2, 1),
                    (4.6, 26.9, 2, 1),
                    (6.6, 26.9, 2, 1),
                    (8.6, 26.9, 2, 1),
                    (10.6, 26.9, 2, 1),
                    (12.6, 26.9, 4, 1),  # Hình chữ nhật này chứa hình ảnh
                    (16.6, 26.9, 1.7, 1),
                    (18.3, 26.9, 2.15, 1),
                ]
                # Tạo danh sách các hình chữ nhật: (x_cm, y_cm, width_cm, height_cm)
                rectangles1 = [    
                    (0.6, y1, 2, cao),
                    (2.6, y1, 2, cao),
                    (4.6, y1, 2, cao),
                    (6.6, y1, 2, cao),
                    (8.6, y1, 2, cao),
                    (10.6, y1, 2, cao),
                    (12.6, y1, 4, cao),  # Hình chữ nhật này chứa hình ảnh
                    (16.6, y1, 1.7, cao),
                    (18.3, y1, 2.15, cao)
                ]
                
                for x_cm, y_cm, width_cm, height_cm in rectangles:
                    # Vẽ các hình chữ nhật
                    exec(code_string1)
                    
                # Xét chuỗi BBVS
                for value001 in dfsnet["BVBS"]:
                    value001_str = str(value001)
                    
                    # Sử dụng biểu thức chính quy để tìm số sau "SD" đến ký tự "@"
                    数量 = r'SD(\d+\.\d+|\d+)@'
                    # Tìm tất cả các kết quả phù hợp với biểu thức chính quy
                    数量1 = re.findall(数量 , value001_str)

                    # Sử dụng biểu thức chính quy để tìm số sau "SD" (bao gồm cả số thập phân)
                    ee = r'e(\d+\.\d+|\d+)@'
                    # Tìm kết quả phù hợp với biểu thức chính quy
                    number = re.search(ee, value001_str)
                    ee1 = number.group(1)
                    
                    count_l = value001.count('l')
                    count_w = value001.count('w')
                    w1, w2, w3, w4, w5, w6, w7 = process_data1(value001_str)
                    result = extract_numbers(value001_str)
                    l1, l2, l3, l4, l5, l6, l7 = process_data(value001_str)
    #TH60   BF2D@Hj@r@i@p1@l11680@n5@e58.11@d13@gSD295@s52@v@a@Gl1500@w90@l1300@w76@l2250@w14@l1680@w14@l2250@w76@l1300@w90@l1500@w0@C82@
                    if count_l == 8 and count_w == 7 and w1=="90" and 0 < int(w2) < 90 and 0 < int(w3) < 90 and 0 < int(w4) < 90 and 0 < int(w5) < 90 and w6=="90" and w7=="0":
                        img_path = image_list[60]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        
                        p.drawRightString(13.95 * 28.3465, (y1 + 0.15) * 28.3465 , l1)
                        p.drawRightString(13.55 * 28.3465, (y1 + 0.75) * 28.3465 , l2) #p.drawCentredString
                        p.drawRightString(13.95 * 28.3465, (y1 + 1.36) * 28.3465 , l3) #p.drawRightString

                        p.drawCentredString(14.6 * 28.3465, (y1 + 1.51) * 28.3465 , l4) #p.drawRightString

                        p.drawString(15.25 * 28.3465, (y1 + 1.36) * 28.3465 , l5) #p.drawRightString
                        p.drawString(15.65 * 28.3465, (y1 + 0.75) * 28.3465 , l6) #p.drawCentredString
                        p.drawString(15.28 * 28.3465, (y1 + 0.15) * 28.3465 , l7)

    #TH59   BF2D@Hj@r@i@p1@l1480@n1@e2.31@d16@gSD295@s80@v@a@Gl218@w90@l400@w90@l400@w90@l400@w-90@l218@w0@PtSEGOPT;o0;o1;o1;o0;o0@C82@            
                    elif count_l == 6 and count_w == 5 and (w1=="90" and w2=="90" and w3=="90" and w4=="-90" and w5=="0" and "PtSEGOPT" in value001 or w1=="90" and w2=="-90" and w3=="-90" and w4=="-90" and w5=="0" and "PtSEGOPT" in value001):
                        img_path = image_list[59]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)

                        p.drawRightString(14.15 * 28.3465, (y1 + 0.2) * 28.3465 , l1)
                        p.drawRightString(14.25 * 28.3465, (y1 + 0.9) * 28.3465 , l2) #p.drawCentredString
                        p.drawCentredString(14.63 * 28.3465, (y1 + 1.4) * 28.3465 , l3) #p.drawRightString
                        p.drawString(15 * 28.3465, (y1 + 0.85) * 28.3465 , l4) #p.drawCentredString
                        p.drawString(15 * 28.3465, (y1 + 0.2) * 28.3465 , l5)

    #TH58   BF2D@Hj@r@i@p1@l1480@n1@e2.31@d16@gSD295@s80@v@a@Gl218@w90@l400@w90@l400@w90@l400@w90@l218@w0@PtSEGOPT;o0;o1;o1;o0;o0@C95@
                    elif count_l == 6 and count_w == 5 and w1=="90" and w2=="90" and w3=="90" and w4=="90" and w5=="0" and "PtSEGOPT" in value001:
                        img_path = image_list[58]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        p.drawRightString(14.15 * 28.3465, (y1 + 0.3) * 28.3465 , l1)
                        p.drawRightString(14.3 * 28.3465, (y1 + 0.9) * 28.3465 , l2) #p.drawCentredString
                        p.drawCentredString(14.68 * 28.3465, (y1 + 1.49) * 28.3465 , l3) #p.drawRightString
                        p.drawString(15.06 * 28.3465, (y1 + 0.85) * 28.3465 , l4) #p.drawCentredString
                        p.drawString(14.8 * 28.3465, (y1 + 0.2) * 28.3465 , l5)

    #TH57   BF2D@Hj@r@i@p1@l1825@n1@e1.02@d10@gSD295@s30@v@a@Gl140@w101@l455@w79@l640@w90@l460@w-90@l200@w0@C96@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4=="-90" and w5=="0" or w1=="90" and w2=="-90" and -90 < int(w3) < 0 and -180 < int(w4) < -90  and w5=="0"):
                        img_path = image_list[57]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4=="-90" and w5=="0":
                            p.drawRightString(14.2 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.6 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.14 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                        else:
                            p.drawRightString(14.2 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.6 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.14 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
                        
    #TH56   BF2D@Hj@r@i@p1@l1865@n5@e5.22@d10@gSD295@s30@v@a@Gl140@w101@l455@w79@l640@w90@l460@w90@l240@w0@C91@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4=="90" and w5=="0" or w1=="90" and w2=="90" and 0 < int(w3) < 90 and 90 < int(w4) < 180  and w5=="0"):
                        img_path = image_list[56]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4=="90" and w5=="0":
                            p.drawRightString(14.2 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.9 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                        else:
                            p.drawRightString(14.2 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.9 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
                        
    #TH55   BF2D@Hj@r@i@p1@l1841@n1@e1.03@d10@gSD295@s30@v@a@Gl150@w79@l460@w-79@l640@w-90@l460@w90@l200@w0@C89@
                    elif count_l == 6 and count_w == 5 and (0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4=="90" and w5=="0" or w1=="90" and w2=="-90" and -90 < int(w3) < 0 and 0 < int(w4) < 90  and w5=="0"):
                        img_path = image_list[55]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4=="90" and w5=="0":
                            p.drawRightString(14 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(14.1 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.7 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.14 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                        else:
                            p.drawRightString(14 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(14.1 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.7 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.14 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
    #TH54   BF2D@Hj@r@i@p1@l2031@n1@e1.14@d10@gSD295@s30@v@a@Gl200@w90@l460@w90@l830@w79@l460@w-79@l150@w0@C75@
                    elif count_l == 6 and count_w == 5 and (0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4=="-90" and w5=="0" or w1=="90" and w2=="90" and 0 < int(w3) < 90 and -90 < int(w4) < 0  and w5=="0"):
                        img_path = image_list[54]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)

                        if 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4=="-90" and w5=="0":
                            p.drawRightString(14 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(14.07 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(15 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                        else:
                            p.drawRightString(14 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(14.07 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(15 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString

    #TH53   BF2D@Hj@r@i@p1@l1924@n1@e1.08@d10@gSD295@s30@v@a@Gl200@w106@l470@w74@l700@w79@l460@w-79@l150@w0@C81@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and 0 < int(w3) < 90 and -90 < int(w4) < 0 and w5=="0" or 0 < int(w1) < 90 and -90 < int(w2) < 0 and -90 < int(w3) < 0 and -180 < int(w4) < -90 and w5=="0"):
                        img_path = image_list[53]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and 0 < int(w3) < 90 and -90 < int(w4) < 0 and w5=="0":
                            p.drawRightString(14.15 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(14.17 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.8 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.55 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(15 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(14.15 * 28.3465, (y1 + 1.54) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(14.17 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.8 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawString(15.55 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawString(15 * 28.3465, (y1 + 1.54) * 28.3465 , l5) #p.drawRightString
                            
    #TH52   BF2D@Hj@r@i@p1@l1770@n2@e1.98@d10@gSD295@s30@v@a@Gl87@w180@l450@w90@l650@w90@l450@w-90@l180@w0@C85@
                    elif count_l == 6 and count_w == 5 and (w1=="180" and w2=="90" and w3=="90" and w4=="-90" and w5=="0" or w1=="90" and w2=="-90" and w3=="-90" and w4=="-180" and w5=="0"):
                        img_path = image_list[52]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if w1=="180" and w2=="90" and w3=="90" and w4=="-90" and w5=="0":
                            p.drawRightString(14.15 * 28.3465, (y1 + 1.50) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(14.15 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.87 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.1) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(14.15 * 28.3465, (y1 + 1.50) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(14.15 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.87 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.1) * 28.3465 , l5) #p.drawRightString
    #TH51   BF2D@Hj@r@i@p1@l1766@n3@e2.97@d10@gSD295@s30@v@a@Gl100@w135@l450@w90@l650@w90@l450@w-90@l180@w0@C77@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="-90" and w5=="0" or w1=="90" and w2=="-90" and w3=="-90" and -180 < int(w4) < -90 and w5=="0"):
                        img_path = image_list[51]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="-90" and w5=="0":
                            p.drawRightString(14.15 * 28.3465, (y1 + 1.52) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(14.15 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.87 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.25) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(14.15 * 28.3465, (y1 + 1.52) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(14.15 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.87 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.25) * 28.3465 , l5) #p.drawRightString
    #TH50   BF2D@Hj@r@i@p1@l1740@n3@e2.92@d10@gSD295@s30@v@a@Gl87@w180@l450@w90@l650@w90@l450@w90@l150@w0@C76@
                    elif count_l == 6 and count_w == 5 and (w1=="180" and w2=="90" and w3=="90" and w4=="90" and w5=="0" or w1=="90" and w2=="90" and w3=="90" and w4=="180" and w5=="0"):
                        img_path = image_list[50]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if w1=="180" and w2=="90" and w3=="90" and w4=="90" and w5=="0":
                            p.drawRightString(14.16 * 28.3465, (y1 + 1.51) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.68 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.1) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(14.16 * 28.3465, (y1 + 1.51) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.68 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.1) * 28.3465 , l5) #p.drawRightString
    #TH49   BF2D@Hj@r@i@p1@l1736@n1@e0.97@d10@gSD295@s30@v@a@Gl100@w135@l450@w90@l650@w90@l450@w90@l150@w0@C68@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="90" and w5=="0" or w1=="90" and w2=="90" and w3=="90" and 90 < int(w4) < 180 and w5=="0"):
                        img_path = image_list[49]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="90" and w5=="0":
                            p.drawRightString(14.16 * 28.3465, (y1 + 1.51) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.68 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.25) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(14.16 * 28.3465, (y1 + 1.51) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.68 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.25) * 28.3465 , l5) #p.drawRightString
    #TH48   BF2D@Hj@r@i@p1@l1706@n1@e0.96@d10@gSD295@s30@v@a@Gl100@w135@l450@w90@l650@w90@l450@w180@l87@w0@C95@
                    elif count_l == 6 and count_w == 5 and (90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="180" and w5=="0" or w1=="180" and w2=="90" and w3=="90" and 90 < int(w4) < 180 and w5=="0"):
                        img_path = image_list[48]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and w2=="90" and w3=="90" and w4=="180" and w5=="0":
                            p.drawString(13.88 * 28.3465, (y1 + 1.16) * 28.3465 , l5) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.67 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.25) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawString(13.88 * 28.3465, (y1 + 1.16) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.67 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l4) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.25) * 28.3465 , l5) #p.drawRightString
    #TH47   BF2D@Hj@r@i@p1@l1377@n1@e0.77@d10@gSD295@s30@v@a@Gl87@w180@l400@w90@l500@w76@l410@w0@C84@
                    elif count_l == 5 and count_w == 4 and (w1 =="180" and w2 =="90" and 0 < int(w3) < 90 and w4 =="0" or 0 < int(w1) < 90 and w2 =="90" and w3=="180" and w4=="0"):
                        img_path = image_list[47]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if w1 =="180" and w2 =="90" and 0 < int(w3) < 90 and w4 =="0":
                            p.drawRightString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.89 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.1) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #p.drawCentredString
                            p.drawCentredString(14.89 * 28.3465, (y1 + 0.14) * 28.3465 , l2)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l3) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.1) * 28.3465 , l4) #p.drawRightString
    #TH46   BF2D@Hj@r@i@p1@l1373@n1@e0.77@d10@gSD295@s30@v@a@Gl100@w135@l400@w90@l500@w76@l410@w0@C86@
                    elif count_l == 5 and count_w == 4 and (90 < int(w1) < 180 and w2 =="90" and 0 < int(w3) < 90 and w4 =="0" or 0 < int(w1) < 90 and w2 =="90" and 90 < int(w3) < 180 and w4=="0"):
                        img_path = image_list[46]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and w2 =="90" and 0 < int(w3) < 90 and w4 =="0":
                            p.drawRightString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.89 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.37 * 28.3465, (y1 + 1.28) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #p.drawCentredString
                            p.drawCentredString(14.89 * 28.3465, (y1 + 0.14) * 28.3465 , l2)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l3) #p.drawCentredString
                            p.drawRightString(15.37 * 28.3465, (y1 + 1.28) * 28.3465 , l4) #p.drawRightString
    #TH45   BF2D@Hj@r@i@p1@l1460@n1@e0.82@d10@gSD295@s30@v@a@Gl87@w180@l400@w90@l600@w90@l400@w0@C67@
                    elif count_l == 5 and count_w == 4 and (w1=="180" and w2 =="90" and w3=="90" and w4 =="0" or w1=="90" and w2 =="90" and w3=="180" and w4=="0"):
                        img_path = image_list[45]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if w1=="180" and w2 =="90" and w3=="90" and w4 =="0":
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.6 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.1) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #p.drawCentredString
                            p.drawCentredString(14.6 * 28.3465, (y1 + 0.14) * 28.3465 , l2)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l3) #p.drawCentredString
                            p.drawRightString(15.35 * 28.3465, (y1 + 1.1) * 28.3465 , l4) #p.drawRightString
    #TH44   BF2D@Hj@r@i@p1@l1456@n1@e0.82@d10@gSD295@s30@v@a@Gl100@w135@l400@w90@l600@w90@l400@w0@C92@
                    elif count_l == 5 and count_w == 4 and (90 < int(w1) < 180 and w2 =="90" and w3=="90" and w4 =="0" or w1=="90" and w2 =="90" and 90 < int(w3) < 180 and w4=="0"):
                        img_path = image_list[44]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and w2 =="90" and w3=="90" and w4 =="0":
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawCentredString(14.6 * 28.3465, (y1 + 0.14) * 28.3465 , l3)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(15.37 * 28.3465, (y1 + 1.28) * 28.3465 , l1) #p.drawRightString
                        else:
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #p.drawCentredString
                            p.drawCentredString(14.6 * 28.3465, (y1 + 0.14) * 28.3465 , l2)
                            p.drawString(15.65 * 28.3465, (y1 + 0.84) * 28.3465 , l3) #p.drawCentredString
                            p.drawRightString(15.37 * 28.3465, (y1 + 1.28) * 28.3465 , l4) #p.drawRightString
    #TH43   BF2D@Hj@r@i@p1@l1539@n1@e0.86@d10@gSD295@s30@v@a@Gl231@w25@l500@w-90@l350@w-90@l500@w0@C69@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and w2 =="-90" and w3=="-90" and w4 =="0" or w1=="90" and w2 =="90" and -90 < int(w3) < 0 and w4=="0"):
                        img_path = image_list[43]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 0 < int(w1) < 90 and w2 =="-90" and w3=="-90" and w4 =="0":
                            p.drawCentredString(14.3 * 28.3465, (y1 + 1.53) * 28.3465 , l4) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.9) * 28.3465 , l3) #p.drawCentredString
                            p.drawCentredString(14.3 * 28.3465, (y1 + 0.36) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(15.26 * 28.3465, (y1 + 0.62) * 28.3465 , l1) #p.drawCentredString
                        else:
                            p.drawCentredString(14.3 * 28.3465, (y1 + 1.53) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.9) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.3 * 28.3465, (y1 + 0.36) * 28.3465 , l3) #p.drawCentredString
                            p.drawString(15.26 * 28.3465, (y1 + 0.62) * 28.3465 , l4) #p.drawCentredString

    #TH42   BF2D@Hj@r@i@p1@l1508@n1@e0.84@d10@gSD295@s30@v@a@Gl200@w23@l500@w90@l350@w90@l500@w0@C75@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and w2 =="90" and w3=="90" and w4 =="0" or w1=="90" and w2 =="90" and 0 < int(w3) < 90 and w4=="0"):
                        img_path = image_list[42]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 0 < int(w1) < 90 and w2 =="90" and w3=="90" and w4 =="0":
                            p.drawCentredString(14.3 * 28.3465, (y1 + 1.51) * 28.3465 , l4) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.9) * 28.3465 , l3) #p.drawCentredString
                            p.drawCentredString(14.15 * 28.3465, (y1 + 0.15) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 0.35) * 28.3465 , l1) #p.drawCentredString
                        else:
                            p.drawCentredString(14.3 * 28.3465, (y1 + 1.51) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.9) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.15 * 28.3465, (y1 + 0.15) * 28.3465 , l3) #p.drawCentredString
                            p.drawString(15.1 * 28.3465, (y1 + 0.35) * 28.3465 , l4) #p.drawCentredString
    #TH41   BF2D@Hj@r@i@p1@l1268@n1@e0.71@d10@gSD295@s30@v@a@Gl450@w65@l150@w25@l200@w90@l500@w0@C70@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and 0 < int(w2) < 90 and w3=="90" and w4 =="0" or w1=="90" and 0 < int(w2) < 90 and 0 < int(w3) < 90 and w4=="0"):
                        img_path = image_list[41]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 0 < int(w1) < 90 and 0 < int(w2) < 90 and w3=="90" and w4 =="0":
                            p.drawCentredString(14.3 * 28.3465, (y1 + 1.51) * 28.3465 , l4) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 1) * 28.3465 , l3) #p.drawCentredString
                            p.drawString(13.95 * 28.3465, (y1 + 0.65) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.9 * 28.3465, (y1 + 0.14) * 28.3465 , l1) #p.drawCentredString
                        else:
                            p.drawCentredString(14.3 * 28.3465, (y1 + 1.51) * 28.3465 , l1) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 1) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(13.95 * 28.3465, (y1 + 0.65) * 28.3465 , l3) #p.drawCentredString
                            p.drawCentredString(14.9 * 28.3465, (y1 + 0.14) * 28.3465 , l4) #p.drawCentredString
    #TH40   BF2D@Hj@r@i@p1@l1180@n1@e0.66@d10@gSD295@s30@v@a@Gl400@w106@l394@w74@l302@w90@l130@w0@C82@
                    elif count_l == 5 and count_w == 4 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4 =="0" or w1=="90" and 0 < int(w2) < 90 and 90 < int(w3) < 180 and w4=="0"):
                        img_path = image_list[40]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="90" and w4 =="0":
                            p.drawString(15.64 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #p.drawCentredString
                            p.drawRightString(14.85 * 28.3465, (y1 + 1.4) * 28.3465 , l2) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.73) * 28.3465 , l3) #p.drawCentredString
                            p.drawString(13.6 * 28.3465, (y1 + 0.15) * 28.3465 , l4)
                        else:
                            p.drawString(15.64 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawRightString(14.85 * 28.3465, (y1 + 1.4) * 28.3465 , l3) #p.drawRightString
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.73) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(13.6 * 28.3465, (y1 + 0.15) * 28.3465 , l1)
                            
    #TH39   BF2D@Hj@r@i@p1@l1058@n1@e0.59@d10@gSD295@s30@v@a@Gl400@w113@l250@w67@l300@w-90@l150@w0@C72@
                    elif count_l == 5 and count_w == 4 and (90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="-90" and w4 =="0" or w1=="90" and -90 < int(w2) < 0 and -180 < int(w3) < -90 and w4=="0"):
                        img_path = image_list[39]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="-90" and w4 =="0":
                            p.drawString(15.64 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #p.drawCentredString
                            p.drawRightString(15.2 * 28.3465, (y1 + 1.4) * 28.3465 , l2) #p.drawRightString
                            p.drawRightString(14.3 * 28.3465, (y1 + 0.73) * 28.3465 , l3) #p.drawCentredString
                            p.drawString(13.7 * 28.3465, (y1 + 0.15) * 28.3465 , l4)
                        else:
                            p.drawString(15.64 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString
                            p.drawRightString(15.2 * 28.3465, (y1 + 1.4) * 28.3465 , l3) #p.drawRightString
                            p.drawRightString(14.3 * 28.3465, (y1 + 0.73) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(13.7 * 28.3465, (y1 + 0.15) * 28.3465 , l1)
    #TH38   BF2D@Hj@r@i@p1@l1210@n1@e1.2@d13@gSD295@s39@v@a@Gl200@w90@l300@w-45@l250@w45@l500@w0@C84@
                    elif count_l == 5 and count_w == 4 and (w1=="90" and -90 < int(w2) < 0 and 0 < int(w3) < 90 and w4 =="0" or 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="90" and w4=="0"):
                        img_path = image_list[38]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if w1=="90" and -90 < int(w2) < 0 and 0 < int(w3) < 90 and w4 =="0":
                            p.drawRightString(13.55 * 28.3465, (y1 + 1.1) * 28.3465 , l1) #p.drawCentredString
                            p.drawString(13.75 * 28.3465, (y1 + 1) * 28.3465 , l2) #p.drawCentredString
                            p.drawRightString(14.45 * 28.3465, (y1 + 0.5) * 28.3465 , l3) #p.drawCentredString
                            p.drawString(14.85 * 28.3465, (y1 + 0.5) * 28.3465 , l4)
                        else:
                            p.drawRightString(13.55 * 28.3465, (y1 + 1.1) * 28.3465 , l4) #p.drawCentredString
                            p.drawString(13.75 * 28.3465, (y1 + 1) * 28.3465 , l3) #p.drawCentredString
                            p.drawRightString(14.45 * 28.3465, (y1 + 0.5) * 28.3465 , l2) #p.drawCentredString
                            p.drawString(14.85 * 28.3465, (y1 + 0.5) * 28.3465 , l1)

    #TH37   BF2D@Hj@r@i@p1@l1238@n1@e1.23@d13@gSD295@s39@v@a@Gl400@w66@l300@w-66@l250@w-59@l325@w0@C88@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and -90 < int(w2) < 0 and -90 < int(w3) < 0 and w4 =="0" or 0 < int(w1) < 90 and 0 < int(w2) < 90 and -90 < int(w3) < 0 and w4=="0"):
                        img_path = image_list[37]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 0 < int(w1) < 90 and -90 < int(w2) < 0 and -90 < int(w3) < 0 and w4 =="0":
                            p.drawString(15 * 28.3465, (y1 + 1.53) * 28.3465 , l1) #p.drawRightString
                            p.drawString(14.9 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(14.3 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawRightString(13.72 * 28.3465, (y1 + 0.73) * 28.3465 , l4) #p.drawCentredString
                            
                        else:
                            p.drawString(15 * 28.3465, (y1 + 1.53) * 28.3465 , l4) #p.drawRightString
                            p.drawString(14.9 * 28.3465, (y1 + 0.8) * 28.3465 , l3) #p.drawCentredString
                            p.drawCentredString(14.3 * 28.3465, (y1 + 0.15) * 28.3465 , l2)
                            p.drawRightString(13.72 * 28.3465, (y1 + 0.73) * 28.3465 , l1) #p.drawCentredString
    #TH36    BF2D@Hj@r@i@p1@l1187@n1@e1.18@d13@gSD295@s39@v@a@Gl400@w66@l308@w-66@l250@w-90@l280@w0@C78@
                    elif count_l == 5 and count_w == 4 and (0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4 =="0" or w1=="90" and 0 < int(w2) < 90 and -90 < int(w3) < 0 and w4=="0"):
                        img_path = image_list[36]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="-90" and w4 =="0":
                            p.drawString(14.9 * 28.3465, (y1 + 1.53) * 28.3465 , l1) #p.drawRightString
                            p.drawString(14.58 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #p.drawCentredString
                            p.drawCentredString(13.89 * 28.3465, (y1 + 0.15) * 28.3465 , l3)
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #p.drawCentredString    
                        else:
                            p.drawString(14.9 * 28.3465, (y1 + 1.53) * 28.3465 , l4) #p.drawRightString
                            p.drawString(14.58 * 28.3465, (y1 + 0.8) * 28.3465 , l3) #p.drawCentredString
                            p.drawCentredString(13.89 * 28.3465, (y1 + 0.15) * 28.3465 , l2)
                            p.drawRightString(13.55 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #p.drawCentredString
                   
    #TH35               
                    elif count_l == 7 and count_w == 6 and w1=="135" and w2=="90" and w3=="90" and w4=="90" and w5=="135" and w6=="0":
                        img_path = image_list[35]
                        exec(code_string2)
                        p.setFont('msmincho.ttc', 10)
                        if int(l2) >= int(l3):
                            p.drawString(14.4 * 28.3465, (y1 + 1) * 28.3465 , l1.rjust(5))

                            p.drawString(14.2 * 28.3465, (y1 + 1.55) * 28.3465 , l2.center(6))
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l3.rjust(5))
                            p.drawString(14.2 * 28.3465, (y1 + 0.1) * 28.3465 , l4.center(6))
                            p.drawString(15.7 * 28.3465, (y1 + 0.8) * 28.3465 , l5) 
                        else:
                            p.drawString(14.4 * 28.3465, (y1 + 1) * 28.3465 , l1.rjust(5))

                            p.drawString(14.2 * 28.3465, (y1 + 1.55) * 28.3465 , l5.center(6))
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l4.rjust(5))
                            p.drawString(14.2 * 28.3465, (y1 + 0.1) * 28.3465 , l3.center(6))
                            p.drawString(15.7 * 28.3465, (y1 + 0.8) * 28.3465 , l2)
    #TH34           
                    elif count_l == 6 and count_w == 5 and 0 < int(w1) < 90 and -90 < int(w2) < 0 and -90 < int(w3) < 0 and 0 < int(w4) < 90 and w5=="0":
                        img_path = image_list[34]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(13.3 * 28.3465, (y1 + 1.52) * 28.3465 , l1.rjust(5)) #l1.rjust(5)
                        p.drawString(13.3 * 28.3465, (y1 + 0.9) * 28.3465 , l2.rjust(5)) #
                        p.drawString(14.2 * 28.3465, (y1 + 0.15) * 28.3465 , l3.center(6)) #
                        p.drawString(15.05 * 28.3465, (y1 + 0.9) * 28.3465 , l4) #phải 1 giữa
                        p.drawString(15.05 * 28.3465, (y1 + 1.52) * 28.3465 , l5) #trên phải
                        
    #TH33   BF2D@Hj@r@i@p1@l1719@n1@e1.71@d13@gSD295@s39@v@a@Gl530@w90@l360@w90@l300@w90@l280@w-90@l350@w0@C95@   
                    elif count_l == 6 and count_w == 5 and (w1=="90" and w2=="90" and w3=="90" and w4=="-90" and w5=="0" or w1=="90" and w2=="-90" and w3=="-90" and w4=="-90" and w5=="0"):                        
                        img_path = image_list[33]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="90" and w2=="90" and w3=="90" and w4=="-90" and w5=="0":
                            p.drawString(13.8 * 28.3465, (y1 + 1.52) * 28.3465 , l1.center(6)) #l4.center(6)
                            p.drawString(12.68 * 28.3465, (y1 + 0.8) * 28.3465 , l2.rjust(5)) #1.rjust(5)
                            p.drawString(13.31 * 28.3465, (y1 + 0.15) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(14.3 * 28.3465, (y1 + 0.65) * 28.3465 , l4) #l4.center(6)                  
                            p.drawString(14.8 * 28.3465, (y1 + 1.15) * 28.3465 , l5) #1.rjust(5)
                        else:
                            p.drawString(13.8 * 28.3465, (y1 + 1.52) * 28.3465 , l5.center(6)) #l4.center(6)
                            p.drawString(12.68 * 28.3465, (y1 + 0.8) * 28.3465 , l4.rjust(5)) #1.rjust(5)
                            p.drawString(13.31 * 28.3465, (y1 + 0.15) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(14.3 * 28.3465, (y1 + 0.65) * 28.3465 , l2) #l4.center(6)                  
                            p.drawString(14.8 * 28.3465, (y1 + 1.15) * 28.3465 , l1) #1.rjust(5)

    #TH32   BF2D@Hj@r@i@p1@l1376@n1@e1.37@d13@gSD295@s39@v@a@Gl164@w90@l200@w90@l750@w90@l200@w90@l164@w0@C75@
                    elif count_l == 6 and count_w == 5 and w1=="90" and w2=="90" and w3=="90" and w4=="90" and w5=="0":
                        img_path = image_list[32]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)   
                        
                        p.drawString(13.35 * 28.3465, (y1 + 0.15) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                        p.drawString(12.68 * 28.3465, (y1 + 0.6) * 28.3465 , l2.rjust(5)) #1.rjust(5)
                        p.drawString(14.2 * 28.3465, (y1 + 1.05) * 28.3465 , l3.center(6)) #l4.center(6)
                        p.drawString(15.65 * 28.3465, (y1 + 0.6) * 28.3465 , l4) # 
                        p.drawString(14.95 * 28.3465, (y1 + 0.15) * 28.3465 , l5) #
    #TH31   BF2D@Hj@r@i@p1@l1202@n1@e0.67@d10@gSD295@s30@v@a@Gl100@w135@l210@w90@l630@w90@l210@w135@l100@w0@C86@
                    elif count_l == 6 and count_w == 5 and 90 < int(w1) < 180 and w2=="90" and w3=="90" and 90 < int(w4) < 180 and w5=="0":
                        img_path = image_list[31]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)    
                        p.drawString(13.8 * 28.3465, (y1 + 1.3) * 28.3465 , l1) #1.rjust(5)
                        p.drawString(12.67 * 28.3465, (y1 + 0.8) * 28.3465 , l2.rjust(5)   ) #1.rjust(5)   
                        p.drawString(14.2 * 28.3465, (y1 + 0.15) * 28.3465 , l3.center(6)) #l4.center(6)
                        p.drawString(15.65 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #
                        p.drawString(14.55 * 28.3465, (y1 + 1.3) * 28.3465 , l5.rjust(5)) #1.rjust(5)

    #TH30   BF2D@Hj@r@i@p1@l1140@n1@e0.64@d10@gSD295@s30@v@a@Gl87@w180@l340@w90@l300@w90@l340@w180@l87@w0@C90@
                    elif count_l == 6 and count_w == 5 and w1=="180" and w2=="90" and w3=="90" and w4=="180" and w5=="0":
                        img_path = image_list[30]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(13.87 * 28.3465, (y1 + 1.06) * 28.3465 , l1) #1.rjust(5)
                        p.drawString(12.67 * 28.3465, (y1 + 0.8) * 28.3465 , l2.rjust(5)   ) #1.rjust(5)   
                        p.drawString(14.2 * 28.3465, (y1 + 0.15) * 28.3465 , l3.center(6)) #l4.center(6)
                        p.drawString(15.65 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #
                        p.drawString(14.46 * 28.3465, (y1 + 1.06) * 28.3465 , l5.rjust(5)) #1.rjust(5)
                        
    #TH29   BF2D@Hj@r@i@p1@l1369@n1@e1.36@d13@gSD295@s39@v@a@Gl220@w90@l300@w-90@l300@w-90@l300@w90@l350@w0@C84@
                    elif count_l == 6 and count_w == 5 and w1=="90" and w2=="-90" and w3=="-90" and w4=="90" and w5=="0":
                        img_path = image_list[29]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10) 
                        p.drawString(13.35 * 28.3465, (y1 + 0.15) * 28.3465 , l1.rjust(5)) #1.rjust(5) 
                        p.drawString(13.25 * 28.3465, (y1 + 0.8) * 28.3465 , l2.rjust(5)) #1.rjust(5)  
                        p.drawString(14.15 * 28.3465, (y1 + 1.52) * 28.3465 , l3.center(6)) #l4.center(6)
                        p.drawString(15.08 * 28.3465, (y1 + 0.8) * 28.3465 , l4) #1.rjust(5)
                        p.drawString(15 * 28.3465, (y1 + 0.15) * 28.3465 , l5) #
    #TH28   BF2D@Hj@r@i@p1@l1181@n1@e0.66@d10@gSD295@s30@v@a@Gl150@w90@l300@w-90@l230@w90@l560@w0@C88@
                    elif count_l == 5 and count_w == 4 and w1 == "90" and w2 == "-90" and w3 == "90" and w4 == "0":
                        img_path = image_list[28]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)   
                        if int(l1) > int(l4):
                            p.drawString(14.6 * 28.3465, (y1 + 1.52) * 28.3465 , l1) #
                            p.drawString(14.3 * 28.3465, (y1 + 1) * 28.3465 , l2) #l4.center(6)
                            p.drawString(13.25 * 28.3465, (y1 + 0.87) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(12.68 * 28.3465, (y1 + 0.5) * 28.3465 , l4.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(14.6 * 28.3465, (y1 + 1.52) * 28.3465 , l4) #
                            p.drawString(14.3 * 28.3465, (y1 + 1) * 28.3465 , l3) #l4.center(6)
                            p.drawString(13.25 * 28.3465, (y1 + 0.87) * 28.3465 , l2.rjust(5)) #1.rjust(5)
                            p.drawString(12.68 * 28.3465, (y1 + 0.5) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH27   BF2D@Hj@r@i@p1@l1204@n1@e1.2@d13@gSD295@s39@v@a@Gl350@w90@l300@w90@l280@w-90@l350@w0@C69@
                    elif count_l == 5 and count_w == 4 and (w1=="90" and w2=="90" and w3=="-90" and w4=="0" or w1=="90" and w2=="-90" and w3=="-90" and w4=="0"):
                        img_path = image_list[27]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)  
                        if w1=="90" and w2=="90" and w3=="-90" and w4=="0":
                            p.drawString(14.6 * 28.3465, (y1 + 1.52) * 28.3465 , l4) #
                            p.drawString(14.3 * 28.3465, (y1 + 0.8) * 28.3465 , l3) #
                            p.drawString(13.48 * 28.3465, (y1 + 0.15) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l1.rjust(5) ) #1.rjust(5)        
                        else:
                            p.drawString(14.6 * 28.3465, (y1 + 1.52) * 28.3465 , l1) #
                            p.drawString(14.3 * 28.3465, (y1 + 0.8) * 28.3465 , l2) #
                            p.drawString(13.48 * 28.3465, (y1 + 0.15) * 28.3465 , l3.center(6)) #l4.center(6)
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l4.rjust(5) ) #1.rjust(5)
    #TH26   BF2D@Hj@r@i@p1@l1721@n1@e2.68@d16@gSD295@s80@v@a@Gl218@w90@l1070@w90@l300@w90@l250@w0@C66@
                    elif count_l == 5 and count_w == 4 and w1=="90" and w2=="90" and w3=="90" and w4=="0":
                        img_path = image_list[26]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if int(l2) > int(l3):
                            p.drawString(13.25 * 28.3465, (y1 + 1.52) * 28.3465 , l4.rjust(5)) #l1.rjust(5)
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 0.15) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.65 * 28.3465, (y1 + 0.6) * 28.3465 , l1) #
                        else:
                            p.drawString(13.25 * 28.3465, (y1 + 1.52) * 28.3465 , l1.rjust(5)) #l1.rjust(5)
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l2.rjust(5)) #1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 0.15) * 28.3465 , l3.center(6)) #l4.center(6)
                            p.drawString(15.65 * 28.3465, (y1 + 0.6) * 28.3465 , l4) #
    #TH25   BF2D@Hj@r@i@p1@l1164@n1@e1.16@d13@gSD295@s39@v@a@Gl112@w135@l950@w-135@l111@w0@C79@
                    elif count_l == 4 and count_w == 3 and 90 < int(w1) < 180 and -180 < int(w2) < -90 and w3=="0":
                        img_path = image_list[25]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(12.9 * 28.3465, (y1 + 0.5) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                        p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                        p.drawString(15.35 * 28.3465, (y1 + 1.2) * 28.3465 , l3) #

    #TH24   BF2D@Hj@r@i@p1@l1987@n1@e6.04@d22@gSD345@s88@v@a@Gl204@w180@l1500@w-180@l204@w0@C83@
                    elif count_l == 4 and count_w == 3 and w1=="180" and w2=="-180" and w3=="0":
                        img_path = image_list[24]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(13.35* 28.3465, (y1 + 1.52) * 28.3465 , l1.rjust(5)) #l1.rjust(5)
                        p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                        p.drawString(15 * 28.3465, (y1 + 0.15) * 28.3465 , l3) #
    #TH23   BF2D@Hj@r@i@p1@l1961@n1@e3.06@d16@gSD295@s80@v@a@Gl450@w67@l1050@w-67@l500@w0@C83@
                    elif count_l == 4 and count_w == 3 and 0 < int(w1) < 90 and -90 < int(w2) < 0 and w3=="0":
                        img_path = image_list[23]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(13.6 * 28.3465, (y1 + 1.52) * 28.3465 , l1) #l1.rjust(5)
                        p.drawString(14.68 * 28.3465, (y1 + 0.9) * 28.3465 , l2) #l4.center(6)
                        p.drawString(15 * 28.3465, (y1 + 0.15) * 28.3465 , l3) #
    #TH22   BF2D@Hj@r@i@p1@l2458@n1@e3.83@d16@gSD295@s80@v@a@Gl218@w90@l2100@w-90@l218@w0@C79@
                    elif count_l == 4 and count_w == 3 and w1=="90" and w2=="-90" and w3=="0":
                        img_path = image_list[22]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(12.63 * 28.3465, (y1 + 1.11) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                        p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                        p.drawString(15.7 * 28.3465, (y1 + 0.55) * 28.3465 , l3) #
    #TH21   BF2D@Hj@r@i@p1@l1644@n1@e2.56@d16@gSD295@s80@v@a@Gl154@w135@l1300@w-45@l200@w0@C77@
                    elif count_l == 4 and count_w == 3 and (90 < int(w1) < 180 and -90 < int(w2) < 0 and w3=="0" or 0 < int(w1) < 90 and -180 < int(w2) < -90 and w3=="0"):
                        img_path = image_list[21]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if 90 < int(w1) < 180:
                            p.drawString(15.35 * 28.3465, (y1 + 1.2) * 28.3465 , l1) #
                            p.drawString(14.2 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.9 * 28.3465, (y1 + 0.8) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(15.35 * 28.3465, (y1 + 1.2) * 28.3465 , l3) #
                            p.drawString(14.2 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.9 * 28.3465, (y1 + 0.8) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH20   BF2D@Hj@r@i@p1@l1944@n1@e3.03@d16@gSD295@s80@v@a@Gl400@w78@l1000@w102@l600@w0@C67@
                    elif count_l == 4 and count_w == 3 and (0 < int(w1) < 90 and 90 < int(w2) < 180 and w3=="0" or 90 < int(w1) < 180 and 0 < int(w2) < 90 and w3=="0"):
                        img_path = image_list[20]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if 0 < int(w1) < 90:
                            p.drawString(12.65 * 28.3465, (y1 + 0.7) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 1.45) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.7 * 28.3465, (y1 + 0.8) * 28.3465 , l3) #
                        else:
                            p.drawString(12.65 * 28.3465, (y1 + 0.7) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 1.45) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.7 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #
    #TH19   BF2D@Hj@r@i@p1@l1970@n1@e3.07@d16@gSD295@s80@v@a@Gl122@w180@l1600@w-45@l220@w0@C78@
                    elif count_l == 4 and count_w == 3 and (w1=="180" and -90 < int(w2) < 0 and w3=="0" or 0 < int(w1) < 90 and w2=="-180" and w3=="0"):
                        img_path = image_list[19]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="180":
                            p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , l1) #
                            p.drawString(14.2 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.9 * 28.3465, (y1 + 0.63) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , l3) #
                            p.drawString(14.2 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.9 * 28.3465, (y1 + 0.63) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH18   BF2D@Hj@r@i@p1@l2441@n1@e7.42@d22@gSD345@s88@v@a@Gl204@w180@l2000@w45@l210@w0@C66@
                    elif count_l == 4 and count_w == 3 and (w1=="180" and 0 < int(w2) < 90 and w3=="0" or 0 < int(w1) < 90 and w2=="180" and w3=="0"):
                        img_path = image_list[18]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="180":
                            p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , l1) #
                            p.drawString(14.2 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.9 * 28.3465, (y1 + 1) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , l3) #
                            p.drawString(14.2 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.9 * 28.3465, (y1 + 1) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH17   BF2D@Hj@r@i@p1@l1477@n1@e1.47@d13@gSD295@s39@v@a@Gl86@w180@l1200@w135@l180@w0@C76@
                    elif count_l == 4 and count_w == 3 and (w1=="180" and 90 < int(w2) < 180 and w3=="0" or 90 < int(w1) < 180 and w2=="180" and w3=="0"):
                        img_path = image_list[17]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="180":
                            p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , l1) #
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.85 * 28.3465, (y1 + 1.16) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , l3) #
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.85 * 28.3465, (y1 + 1.16) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH16   BF2D@Hj@r@i@p1@l1267@n1@e1.26@d13@gSD295@s39@v@a@Gl86@w180@l1000@w-135@l170@w0@C72@
                    elif count_l == 4 and count_w == 3 and (w1=="180" and -180 < int(w2) < -90 and w3=="0" or 90 < int(w1) < 180 and w2=="-180" and w3=="0"):
                        img_path = image_list[16]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="180":
                            p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , l1) #
                            p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.9 * 28.3465, (y1 + 0.5) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(15 * 28.3465, (y1 + 1.52) * 28.3465 , l3) #
                            p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.9 * 28.3465, (y1 + 0.5) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH15   BF2D@Hj@r@i@p1@l1278@n1@e1.99@d16@gSD295@s80@v@a@Gl218@w90@l900@w-135@l200@w0@C78@
                    elif count_l == 4 and count_w == 3 and (w1=="90" and -180 < int(w2) < -90 and w3=="0" or 90 < int(w1) < 180 and w2=="-90" and w3=="0"):
                        img_path = image_list[15]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="90":
                            p.drawString(12.6 * 28.3465, (y1 + 0.6) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.35 * 28.3465, (y1 + 1.2) * 28.3465 , l3) #
                        else:
                            p.drawString(12.6 * 28.3465, (y1 + 0.6) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.35 * 28.3465, (y1 + 1.2) * 28.3465 , l1) #
    #TH14   BF2D@Hj@r@i@p1@l2489@n1@e3.88@d16@gSD295@s80@v@a@Gl218@w90@l1860@w-45@l460@w0@C91@
                    elif count_l == 4 and count_w == 3 and (w1=="90" and -90 < int(w2) < 0 and w3=="0" or 0 < int(w1) < 90 and w2=="-90" and w3=="0"): 
                        img_path = image_list[14]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="90":
                            p.drawString(12.6 * 28.3465, (y1 + 0.6) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                            p.drawString(13.8 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.4 * 28.3465, (y1 + 1) * 28.3465 , l3) #
                        else:
                            p.drawString(12.6 * 28.3465, (y1 + 0.6) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(13.8 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.4 * 28.3465, (y1 + 1) * 28.3465 , l1) #
    #TH13   BF2D@Hj@r@i@p1@l2128@n1@e4.79@d19@gSD345@s114@v@a@Gl268@w90@l1700@w-180@l154@w0@C73@
                    elif count_l == 4 and count_w == 3 and (w1=="90" and w2=="-180" and w3=="0" or w1=="180" and w2=="-90" and w3=="0"):
                        img_path = image_list[13]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="90":
                            p.drawString(12.62 * 28.3465, (y1 + 0.6) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(14.95 * 28.3465, (y1 + 1.53) * 28.3465 , l3) #
                        else:
                            p.drawString(12.62 * 28.3465, (y1 + 0.6) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(14.95 * 28.3465, (y1 + 1.53) * 28.3465 , l1) #
    #TH12   BF2D@Hj@r@i@p1@l2248@n1@e3.51@d16@gSD295@s80@v@a@Gl218@w90@l1800@w135@l270@w0@C80@
                    elif count_l == 4 and count_w == 3 and (w1 == "90" and 90 < int(w2) < 180 and w3 == "0" or 90 < int(w1) < 180 and w2 == "90" and w3 == "0"):
                        img_path = image_list[12]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1 == "90":
                            p.drawString(15.69 * 28.3465, (y1 + 1.15) * 28.3465 , l1) #
                            p.drawString(14.2 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.8 * 28.3465, (y1 + 1.15) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(15.69 * 28.3465, (y1 + 1.15) * 28.3465 , l3) #
                            p.drawString(14.2 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.8 * 28.3465, (y1 + 1.15) * 28.3465 , l1.rjust(5) ) #1.rjust(5)         
    #TH11   BF2D@Hj@r@i@p1@l2559@n1@e7.78@d22@gSD345@s88@v@a@Gl311@w90@l2100@w45@l210@w0@C95@
                    elif count_l == 4 and count_w == 3 and (w1 == "90" and 0 < int(w2) < 90 and w3 =="0" or 0 < int(w1) < 90 and w2 =="90"  and w3=="0"):
                        img_path = image_list[11]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="90":
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                            p.drawString(13.8 * 28.3465, (y1 + 1.52) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.45 * 28.3465, (y1 + 0.8) * 28.3465 , l3) #
                        else:
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                            p.drawString(13.8 * 28.3465, (y1 + 1.52) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(15.45 * 28.3465, (y1 + 0.8) * 28.3465 , l1) #
    #TH10   BF2D@Hj@r@i@p1@l2105@n1@e6.4@d22@gSD345@s88@v@a@Gl204@w180@l1600@w90@l311@w0@C81@
                    elif count_l == 4 and count_w == 3 and (w1=="90" and w2=="180" and w3=="0" or w1=="180" and w2=="90" and w3=="0"):
                        img_path = image_list[10]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if w1=="180":
                            p.drawString(15 * 28.3465, (y1 + 0.63) * 28.3465 , l1) #
                            p.drawString(14.1 * 28.3465, (y1 + 1.52) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l3.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(15 * 28.3465, (y1 + 0.65) * 28.3465 , l3) #
                            p.drawString(14.1 * 28.3465, (y1 + 1.52) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.65 * 28.3465, (y1 + 0.8) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH9    BF2D@Hj@r@i@p1@l1514@n1@e2.36@d16@gSD295@s48@v@a@Gl138@w135@l1250@w135@l138@w0@C92@
                    elif count_l == 4 and count_w == 3 and 90 < int(w1) < 180 and 90 < int(w2) < 180 and w3=="0":
                        img_path = image_list[9]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(12.9 * 28.3465, (y1 + 0.5) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                        p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                        p.drawString(15.45 * 28.3465, (y1 + 0.5) * 28.3465 , l3) #

    #TH8    BF2D@Hj@r@i@p1@l2117@n1@e4.76@d19@gSD345@s114@v@a@Gl398@w85@l1509@w45@l265@w0@C89@
                    elif count_l == 4 and count_w == 3 and 0 < int(w1) < 90 and 0 < int(w2) < 90 and w3=="0":
                        img_path = image_list[8]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(12.9 * 28.3465, (y1 + 0.7) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                        p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                        p.drawString(15.45 * 28.3465, (y1 + 0.7) * 28.3465 , l3) #

    #TH7 BF2D@Hj@r@i@p1@l2300@n1@e1.29@d10@gSD295@s30@v@a@Gl87@w180@l2100@w180@l87@w0@C79@
                    elif count_l == 4 and count_w == 3 and w1=="180" and w2=="180" and w3=="0":
                        img_path = image_list[7]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(13.35 * 28.3465, (y1 + 1.52) * 28.3465 , l1.rjust(5)) #l1.rjust(5)
                        p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                        p.drawString(14.98 * 28.3465, (y1 + 1.52) * 28.3465 , l3) #

    #TH6    BF2D@Hj@r@i@p1@l2158@n1@e3.37@d16@gSD295@s80@v@a@Gl218@w90@l1800@w90@l218@w0@C90@ 
                    elif count_l == 4 and count_w == 3 and w1=="90" and w2=="90" and w3=="0":
                        img_path = image_list[6]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(12.6 * 28.3465, (y1 + 0.6) * 28.3465 , l1.rjust(5)) #1.rjust(5)
                        p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                        p.drawString(15.7 * 28.3465, (y1 + 0.6) * 28.3465 , l3) #

    #TH5    BF2D@Hj@r@i@p1@l1057@n1@e1.05@d13@gSD295@s39@v@a@Gl111@w135@l950@w0@C77@    
                    elif count_l == 3 and count_w == 2 and 90 < int(w1) < 180 and int(w2) == 0: 
                        img_path = image_list[5]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if int(l1) > int(l2):
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l1.center(6)) #l4.center(6)
                            p.drawString(12.8 * 28.3465, (y1 + 1.15) * 28.3465 , l2.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.8 * 28.3465, (y1 + 1.15) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH4    BF2D@Hj@r@i@p1@l2088@n1@e4.7@d19@gSD345@s114@v@a@Gl600@w45@l1500@w0@C76@    
                    elif count_l == 3 and count_w == 2 and 0 < int(w1) < 90 and int(w2) == 0 :  
                        img_path = image_list[4]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if int(l1) > int(l2):
                            p.drawString(14.4 * 28.3465, (y1 + 1.06) * 28.3465 , l1.center(6)) #l4.center(6)      
                            p.drawString(12.9 * 28.3465, (y1 + 0.7) * 28.3465 , l2.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(14.4 * 28.3465, (y1 + 1.06) * 28.3465 , l2.center(6) ) #l4.center(6)      
                            p.drawString(12.9 * 28.3465, (y1 + 0.7) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH3    BF2D@Hj@r@i@p1@l1744@n1@e5.3@d22@gSD345@s88@v@a@Gl204@w180@l1500@w0@C77@    
                    elif count_l == 3 and count_w == 2 and w1=="180" and w2=="0": 
                        img_path = image_list[3]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if int(l1) > int(l2):
                            p.drawString(13.35 * 28.3465, (y1 + 1.52) * 28.3465 , l2.rjust(5)) #l1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l1.center(6)) #l4.center(6)
                        else:
                            p.drawString(13.35 * 28.3465, (y1 + 1.52) * 28.3465 , l1.rjust(5)) #l1.rjust(5)
                            p.drawString(14.1 * 28.3465, (y1 + 0.63) * 28.3465 , l2.center(6)) #l4.center(6)
    #TH2    BF2D@Hj@r@i@p1@l1979@n1@e3.09@d16@gSD295@s80@v@a@Gl218@w90@l1800@w0@C88@    
                    elif count_l == 3 and count_w == 2 and w1=="90" and w2=="0": 
                        img_path = image_list[2]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        if int(l1) > int(l2):
                            p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l1.center(6)) #l4.center(6)
                            p.drawString(12.6 * 28.3465, (y1 + 0.6) * 28.3465 , l2.rjust(5)) #1.rjust(5)
                        else:
                            p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l2.center(6)) #l4.center(6)
                            p.drawString(12.6 * 28.3465, (y1 + 0.6) * 28.3465 , l1.rjust(5)) #1.rjust(5)
    #TH1    BF2D@Hj@r@i@p1@l2250@n1@e14.02@d32@gSD390@s@v@a@Gl2250@w0@C83@
                    elif count_l == 2 and count_w == 1 and w1=="0":                         
                        img_path = image_list[1]
                        exec(code_string2) 
                        p.setFont('msmincho.ttc', 10)
                        p.drawString(14.1 * 28.3465, (y1 + 1.05) * 28.3465 , l1.center(6)) #l4.center(6)
    #TH0
                    else:
                        for x_cm, y_cm, width_cm, height_cm in rectangles1:
                            # Chèn hình ảnh vào hình chữ nhật tại tọa độ và điều chỉnh kích thước
                            p.setLineWidth(border_width1)
                            # Vẽ các hình chữ nhật khác
                            p.rect(x_cm * 28.3465, y1 * 28.3465, width_cm * 28.3465, height_cm * 28.3465)
                            p.setFont('msmincho.ttc', 16) 
                            # Vẽ văn bản tiếng Nhật và tiếng Anh với kích thước font khác nhau
                            p.drawString(0.85 * 28.3465, (y1 + 0.7) * 28.3465 , (f'No.{NO1}').center(5))  #1
                            p.drawString(2.9 * 28.3465, (y1 + 0.7) * 28.3465 , ("D" + result['d']).center(5))  #2 
                            p.drawString(4.75 * 28.3465, (y1 + 0.7) * 28.3465 , (result['l']).center(5))  #3 
                            p.drawString(6.85 * 28.3465, (y1 + 0.7) * 28.3465 , (result['n']).center(5))  #4 
                            p.drawString(8.9 * 28.3465, (y1 + 0.7) * 28.3465 , "")  #5 
                            p.drawString(10.9 * 28.3465, (y1 + 0.7) * 28.3465 , ("SD" + 数量1[0]).center(5))  #6 
                            p.drawString(16.65 * 28.3465, (y1 + 0.7) * 28.3465 , (result['s']).center(5))  #8 
                            p.drawString(18.5 * 28.3465, (y1 + 0.7) * 28.3465 , ee1.center(5))   #9 
                            p.setFont('msmincho.ttc', 15) 
                            p.drawString(13.8 * 28.3465, (y1 + 0.8) * 28.3465 , "非定型")
###___PDF BẢNG____###################################################################################################################
                    rects_on_page1 += 1
                    y1 -= 1.9
                    E += 1
                    NO1 += 1
                    if rects_on_page1 == 14:
                        p.showPage()
                        rects_on_page1 = 0
                        y1 = 25
                    if  E >= 15:
                        K += 1
                        exec(code_string1)
                        E = 1
                p.save()
                buffer.seek(0)
                return buffer
#################################################################################################################################        
            # Danh sách điều kiện và đường dẫn đến các hình ảnh
            image_list = [
		        "image/0.png",
                "image/1.png",
                "image/2.png",
                "image/3.png",
                "image/4.png",
                "image/5.png",
                "image/6.png",
                "image/7.png",
                "image/8.png",
                "image/9.png",
                "image/10.png",
                "image/11.png",
                "image/12.png",
                "image/13.png",
                "image/14.png",
                "image/15.png",
                "image/16.png",
                "image/17.png",
                "image/18.png",
                "image/19.png",
                "image/20.png",
                "image/21.png",
                "image/22.png",
                "image/23.png",
                "image/24.png",
                "image/25.png",
                "image/26.png",
                "image/27.png",
                "image/28.png",
                "image/29.png",                              
                "image/30.png",
                "image/31.png",
                "image/32.png",
                "image/33.png",
                "image/34.png",
                "image/35.png",
                "image/36.png",
                "image/37.png",
                "image/38.png",
                "image/39.png",
                "image/40.png",
                "image/41.png",
                "image/42.png",
                "image/43.png",
                "image/44.png",
                "image/45.png",
                "image/46.png",
                "image/47.png",
                "image/48.png",
                "image/49.png",
                "image/50.png",
                "image/51.png",
                "image/52.png",
                "image/53.png",
                "image/54.png",
                "image/55.png",
                "image/56.png",
                "image/57.png",
                "image/58.png",
                "image/59.png",
                "image/60.png",
            ]
            st.subheader(' ', divider='rainbow')
            #st.write("------------------------------------------------------")
            st.title("情報を入力する")
            colA0, colA1, colA2, colA3, colA4, colA5, colA6 = st.columns(7)
            text11 = colA1.text_input("工事名", "某工事名")
            #text11 = st.text_input("工事名", "某工事名")
            text22 = colA2.text_input("協力会社", "株式会社ABC")
            text33 = colA3.text_input("鉄筋メーカー", "某会社")
            text44 = colA4.text_input("使用場所", "Y1-X1 柱")
            text55 = colA5.date_input('運搬日')

            x1, y1 = 3, 167 #
            x2, y2 = 3, 147
            x3, y3 = 266, 167
            x4, y4 = 266, 147

            selected_option = colA6.radio("", ["AM", "PM"])
            # Hiển thị thông báo dựa trên tùy chọn được chọn
            if selected_option == "AM":
                text66 = "AM"
            else:
                text66 = "PM"

            # Tạo PDF khi người dùng nhấn nút "Tạo PDF"
            st.subheader(' ', divider='rainbow')
            #st.write("------------------------------------------------------")
            st.title("エフ・加工帳 PDF出力")
            #st.markdown('<h1 style="text-align: center;">BVBSと加工帳のPDFを作成する</h1>', unsafe_allow_html=True)
            # Tạo hai cột với tỷ lệ chiều rộng 2:1
            col11, col22, col33, col44, col55, col66  = st.columns(6)

            if len(selected_rows):
                if col33.button("エフ.PDFを作成"):
                    pdf_buffer = create_pdf(dfs, image_list, text11, text22, text33, text44)
                    col33.download_button("Download エフ.pdf", pdf_buffer, file_name="エフ.pdf", key="download_pdf")
            if len(selected_rows):
                if col44.button("加工帳.PDFを作成"):
                    pdf_buffer = create_pdf1(text11, text22, text44, text55, text66)
                    col44.download_button("Download 加工帳.pdf", pdf_buffer, file_name="加工帳.pdf", key="download-pdf-button")
            st.subheader(' ', divider='rainbow')

if __name__ == "__main__":
    session = st.session_state
    main()
