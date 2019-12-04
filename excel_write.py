import xlwt
import os

folder = "data"
file_name = "sensor_data"

def init_excel():
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Sensor Data")

    bold_style = xlwt.easyxf('font: bold 1')

    first_col = sheet.col(0)
    second_col = sheet.col(1)

    first_col.width = 256 * 15
    second_col.width = 256 * 15

    sheet.write(0, 0, "Temp (" + u'\N{DEGREE SIGN}' + "C)", bold_style)
    sheet.write(0, 1, "Avg V", bold_style)

    return [sheet, workbook]

def get_file_list():
    file_list = []
    for file in os.listdir(folder):
        if file.endswith(".txt") and file.startswith(file_name):
            file_list.append(file)
    return file_list

def read_file(file):
    text_file = open(f"{folder}/{file}", "r")
    lines = text_file.readlines()
    lines.pop(0)
    return lines

def record_data(sheet, s, data_iter):
    sheet.write(data_iter + 1, 0, s[0:s.find(" ")])
    sheet.write(data_iter + 1, 1, s[s.rfind(" "):])

def save_data(workbook, file_iter):
    workbook.save(f"{folder}/{file_name}{file_iter}.xls")
    print("Data Saved!")

def main():
    file_list = get_file_list()
    for f in file_list:
        file_iter = f[f.find(file_name[-1])+3:f.find(".")]
        lines = read_file(f)
        sheet, workbook = init_excel()
        for idx, l in enumerate(lines):
            record_data(sheet, l, idx)
        save_data(workbook, file_iter)

main()