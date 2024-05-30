from datetime import datetime

def make_file_name(serial):
    now = datetime.now().strftime('%Y-%m-%dT%H:%M')
    file_name = str(serial)+'_'+now
    return file_name

