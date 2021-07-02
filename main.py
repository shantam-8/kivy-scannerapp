# All libraries
from kivy.app import App
from kivy.core import text
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.graphics.texture import Texture
from pyzbar import pyzbar
import numpy as np
import cv2
import socket
import gspread
import numpy as np
from datetime import date, datetime


# All global variables
outputtext = ""
details = ["", ""]
flag = [""]

stone_in = TextInput(text=outputtext, size_hint=(None, 0.8), width=300, multiline=False, readonly=True)
width_in = TextInput(text=outputtext, size_hint=(None, 0.8), width=300, multiline=False, readonly=True)
length_in = TextInput(text=outputtext, size_hint=(None, 0.8), width=300, multiline=False, readonly=True)
breadth_in = TextInput(text=outputtext, size_hint=(None, 0.8), width=300, multiline=False, readonly=True)

found = set()

gc = gspread.service_account(
    filename="C:\\Users\\Shantam Gilra\\Desktop\\Coding\\App\\credentials.json"
)
wks = gc.open("Trial")


# All Pages
class FunctionPage(GridLayout):
    # runs on initialization
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        self.add = Button(text="Add Materials", on_release=lambda btn: self.add_button())
        self.add_widget(self.add)

        self.remove = Button(text="Remove Materials", on_release=lambda btn: self.remove_button())
        self.add_widget(self.remove)

    def add_button(self):  # Edit this
        flag[0] = "True"
        app_page.screen_manager.current = "Camera"

    def remove_button(self):  # Edit this
        flag[0] = "False"
        app_page.screen_manager.current = "Camera"


class WifiApp(FloatLayout):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.label = Label(
            halign="center",
            valign="middle",
            text="No internet connection is established. Please ensure you have a stable connection and press Retry."
            )
        self.label.bind(width=self.update_text_width)
        self.add_widget(self.label)
        button = Button(
            text="Retry",
            size_hint=(0.15, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
        )
        self.add_widget(button)
        button.bind(width=self.update_text_width, on_press=self.on_press_button)

    def update_text_width(self, *_):
        self.label.text_size = (self.label.width * 0.9, None)

    def on_press_button(self, *args):
        self.connection = is_connected()
        if self.connection == True:
            app_page.screen_manager.current = "Function"


class CamScreen(BoxLayout):
    # Camera Screen
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 1280)
        self.cam.set(4, 720)
        self.img = Image()

        self.exit = Button(
            text="Back",
            size_hint_y=None,
            height="48dp",
            on_press=self.stop_stream,
        )
        self.add_widget(self.img)
        self.add_widget(self.exit)
        Clock.schedule_interval(self.update, 1.0 / 30)

    def update(self, dt):
        if True:
            ret, frame = self.cam.read()

            if ret:
                buf1 = cv2.flip(frame, 0)
                buf = buf1.tostring()
                image_texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]), colorfmt="bgr"
                )
                image_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
                self.img.texture = image_texture

                barcodes = pyzbar.decode(frame)
                for barcode in barcodes:
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    barcodeData = barcode.data.decode("utf-8")
                    text = "{}".format(barcodeData)
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    if barcodeData not in found:
                        outputtext = text
                        data = outputtext.split("_", 4) #Barcode split into values for different parameters, assuming they are seperated by an underscore.  
                        stone_in.text = data[0]
                        width_in.text = data[1]
                        length_in.text = data[2]
                        breadth_in.text = data[3]
                        found.add(barcodeData)
                        self.change_screen()

    def stop_stream(self, *args):
        app_page.screen_manager.current = "Function"

    def change_screen(self, *args):
        app_page.screen_manager.current = "Detail"


class DetailPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2

        self.lab1 = Label(
            text="Information", size_hint_y=None, height="30dp", font_size="30dp"
        )
        self.lab1.bind(width=self.update_text_width)
        self.add_widget(self.lab1)
        self.add_widget(Label(size_hint=(None, 0.8), width=300))

        self.add_widget(Label(text="Material Name:", size_hint=(None, 0.8), width=300))
        self.add_widget(stone_in)

        self.add_widget(Label(text="Width (in cm):", size_hint=(None, 0.8), width=300))
        self.add_widget(width_in)

        self.add_widget(Label(text="Length (in cm):", size_hint=(None, 0.8), width=300))
        self.add_widget(length_in)

        self.add_widget(
            Label(text="Breadth (in cm):", size_hint=(None, 0.8), width=300)
        )
        self.add_widget(breadth_in)

        self.add_widget(
            Label(text="Number of pieces:", size_hint=(None, 0.8), width=300)
        )
        self.number_in = TextInput(size_hint=(None, 0.8), width=300, multiline=False)
        self.add_widget(self.number_in)


        self.add_widget(Label(text="Type: ", size_hint=(None, 0.8), width=300))

        dropdown = DropDown()
        types = ["Material Categorisation 1", "Material Categorisation 2", "Material Categorisation 3", "Material Categorisation 4"]

        for i in types:
            btn = Button(
                text="% s" % i,
                size_hint_y=None,
                on_release=lambda btn: self.text_store(btn.text, 0),
            )
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

        mainbtn = Button(text="Select Type", size_hint=(None, 0.8), width=300)
        mainbtn.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(mainbtn, "text", x))
        self.add_widget(mainbtn)


        self.add_widget(Label(text="Yard Number: ", size_hint=(None, 0.8), width=300))

        dropdown2 = DropDown()
        yards = ["Area of Loading 1", "Area of Loading 2", "Area of Loading 3"]

        for i in yards:
            btn = Button(
                text="% s" % i,
                size_hint_y=None,
                on_release=lambda btn: self.text_store(btn.text, 1),
            )
            btn.bind(on_release=lambda btn: dropdown2.select(btn.text))
            dropdown2.add_widget(btn)

        mainbtn2 = Button(text="Select Yard", size_hint=(None, 0.8), width=300)
        mainbtn2.bind(on_release=dropdown2.open)
        dropdown2.bind(on_select=lambda instance, x: setattr(mainbtn2, "text", x))
        self.add_widget(mainbtn2)

        # Adding Accept Details Button.
        self.accept = Button(text="Accept Details", size_hint=(None, 0.8), width=300)
        self.add_widget(Label())    # For organisation purposes.
        self.add_widget(self.accept)
        self.accept.bind(on_press=self.accept_func)

        # Adding Scanner Button.
        self.back = Button(text="Back to Scanner", size_hint=(None, 0.8), width=300)
        self.add_widget(Label())    # For organisation purposes.
        self.add_widget(self.back)
        self.back.bind(on_press=self.back_func)

    def update_text_width(self, *_):
        self.lab1.text_size = (self.lab1.width * 0.9, None)

    def back_func(self, *args):
        app_page.screen_manager.current = "Camera"
        found.clear()

    def text_store(self, val, index):
        details[index] = str(val)

    def accept_func(self, *args):

        if (
            (details[0] == "")
            or (details[1] == "")
            or (width_in.text.replace(" ", "").isnumeric() == False)
            or (length_in.text.replace(" ", "").isnumeric() == False)
            or (breadth_in.text.replace(" ", "").isnumeric() == False)
            or (self.number_in.text.replace(" ", "").isnumeric() == False)
        ):
            self.label_error = Label(
                text="Please fill the approporiate values for all fields.",
                halign="center",
                size_hint=(None, 0.8),
                width=500,
            )
            self.add_widget(self.label_error)
            Clock.schedule_once(lambda dt: self.remove_widget(self.label_error), 3)
        else:
            sort = [int(length_in.text), int(breadth_in.text)]
            sort.sort(reverse=True)
            detail = [
                stone_in.text.upper(), int(width_in.text), sort[0], sort[1], int(self.number_in.text),
                details[0], details[1], date.today().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M:%S"),
            ]
            yards = ["Area of Loading 1", "Area of Loading 2", "Area of Loading 3"]
            sheet = wks.get_worksheet(yards.index(detail[6]))

            if flag[0] == "True":
                data = np.array(sheet.get_all_values())
                for i in range(len(data[:,1])):
                    if list(data[i,:4]) == list(map(str, detail[:4])):
                        new_val = int(sheet.get(f'E{i+1}').first()) + detail[4]
                        sheet.update(f'E{i+1}', new_val)
                        wks.get_worksheet(3).append_row(detail)
                        found.clear()
                        app_page.screen_manager.current = "Success"
                        present = True
                    else:
                        present = False

                if present == False: 
                    sheet.append_row(detail[:-3])
                    wks.get_worksheet(3).append_row(detail)
                    found.clear()
                    app_page.screen_manager.current = "Success"
            
            if flag[0] == "False":
                data = np.array(sheet.get_all_values())
                for i in range(len(data[:,1])):
                    if list(data[i,:4]) == list(map(str, detail[:4])):
                        new_val = int(sheet.get(f'E{i+1}').first()) - detail[4]
                        if new_val < 0:
                            break
                        sheet.update(f'E{i+1}', new_val)
                        wks.get_worksheet(4).append_row(detail)
                        found.clear()
                        app_page.screen_manager.current = "Success"
                        present = True
                    else:
                        present = False

                if present == False:
                    found.clear()
                    app_page.screen_manager.current = "Error"


