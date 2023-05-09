import os
import wx
import json
from datetime import datetime
import threading
import logging
from engine.engine import AcademiaBot

class MyFrame(wx.Frame):
    def __init__(self, parent, title, logger = None):
        super().__init__(parent, title=title, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)

        self.quit_event = threading.Event()
        self.logger = logger or logging.getLogger(__name__)
        self.get_login_details()

        self.char = '.'
        self.counter = 1

        # create a panel to contain our button
        panel = wx.Panel(self)

        # create a sizer to control the layout of the panel
        sizer = wx.BoxSizer(wx.VERTICAL)

        login_sizer = wx.BoxSizer(wx.HORIZONTAL)


        # create a text field for the first input


        # create a button and add it to the sizer
        self.login_button = wx.Button(panel, label='Log In')
        self.start_bidding_button = wx.Button(panel, label='Start Bidding')
        self.start_bidding_button.Disable()
        self.stop_bidding_button = wx.Button(panel, label='Stop Bidding')
        self.stop_bidding_button.Disable()
        self.save_button = wx.Button(panel, label='Save Log In Details')

        login_sizer.Add(self.login_button, 1, wx.CENTER|wx.ALL, 2)
        login_sizer.Add(self.start_bidding_button, 1, wx.CENTER|wx.ALL, 2)
        login_sizer.Add(self.stop_bidding_button, 1, wx.CENTER|wx.ALL, 2)
        login_sizer.Add(self.save_button, 1, wx.CENTER|wx.ALL, 2)


        self.msgtextarea = wx.TextCtrl(panel, style=wx.TE_MULTILINE)

        sizer.Add(login_sizer, 1, wx.EXPAND, 5)

        sizer.Add(self.msgtextarea, 5, wx.EXPAND, 5)
        # set the panel sizer to our sizer
        panel.SetSizer(sizer)

        # create a main sizer for the frame
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # add the panel to the main sizer
        main_sizer.Add(panel, 1, wx.EXPAND)

        # set the main sizer for the frame
        self.SetSizer(main_sizer)

        self.SetMinSize((400, 300))

        # set the size of the frame based on the size of its content
        self.Fit()


        # bind the button to an event handler
        self.save_button.Bind(wx.EVT_BUTTON, self.save_login_details)
        self.login_button.Bind(wx.EVT_BUTTON, self.login)
        self.start_bidding_button.Bind(wx.EVT_BUTTON, self.begin_bidding)
        self.stop_bidding_button.Bind(wx.EVT_BUTTON, self.stop_bidding)

    def save_login_details(self, event):
        dlg = TwoInputDlg(self, title='Two Input Dialog')
        dlg.ShowModal()

        self.email = dlg.email.GetValue()
        self.password = dlg.password.GetValue()
        # log in to academia research
        # launch bot in child thread
        self.write_login_details()
        dlg.Destroy()

    def login(self, evt):
        launch_thread = threading.Thread(target = self.begin_login)
        launch_thread.start()



    def begin_login(self):
        launch_thread = threading.Thread(target = self.begin_thread_login)
        launch_thread.start()
        launch_thread.join()

        self.login_button.Disable()
        self.start_bidding_button.Enable()
        self.stop_bidding_button.Enable()

    def begin_thread_login(self):
        self.bot = AcademiaBot(self.email, self.password, window = self)


    def start_bot(self):
        self.bot.start_bidding(self.quit_event, window = self)
        self.start_bidding_button.Disable()


    def stop_bidding(self, evt):
        self.log_message_to_txt_field("Stopping bidding bot. Please wait...")
        self.quit_event.set()
        self.stop_bidding_button.Disable()
        self.start_bidding_button.Enable()

    def begin_bidding(self, evt):
        launch_thread = threading.Thread(target = self.start_bot)

        self.logger.info("Launching the launcher thread")
        launch_thread.start()



    def stop_bidding(self):
        self.quit_event.set()

    def log_message_to_txt_field(self, msg):
        self.msgtextarea.AppendText(msg)
        self.msgtextarea.AppendText("\n")

    def show_no_links(self):

        value = self.msgtextarea.GetValue()

        # Split the value into lines
        lines = value.split('\n')

        # Remove the last line
        lines.pop()

        # Print the new value with three dots one after the other
        dots = f"{self.char * self.counter}"
        if self.counter < 6:
            self.counter = self.counter + 1
        else:
            self.counter = 1

        lines.append(f"No new links yet{dots}\n")

        # Join the remaining lines back together
        new_value = '\n'.join(lines)


        self.msgtextarea.SetValue(new_value)


    ###implement on bot close
    def get_login_details(self):
        with open('config.json') as f:
          data = json.load(f)
          self.email = data['email'],
          self.password = data['password']

    def write_login_details(self):
        with open('config.json', 'w') as f:
            data = {'email': self.email, 'password': self.password}
            json.dump(data, f)
        self.log_message_to_txt_field("Login details saved successfully.")




