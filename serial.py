import os

def write_serial_file():
    folder_dir = './'
    folder_lists = os.listdir(folder_dir)

    serial = os.popen("cat /proc/cpuinfo | grep Serial | awk '{print $3}'")

    serial_file = open("./serial/serial.txt", "w")
    serial_num = serial.read()
    serial_file.write(serial_num)
    serial_file.close()
    return serial_num
