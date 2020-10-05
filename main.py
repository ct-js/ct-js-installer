from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QGridLayout,
    QApplication,
    QInputDialog,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QProgressBar,
)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QMovie, QPainter, QPixmap, QImage
from PyQt5 import QtGui, QtCore, QtWidgets, QtSvg

from platform import platform
import sys
import os
from os import path
import tempfile
from zipfile import ZipFile as ZipFile_
from zipfile import ZipInfo
import random
import json

print(" ")

null = None
true = True
false = False

is64bits = sys.maxsize > 2 ** 32
gui = false
installFolderName = "ct.js"

if "win" in platform().lower() and not "darwin" in platform().lower():
    installDirectoryParent = os.environ["LOCALAPPDATA"]
else:
    installDirectoryParent = os.environ["HOME"]
    if "darwin" in platform().lower():
        installDirectoryParent = os.path.join(installDirectoryParent, "Applications")

# https://stackoverflow.com/a/13790741
def basePath():
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except:
        basePath = os.path.abspath(".")

    return basePath


def getAsset(name):
    return os.path.join(basePath(), "assets", name)


# https://stackoverflow.com/a/39296577
class ZipFile(ZipFile_):
    def extractall(self, path=None, members=None, pwd=None):
        if members is None:
            members = self.namelist()

        if path is None:
            path = os.getcwd()
        else:
            path = os.fspath(path)

        for zipinfo in members:
            self.extract(zipinfo, path, pwd)

    def extract(self, member, path=None, pwd=None):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        ret_val = self._extract_member(member, path, pwd)
        attr = member.external_attr >> 16
        os.chmod(ret_val, attr)
        return ret_val


class Constants:
    ########### Text
    welcomeLabel_1 = "Welcome to Ct.js!"
    instructionsLabel = "You're almost there! Press this big button to open a door to a wonderful world of game development: "
    installButtonLabel = "Install ct.js"
    bottomRowTextLabel_1 = "Installing at "
    changeAbortLabel_1 = "Change..."

    welcomeLabel_2 = lambda: random.choice(json.load(open(getAsset("messages.json"))))
    installInfoLabel_1 = "Get release info"
    installInfoLabel_2 = "Download the app"
    installInfoLabel_3 = "Unpack and install ct.js"
    installInfoLabel_4 = "Create shortcuts and file rules"
    etaLabel_1 = "This will take about "
    etaLabel_2 = " seconds."
    bottomRowTextLabel_2 = "Pro tip: use the same installer to update ct.js!"
    changeAbortLabel_2 = "Abort"
    welcomeLabel_3 = "Done!"
    changeAbortLabel_3 = "Open ct.js"

    ########### Path
    defaultInstallDir = os.path.join(installDirectoryParent)
    downloadedFileName = "ctjs-installer-download.zip"
    downloadedFilePath = lambda: os.path.join(
        tempfile.gettempdir(), installFolderName, Constants.downloadedFileName
    )
    locationFileName = "ctjs-installer-location.txt"
    locationFilePath = lambda: os.path.join(
        tempfile.gettempdir(), Constants.locationFileName
    )
    nodeModulesPath = ["./node_modules", "./data/node_requires"]
    macRoot = "./ctjs.app/Contents/Resources/app.nw"

    ########### Other
    githubUrl = "https://api.github.com/repos/ct-js/ct-js/releases/latest"


print("Default installation directory location: " + Constants.defaultInstallDir)
print(
    "Default installation directory location exists: "
    + os.path.exists(Constants.defaultInstallDir).__str__()
)


githubData = {}


