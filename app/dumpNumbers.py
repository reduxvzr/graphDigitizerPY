import digitizerGUI
from digitizerGUI import DigitizerGUI

digitizer_instance = DigitizerGUI()
other_file_filename = digitizer_instance.filename

def xAndyValues():
    dialog = digitizerGUI.InputDialog()  # Создаем экземпляр класса InputDialog
    x, y, name_x, name_y = dialog.get_inputs()  # Вызываем метод get_inputs для получения x, y и имен осей
    return float(x), float(y), name_x, name_y