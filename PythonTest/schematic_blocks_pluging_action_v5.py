import wx
import os
import subprocess
import platform
import shutil
import configparser


class ClipboardSaverApp(wx.App):
    def OnInit(self):
        self.frame = ClipboardSaverFrame(None, title="Clipboard Saver",size=(400, 600))
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

class ClipboardSaverFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ClipboardSaverFrame, self).__init__(*args, **kwargs)

        self.InitUI()

    def InitUI(self):

        self.Bind(wx.EVT_CLOSE, self.OnExit)
        load_config()

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        label1 = wx.StaticText(panel, label="Enter file name:")
        vbox.Add(label1, flag=wx.TOP | wx.LEFT | wx.RIGHT, border=10)

        self.filename_input = wx.TextCtrl(panel)
        vbox.Add(self.filename_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        save_button = wx.Button(panel, label="Save Clipboard to .kicad_pack")
        vbox.Add(save_button, flag=wx.EXPAND | wx.ALL, border=10)

        label2 = wx.StaticText(panel, label="Select a .kicad_pack file to import:")
        vbox.Add(label2, flag=wx.TOP | wx.LEFT | wx.RIGHT, border=10)

        self.search_bar = wx.SearchCtrl(panel, style=wx.TE_PROCESS_ENTER)
        vbox.Add(self.search_bar, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        self.file_list = wx.ListBox(panel)
        vbox.Add(self.file_list, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        import_button = wx.Button(panel, label="Import Selected File to Clipboard")
        vbox.Add(import_button, flag=wx.EXPAND | wx.ALL, border=10)

        import_to_dir_button = wx.Button(panel, label="Import to Current Directory")
        vbox.Add(import_to_dir_button, flag=wx.EXPAND | wx.ALL, border=10)

        dir_button = wx.Button(panel, label="Change Working Directory")
        vbox.Add(dir_button, flag=wx.EXPAND | wx.ALL, border=10)

        open_dir_button = wx.Button(panel, label="Open Working Directory")
        vbox.Add(open_dir_button, flag=wx.EXPAND | wx.ALL, border=10)

        delete_button = wx.Button(panel, label="Delete Selected File")
        delete_button.SetForegroundColour(wx.Colour(255, 0, 0))  # Set text color to red
        vbox.Add(delete_button, flag=wx.EXPAND | wx.ALL, border=10)



        panel.SetSizer(vbox)

        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        import_button.Bind(wx.EVT_BUTTON, self.OnImport)
        import_to_dir_button.Bind(wx.EVT_BUTTON, self.OnImportToDirectory)
        dir_button.Bind(wx.EVT_BUTTON, self.OnChangeDirectory)
        open_dir_button.Bind(wx.EVT_BUTTON, self.OnOpenDirectory)
        delete_button.Bind(wx.EVT_BUTTON, self.OnDeleteFile)
        self.search_bar.Bind(wx.EVT_TEXT, self.OnSearch)
        self.search_bar.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelSearch)

        self.UpdateFileList()

    def OnExit(self, event):
        save_config()
        self.Destroy()


    def UpdateFileList(self, search_text=""):
        kicad_pack_files = [filename for filename in os.listdir() if filename.endswith(".kicad_pack")]
        if search_text:
            kicad_pack_files = [filename for filename in kicad_pack_files if search_text.lower() in filename.lower()]
        display_files = [f"📦 {filename}" for filename in kicad_pack_files]
        
        self.file_list.Set(display_files)
        self.file_list.Set(display_files)
       # print(display_files)
        # print(self.file_list.GetStrings())

    def OnSearch(self, event):
        search_text = self.search_bar.GetValue()
        self.UpdateFileList(search_text)

    def OnCancelSearch(self, event):
        self.search_bar.SetValue("")
        self.UpdateFileList()

    def OnSave(self, event):
        filename = self.filename_input.GetValue()
        if filename:
            clipboard = wx.Clipboard.Get()
            clipboard.Open()
            data = wx.TextDataObject()
            clipboard.GetData(data)
            clipboard.Close()

            clipboard_text = data.GetText()
            
            if clipboard_text:
                if not filename.endswith(".kicad_pack"):
                    filename += ".kicad_pack"
                packed_data = f"packSch:[{clipboard_text}]"
                with open(filename, "w") as file:
                    file.write(packed_data)
                wx.MessageBox("Clipboard content saved successfully!", "Success")
                self.UpdateFileList()
            else:
                wx.MessageBox("Clipboard is empty!", "Error")
        else:
            wx.MessageBox("Please enter a valid file name.", "Error")

    def OnImport(self, event):
        selected_file = self.file_list.GetStringSelection()[2:] 
        if selected_file[-1] != 'k':
            selected_file = selected_file + 'k'
        if selected_file:
            with open(selected_file, "r") as file:
                file_content = file.read()
                start = file_content.find("[") + 1
                end = file_content.rfind("]")
                if start != -1 and end != -1:
                    clipboard_text = file_content[start:end]
                    clipboard = wx.Clipboard.Get()
                    clipboard.Open()
                    data = wx.TextDataObject(clipboard_text)
                    clipboard.SetData(data)
                    clipboard.Close()
                    #wx.MessageBox("File content imported to clipboard!", "Success")
                else:
                    wx.MessageBox("Invalid file format.", "Error")
        else:
            wx.MessageBox("Please select a file to import.", "Error")

    def OnChangeDirectory(self, event):
        dialog = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            new_directory = dialog.GetPath()
            os.chdir(new_directory)
            self.UpdateFileList()
            save_config()
        dialog.Destroy()

    def OnOpenDirectory(self, event):
        # current_directory = os.getcwd()+'/'
        # #print("+++++++++" + current_directory)
        # subprocess.Popen(["xdg-open", current_directory])  # Open directory in file explorer
        current_directory = os.getcwd()
        if platform.system() == "Windows":
            subprocess.Popen(["explorer", current_directory])  # Open directory in file explorer (Windows)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", current_directory])  # Open directory in Finder (macOS)
        else:  # Assuming it's Linux or other Unix-like OS
            subprocess.Popen(["xdg-open", current_directory])  # Open directory in default file manager (Linux)


    def OnDeleteFile(self, event):
            selected_file = self.file_list.GetStringSelection()
            if selected_file[-1] != 'k':
                selected_file = selected_file + 'k'
            if selected_file:
                selected_file = selected_file.replace("📦 ", "")  # Remove the 📦 character
                try:
                    os.remove(selected_file)
                    wx.MessageBox("File deleted successfully!", "Success")
                    self.UpdateFileList()
                except Exception as e:
                    wx.MessageBox(f"Error deleting file: {str(e)}", "Error")
            else:
                wx.MessageBox("Please select a file to delete.", "Error")

    def OnImportToDirectory(self, event):
        dialog = wx.FileDialog(self, "Select a .kicad_pack file to import:", style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            source_file = dialog.GetPath()
            filename = os.path.basename(source_file)
            new_file_path = os.path.join(os.getcwd(), filename)
            try:
                shutil.copy(source_file, new_file_path)
                wx.MessageBox("File imported to current directory successfully!", "Success")
                self.UpdateFileList()
            except Exception as e:
                wx.MessageBox(f"Error importing file: {str(e)}", "Error")
        dialog.Destroy()

def load_config():
    config = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")  # Use absolute path
    config.read(config_file_path)
    if "General" in config:
        os.chdir(config["General"]["WorkingDirectory"])

def save_config():
    config = configparser.ConfigParser()
    config["General"] = {"WorkingDirectory": os.getcwd()}
    config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")  # Use absolute path
    with open(config_file_path, "w") as configfile:
        config.write(configfile)

if __name__ == "__main__":
    app = ClipboardSaverApp(False)
    app.MainLoop()
