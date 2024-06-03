import digitizerGUI
from digitizerGUI import DigitizerGUI

digitizer_instance = DigitizerGUI()
other_file_filename = digitizer_instance.filename

def xAndyValues():
    dialog = digitizerGUI.InputDialog()  # Создаем экземпляр класса InputDialog
    x, y = dialog.get_inputs()  # Вызываем метод get_inputs для получения x и y
    return float(x), float(y)