class TwoInputDlg(wx.Dialog):
    def __init__(self, parent, title):
        super(TwoInputDlg, self).__init__(parent, title=title)
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label='Email:')
        self.email = wx.TextCtrl(panel)
        hbox1.Add(label1, wx.ALIGN_CENTER_VERTICAL)
        hbox1.Add(self.email, wx.EXPAND)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        label2 = wx.StaticText(panel, label='Password:')
        self.password = wx.TextCtrl(panel)
        hbox2.Add(label2, wx.ALIGN_CENTER_VERTICAL)
        hbox2.Add(self.password, wx.EXPAND)

        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=10)
        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(panel, label='OK')
        ok_button.Bind(wx.EVT_BUTTON, self.OnOK)
        cancel_button = wx.Button(panel, label='Cancel')
        cancel_button.Bind(wx.EVT_BUTTON, self.OnCancel)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(ok_button, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=2)
        hbox3.Add(cancel_button, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=2)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.ALL, border=10)

        panel.SetSizer(vbox)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # add the panel to the main sizer
        main_sizer.Add(panel, 1, wx.EXPAND)

        # set the main sizer for the frame
        self.SetSizer(main_sizer)

        # set the size of the frame based on the size of its content
        self.Fit()

        self.Center()

    def OnOK(self, event):
        input1_value = self.email.GetValue()
        input2_value = self.password.GetValue()
        # Pass the input values to the parent frame
        if not input1_value or not input2_value:
            wx.MessageBox('Please enter both email and password.', 'Error', wx.OK|wx.ICON_ERROR)
        else:
            # Pass the input values to the parent frame
            self.EndModal(wx.ID_OK)

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)


def get_logger():
    d = datetime.now()

    log_file = d.strftime("%d %a-%m-%Y-%H-%M-%S")
    log_path = os.getcwd() + "\\logs"

    CHECK_FOLDER = os.path.isdir(log_path)
    if not CHECK_FOLDER:
          os.makedirs(log_path)

    print(log_path)


    logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    datefmt="'%m/%d/%Y %I:%M:%S %p",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(log_path, log_file)),
        logging.StreamHandler()
    ],
    level = logging.DEBUG)

    logger = logging.getLogger(__name__)

    # get posta object
    logger.info("...Starting Application...")
    return logger


class AcademiaBotApp(wx.App):

    def OnInit(self, logger = None):
        """
        bmp = wx.Image("gui/posta.png").ConvertToBitmap()
        wx.adv.SplashScreen(bmp, wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
                1000, None, -1)
        wx.Yield()"""


        frame = MyFrame(None, title='Academia Research Bot', logger = get_logger())
        self.locale = wx.GetLocale()
        frame.Show(True)
        self.SetTopWindow(frame)


        return True

    def GetInstallDir(self):
        """
        Return the installation directory for my application.
        """


        return self.installDir

if __name__ == '__main__':
    app =AcademiaBotApp(False)
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()