# https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url#14260592
def downloadUrl(app: "Installer", url, save_path="", chunk_size=1024):
    if save_path == "":
        save_path = Constants.downloadedFilePath()

    prevMessageChange = 0

    print("Downloading " + url + " to " + save_path)
    try:
        os.mkdir(os.path.dirname(save_path))
    except:
        pass
    # https://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads#15645088
    with open(save_path, "wb") as f:
        import requests

        response = requests.get(url, stream=True)
        total_length = response.headers.get("content-length")

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            progressBarTotal = 100
            dl = 0
            prevDone = 0;
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=chunk_size):
                dl += len(data)
                f.write(data)
                done = int(progressBarTotal * dl / total_length)
                if done % 10 == 0 and prevMessageChange != done:
                    prevMessageChange = done
                    app.welcomeLabel.setText(Constants.welcomeLabel_2())
                if (prevDone != done):
                    downloadLabel = Constants.installInfoLabel_2 + ' (' + str(done) + '%)';
                    prevDone = done;
                    print(done);
                    app.installInfoLabel_2.setText(downloadLabel);
                sys.stdout.write("\r[%s / %s]" % (done, progressBarTotal))
                sys.stdout.flush()
                try:
                    app.pbar.setValue(done)
                except:
                    pass

    print(" ")
    print("Finished downloading " + url + " to " + save_path)


def runCommand(command: str):
    print(f"Running command: {command}")
    import subprocess

    subprocess.Popen(command, shell=True)


def chmod(path_):
    program = "chmod +x '" + path_ + "'"
    runCommand(program)


def showShortcutsWarning():
    if gui == true:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(
            "Creating shortcuts have failed. You may want to re-run the installer."
        )
        msg.setWindowTitle("Warning")
        msg.show()


class PlatformStuff:
    def __init__(self):
        print("Platform: " + platform())
        if "darwin" in platform().lower():
            # Mac
            self.shortcuts = self.macShortcuts
            self.channel = "osx64"
        elif "win" in platform().lower():
            # Windows
            self.shortcuts = self.windowsShortcuts
            self.channel = "win32"
            if is64bits:
                self.channel = "win64"
        else:
            # Assume linux
            self.shortcuts = self.linuxShortcuts
            self.channel = "linux32"
            if is64bits:
                self.channel = "linux64"
        print(f"Channel: {self.channel}")

    def windowsShortcuts(self, app: "Installer", location):
        print(" ")

        try:

            def create_shortcuts(tool_name, exe_path, icon_path):
                with open(getAsset("create_shortcuts.bat"), "r") as f:
                    contents = f.read().replace("{installDir}", location)

                runCommand(contents)

            create_shortcuts(
                "ct.js",
                path.join(location, installFolderName, "ctjs.exe"),
                path.join(location, installFolderName, "ct_ide.png"),
            )

        except:
            showShortcutsWarning()

    def macShortcuts(self, app: "Installer", location):
        try:
            import pyshortcuts

            os.symlink(
                path.join(location, installFolderName, "ctjs.app"),
                path.join(pyshortcuts.get_desktop(), "ctjs.app"),
            )

        except:
            showShortcutsWarning()

    def linuxShortcuts(self, app: "Installer", location):
        try:
            desktopFileName = "ct.js.desktop"
            with open(getAsset(desktopFileName), "r") as f:
                contents = f.read().replace("{installDir}", location)

            import pyshortcuts
            from pyshortcuts.linux import get_homedir

            home = get_homedir()
            firstLocation = path.join(
                home, ".local", "share", "applications", desktopFileName
            )
            secondLocation = path.join(home, "Desktop", desktopFileName)

            with open(firstLocation, "w") as f:
                f.write(contents)
            chmod(firstLocation)

            with open(secondLocation, "w") as f:
                f.write(contents)
            chmod(secondLocation)

        except:
            showShortcutsWarning()


platformStuff = PlatformStuff()


