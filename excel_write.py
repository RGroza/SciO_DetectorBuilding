import xlwt
import os

workbook = xlwt.Workbook()
sheet = workbook.add_sheet("Sensor Data")

bold_style = xlwt.easyxf('font: bold 1')

first_col = sheet.col(0)
second_col = sheet.col(1)

first_col.width = 256 * 15
second_col.width = 256 * 15

sheet.write(0, 0, "Temp (" + u'\N{DEGREE SIGN}' + "C)", bold_style)
sheet.write(0, 1, "Avg V", bold_style)


def record_data(temp, v, data_iter):
    sheet.write(data_iter + 1, 0, str(temp))
    sheet.write(data_iter + 1, 1, str(v))
    print("Data written!")

def save_data():
    file_list = []
    for file in os.listdir("/data"):
        if file.endswith(".xls") and file.startswith("sensor_data"):
            file_list.append(file)
    file_iter = str(len(file_list)) if len(file_list) > 0 else ""
    workbook.save(f"data/sensor_data{file_iter}.xls")
    print("Data Saved!")