class SuccessPage(FloatLayout):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.label = Label(
            halign="center",
            valign="middle",
            text="Process was a success! Please click the button below to add/remove more items.")
        self.label.bind(width=self.update_text_width)
        self.add_widget(self.label)
        button = Button(
            text="Main Page",
            size_hint=(0.15, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
        )
        self.add_widget(button)
        button.bind(width=self.update_text_width, on_press=self.on_press_button)

    def update_text_width(self, *_):
        self.label.text_size = (self.label.width * 0.9, None)

    def on_press_button(self, *args):
        app_page.screen_manager.current = "Function"


class ErrorPage(FloatLayout):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.label = Label(
            halign="center",
            valign="middle",
            text="Materials of those dimensions are not present or are in lower quantities in the database. Please add it in the database by clicking the 'Add Materials' in the Main Page")
        self.label.bind(width=self.update_text_width)
        self.add_widget(self.label)
        button = Button(
            text="Main Page",
            size_hint=(0.15, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
        )
        self.add_widget(button)
        button.bind(width=self.update_text_width, on_press=self.on_press_button)

    def update_text_width(self, *_):
        self.label.text_size = (self.label.width * 0.9, None)

    def on_press_button(self, *args):
        app_page.screen_manager.current = "Function"


class Main(App):
    def build(self):

        self.screen_manager = ScreenManager()

        # Function Page
        self.connect_page = FunctionPage()
        screen = Screen(name="Function")
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        # Wifi Page
        self.wifi_app = WifiApp()
        screen = Screen(name="Wifi")
        screen.add_widget(self.wifi_app)
        self.screen_manager.add_widget(screen)

        # Camera Page
        self.cam_page = CamScreen()
        screen = Screen(name="Camera")
        screen.add_widget(self.cam_page)
        self.screen_manager.add_widget(screen)

        # Detail Page
        self.detail_page = DetailPage()
        screen = Screen(name="Detail")
        screen.add_widget(self.detail_page)
        self.screen_manager.add_widget(screen)

        # Success Page
        self.success_page = SuccessPage()
        screen = Screen(name="Success")
        screen.add_widget(self.success_page)
        self.screen_manager.add_widget(screen)

        # Error Page
        self.error_page = ErrorPage()
        screen = Screen(name="Error")
        screen.add_widget(self.error_page)
        self.screen_manager.add_widget(screen)


        if is_connected() == True:
            self.screen_manager.current = "Function"
        else:
            self.screen_manager.current = "Wifi"    #Page starts when there is no internet connection.

        return self.screen_manager

#Checks internet connection.
def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


if __name__ == "__main__":
    app_page = Main()
    app_page.run()