class InstallThread(QThread):
    def __init__(self, location, parent=null):
        QThread.__init__(self)

        self.location = location
        self.app: Installer = parent

        print(" ")
        print("InstallThread installation location:", self.location)
        print(
            "InstallThread actual location:      ",
            path.join(self.location, installFolderName),
        )
        print("Install folder name:", installFolderName)

    def __del__(self):
        self.wait()

    def getGitHubData(self):
        import requests

        githubData = requests.get(Constants.githubUrl).json()
        self.changeStep("installInfoImage_2")

        print(" ")
        return githubData

    def getRelease(self, channel):
        # https://stackoverflow.com/questions/9542738/python-find-in-list#9542768
        release = [x for x in self.getGitHubData()["assets"] if channel in x["name"]][0]

        print(" ")

        url = release["browser_download_url"]

        print(" ")

        try:
            pass
            # self.app.pbar.show()
        except:
            pass

        downloadUrl(self.app, url)
        self.changeStep("installInfoImage_3")

        print(" ")

    def changeStep(self, name):
        try:
            self.app.currentStep.load(getAsset("check-circle.svg"))
            self.app.currentStep = self.app.__dict__[name]
            self.app.currentStep.load(getAsset("clock.svg"))
            self.app.welcomeLabel.setText(Constants.welcomeLabel_2())

        except:
            pass

    def run(self):
        self.getRelease(platformStuff.channel)

        from shutil import copyfile, copy2, rmtree
        from shutil import copytree as copytree_

        root = path.join(self.location, installFolderName)
        if "osx" in platformStuff.channel:
            root = path.join(root, Constants.macRoot)
        for path_ in Constants.nodeModulesPath:
            try:
                node_module = path.join(root, path_)
                print(f"Removing {path.basename(node_module)} (path: {node_module})")
                rmtree(node_module)

            except:
                pass

        print(" ")

        zipFolderName = platformStuff.channel

        print(" ")

        print("Unpacking the zip")
        with ZipFile(Constants.downloadedFilePath(), "r") as zip_ref:
            try:
                zipFolderName = os.path.dirname(zip_ref.namelist()[0])

            except:
                pass

            zip_ref.extractall(self.location)
        print("Done unpacking the zip")

        import time

        time.sleep(0.5)

        # https://lukelogbook.tech/2018/01/25/merging-two-folders-in-python/
        def copytree(src, dst):
            for src_dir, dirs, files in os.walk(src):
                dst_dir = src_dir.replace(src, dst, 1)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                for file_ in files:
                    src_file = os.path.join(src_dir, file_)
                    dst_file = os.path.join(dst_dir, file_)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    copy2(src_file, dst_dir)

        try:
            print("Making install folder directory")
            os.mkdir(os.path.join(self.location, installFolderName))

        except:
            pass

        print("Copying files")
        copytree(
            os.path.join(self.location, zipFolderName),
            os.path.join(self.location, installFolderName),
        )
        print(" ")

        print("Copying icon files (if they dont exist)")
        if not path.exists(path.join(self.location, installFolderName, "ctjs.ico")):
            print("Copying ctjs.ico")
            copyfile(
                getAsset("icon.ico"),
                path.join(self.location, installFolderName, "ctjs.ico"),
            )

        if not path.exists(path.join(self.location, installFolderName, "ctjs.icns")):
            print("Copying ctjs.icns")
            copyfile(
                getAsset("icon.icns"),
                path.join(self.location, installFolderName, "ctjs.icns"),
            )

        if not path.exists(path.join(self.location, installFolderName, "ctjs.png")):
            print("Copying ct_ide.png")
            copyfile(
                getAsset("icon.png"),
                path.join(self.location, installFolderName, "ct_ide.png"),
            )

        try:
            print("Deleting unzipped folder")
            rmtree(os.path.join(self.location, zipFolderName))

        except:
            pass

        self.changeStep("installInfoImage_4")

        print(" ")

        platformStuff.shortcuts(self.app, self.location)

        print(" ")

        try:
            # TODO: fix this to not freeze the installer

            # print("Deleting temporary zip")
            # os.remove(Constants.downloadedFilePath())
            print(" ")
        except:
            pass

        # https://stackoverflow.com/a/404750
        if getattr(sys, "frozen", False):
            application_path = os.path.abspath(sys.executable)
            print(" ")
            try:
                copyfile(
                    application_path,
                    path.join(
                        self.location,
                        installFolderName,
                        path.basename(application_path),
                    ),
                )
                chmod(
                    path.join(
                        self.location,
                        installFolderName,
                        path.basename(application_path),
                    )
                )
                print(" ")

            except:
                pass

        else:
            print(
                "You may be running from source, not copying the executable to the install dir."
            )
            print(" ")

        try:
            self.app.welcomeLabel.setText(Constants.welcomeLabel_3)
            print(" ")
            self.app.changeAbortLabel.setText(Constants.changeAbortLabel_3)
            print(" ")
            self.app.currentStep.load(getAsset("check-circle.svg"))
            print(" ")
            self.app.currentStep = null
            self.app.doneInstalling = true
            self.app.setWindowTitle("Done installing ct.js!")

        except:
            pass

        print("Done installing!")


class Installer(QDialog):
    def __init__(self, parent=null):
        super(Installer, self).__init__(parent)

        try:
            self.setWindowIcon(QtGui.QIcon(getAsset("icon.ico")))

        except:
            pass

        self.setWindowIconText("ct.js Installer")
        self.setWindowTitle("ct.js Installer")
        self.left = 30
        self.top = 30
        self.width = 506
        self.height = 318
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        self.location = Constants.defaultInstallDir

        try:
            with open(Constants.locationFilePath(), "r") as f:
                self.location = f.read()
                print("Read the location from " + Constants.locationFilePath())

        except:
            print(
                "Reading the location file failed; attempted location: "
                + Constants.locationFilePath()
            )

        self.installing = false
        self.doneInstalling = false

        # First page

        self.welcomeLabel = QLabel(Constants.welcomeLabel_1, parent=self)
        self.welcomeLabel.move(20, 14)
        self.welcomeLabel.resize(350, 44)
        self.setStyleName("welcomeLabel")

        self.instructionsLabel = QLabel(Constants.instructionsLabel, parent=self)
        self.instructionsLabel.move(23, 69)
        self.instructionsLabel.resize(245, 57)
        self.instructionsLabel.setWordWrap(true)
        self.setStyleName("instructionsLabel")

        self.installButtonLabel = QPushButton(Constants.installButtonLabel, self)
        self.installButtonLabel.move(23, 148)
        self.installButtonLabel.resize(185, 60)
        self.installButtonLabel.clicked.connect(self.install)
        self.setStyleName("installButtonLabel")

        self.bottomRowTextLabel = QLabel(
            Constants.bottomRowTextLabel_1
            + self.location
            + path.sep
            + installFolderName,
            parent=self,
        )
        self.updateLocation()
        self.bottomRowTextLabel.move(21, 281)
        self.bottomRowTextLabel.resize(340, 19)
        self.bottomRowTextLabel.setWordWrap(false)
        self.setStyleName("bottomRowTextLabel")

        self.changeAbortLabel = QPushButton(Constants.changeAbortLabel_1, self)
        self.changeAbortLabel.move(369, 275)
        self.changeAbortLabel.resize(113, 32)
        self.changeAbortLabel.clicked.connect(self.changeLocation)
        self.setStyleName("changeAbortLabel")

        self.hammerCatImage = QtSvg.QSvgWidget(getAsset("HammerCat.svg"), self)
        self.hammerCatImage.resize(171, 207)
        self.hammerCatImage.move(481 - 171, 34)

    def install(self):
        self.installing = true
        self.setWindowTitle("Installing ct.js...")

        try:
            with open(Constants.locationFilePath(), "w") as f:
                f.write(self.location)
                print("Wrote the location to " + Constants.locationFilePath())

        except:
            print(
                "Writing the location file failed; attempted location: "
                + Constants.locationFilePath()
            )

        self.welcomeLabel.setText(Constants.welcomeLabel_2())
        self.changeAbortLabel.setText(Constants.changeAbortLabel_2)
        self.bottomRowTextLabel.setText(Constants.bottomRowTextLabel_2)
        self.instructionsLabel.hide()
        self.installButtonLabel.hide()

        self.pbar = QProgressBar(self)
        self.pbar.move(20, 229)
        self.pbar.resize(177, 22)
        self.setStyleName("pbar")
        self.pbar.hide()

        self.installInfoLabel_1 = QLabel(Constants.installInfoLabel_1, parent=self)
        self.installInfoLabel_1.move(46, 71)
        self.setStyleName("installInfoLabel_1")
        self.installInfoLabel_1.show()

        self.installInfoLabel_2 = QLabel(Constants.installInfoLabel_2, parent=self)
        self.installInfoLabel_2.move(46, 99)
        self.setStyleName("installInfoLabel_2")
        self.installInfoLabel_2.show()

        self.installInfoLabel_3 = QLabel(Constants.installInfoLabel_3, parent=self)
        self.installInfoLabel_3.move(46, 127)
        self.setStyleName("installInfoLabel_3")
        self.installInfoLabel_3.show()

        self.installInfoLabel_4 = QLabel(Constants.installInfoLabel_4, parent=self)
        self.installInfoLabel_4.move(46, 155)
        self.setStyleName("installInfoLabel_4")
        self.installInfoLabel_4.show()

        # Images

        self.installInfoImage_1 = QtSvg.QSvgWidget(getAsset("clock.svg"), self)
        self.installInfoImage_1.resize(16, 16)
        self.installInfoImage_1.move(20, 72)
        self.installInfoImage_1.show()

        self.installInfoImage_2 = QtSvg.QSvgWidget(getAsset("circle.svg"), self)
        self.installInfoImage_2.resize(16, 16)
        self.installInfoImage_2.move(20, 100)
        self.installInfoImage_2.show()

        self.installInfoImage_3 = QtSvg.QSvgWidget(getAsset("circle.svg"), self)
        self.installInfoImage_3.resize(16, 16)
        self.installInfoImage_3.move(20, 128)
        self.installInfoImage_3.show()

        self.installInfoImage_4 = QtSvg.QSvgWidget(getAsset("circle.svg"), self)
        self.installInfoImage_4.resize(16, 16)
        self.installInfoImage_4.move(20, 155)
        self.installInfoImage_4.show()

        self.currentStep = self.installInfoImage_1

        self.installThread = InstallThread(self.location, self)
        self.installThread.start()

    def updateLocation(self):
        self.bottomRowTextLabel.setText(
            Constants.bottomRowTextLabel_1
            + self.location
            + path.sep
            + installFolderName
        )

    def changeLocation(self):
        if self.doneInstalling:
            # Open ct.js
            program = []

            if "osx" in platformStuff.channel:
                # Mac
                program = "open -n -a '" + self.location + "/ct.js/ctjs.app'"

            elif "win" in platformStuff.channel:
                # Windows
                program = (
                    'cmd /C start "ct.js" "' + self.location + '\\ct.js\\ctjs.exe"'
                )

            else:
                # Linux hopefully
                program = "'" + self.location + "/ct.js/ctjs' &"

            runCommand(program)
            sys.exit()
            return

        if self.installing:
            # Abort button
            try:
                print(" ")
                print("Deleting temporary zip since the user aborted")
                os.remove(Constants.downloadedFilePath())
            except:
                pass
            try:
                self.installThread.exit(0)
            except:
                pass
            sys.exit()
            return

        # Change button
        dialog = QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dialog.exec_()
        self.location = dialog.selectedFiles()[0]
        self.updateLocation()
        return

    def paintEvent(self, event):
        # Border
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(200, 205, 209, 200))
        pen.setWidth(1)
        qp.setPen(pen)
        qp.setBrush(br)
        qp.drawRect(QtCore.QRect(0, 0, self.width, self.height))
        qp.end()

        # Bottom row
        qp2 = QtGui.QPainter(self)
        br2 = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        pen2 = QtGui.QPen()
        pen2.setColor(QtGui.QColor(200, 205, 209, 200))
        pen2.setWidth(1)
        qp2.setPen(pen2)
        qp2.setBrush(br2)
        qp2.drawRect(QtCore.QRect(0, 264, self.width, self.height))
        qp2.end()

    def setStyleName(self, name: str):
        return self.__dict__[name].setObjectName(name)


print(" ")

if __name__ == "__main__":
    del sys.argv[0]
    print("Arguments:", sys.argv)
    print("Current working directory:", os.getcwd())
    print("sys.executable:", sys.executable)
    print(" ")

    print("Running gui")
    # https://stackoverflow.com/a/51914685
    # Tries to solve weird scaling that could occur
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QApplication([])
    gui = true

    app.setStyle("Fusion")
    with open(getAsset("stylesheet.css"), "r") as f:
        app.setStyleSheet(f.read())

    installer = Installer()
    installer.show()

    # Try to get location from arguments
    try:
        installer.location = path.dirname(sys.argv[0])
        installer.updateLocation()
        installFolderName = path.basename(sys.argv[0])
        print(
            "Location from arguments:",
            installer.location,
            "\nFolder name from arguments:",
            installFolderName,
        )

    except:
        pass

    app.setActiveWindow(installer)

    app.exec_()

    print(" ")
    print("Application closed")
    sys.exit()
