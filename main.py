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
import shutil

is64bits = sys.maxsize > 2 ** 32

null = None
true = True
false = False

if "win" in platform().lower() and not "darwin" in platform().lower():
    installDirectoryParent = os.environ["LOCALAPPDATA"]
else:
    installDirectoryParent = os.environ["HOME"]
    if "darwin" in platform().lower():
        installDirectoryParent = os.path.join(installDirectoryParent, "Applications")


class Constants:
    ########### Text
    welcomeLabel_1 = "Welcome to Ct.js!"
    instructionsLabel = "You're almost there! Press this big button to open a door to a wonderful world of game development: "
    installButtonLabel = "Install ct.js"
    bottomRowTextLabel_1 = "Installing at "
    changeAbortLabel_1 = "Change..."

    welcomeLabel_2 = "Working..."
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
    downloadedFilePath = os.path.join(
        tempfile.gettempdir(), "ct.js", downloadedFileName
    )

    ########### Other
    githubUrl = "https://api.github.com/repos/ct-js/ct-js/releases/latest"


print("Default installation directory location: " + Constants.defaultInstallDir)
print(
    "Default installation directory location exists: "
    + os.path.exists(Constants.defaultInstallDir).__str__()
)


githubData = {}


# https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url#14260592
def downloadUrl(
    app: "Installer", url, save_path=Constants.downloadedFilePath, chunk_size=1024
):
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
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=chunk_size):
                dl += len(data)
                f.write(data)
                done = int(progressBarTotal * dl / total_length)
                sys.stdout.write("\r[%s / %s]" % (done, progressBarTotal))
                sys.stdout.flush()
                app.pbar.setValue(done)
                # sys.stdout.write(
                #    "\r[%s%s]" % ("=" * done, " " * (progressBarTotal - done))
                # )
                # sys.stdout.flush()
    print(" ")
    print("Finished downloading " + url + " to " + save_path)


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


def runCommand(command: str):
    print(f"running command: {command}")
    import subprocess

    subprocess.Popen(command, shell=True)


def showShortcutsWarning():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("Creating shortcuts have failed. You may want to re-run the installer.")
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

    def windowsShortcuts(self, app: "Installer"):
        print(" ")
        try:

            def create_shortcuts(tool_name, exe_path, icon_path):
                with open(getAsset("create_shortcuts.bat"), "r") as f:
                    contents = f.read().replace("{installDir}", app.location)

                program = contents
                runCommand(program)

            create_shortcuts(
                "ct.js",
                path.join(app.location, "ct.js", "ctjs.exe"),
                path.join(app.location, "ct.js", "ct_ide.png"),
            )

        except:
            showShortcutsWarning()

    def macShortcuts(self, app: "Installer"):
        program = (
            "chmod +x '"
            + path.abspath(
                path.join(
                    app.location, "ct.js", "ctjs.app", "Contents", "MacOS", "nwjs"
                )
            )
            + "'"
        )
        runCommand(program)

        try:
            import pyshortcuts

            os.symlink(
                path.join(app.location, "ct.js", "ctjs.app"),
                path.join(pyshortcuts.get_desktop(), "ctjs.app"),
            )
        except:
            showShortcutsWarning()

    def linuxShortcuts(self, app: "Installer"):
        exeFiles = ["chromedriver", "ctjs", "nwjc"]
        for i in exeFiles:
            try:
                program = (
                    "chmod +x '"
                    + path.abspath(path.join(app.location, "ct.js", i))
                    + "'"
                )
                runCommand(program)
            except:
                pass

        try:
            desktopFileName = "ct.js.desktop"
            with open(getAsset(desktopFileName), "r") as f:
                contents = f.read().replace("{installDir}", app.location)

            import pyshortcuts
            from pyshortcuts.linux import get_homedir

            home = get_homedir()
            firstLocation = path.join(
                home, ".local", "share", "applications", desktopFileName
            )
            secondLocation = path.join(home, "Desktop", desktopFileName)

            with open(firstLocation, "w") as f:
                f.write(contents)
            program = "chmod +x '" + firstLocation + "'"
            runCommand(program)

            with open(secondLocation, "w") as f:
                f.write(contents)
            program = "chmod +x '" + secondLocation + "'"
            runCommand(program)
        except:
            showShortcutsWarning()


platformStuff = PlatformStuff()


class InstallThread(QThread):
    def __init__(self, location, parent):
        QThread.__init__(self)

        self.location = location
        self.app: Installer = parent

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
        self.app.pbar.show()
        downloadUrl(self.app, url)
        self.changeStep("installInfoImage_3")
        print(" ")

    def changeStep(self, name):
        self.app.currentStep.load(getAsset("check-circle.svg"))
        self.app.currentStep = self.app.__dict__[name]
        self.app.currentStep.load(getAsset("clock.svg"))

    def run(self):
        import zipfile

        self.getRelease(platformStuff.channel)
        print(" ")
        zipFolderName = platformStuff.channel
        print(" ")

        with zipfile.ZipFile(Constants.downloadedFilePath, "r") as zip_ref:
            try:
                zipFolderName = os.path.dirname(zip_ref.namelist()[0])
            except:
                pass
            zip_ref.extractall(self.location)

        import time

        time.sleep(0.5)
        try:
            shutil.rmtree(os.path.join(self.location, "ct.js"))
        except:
            pass

        os.rename(
            os.path.join(self.location, zipFolderName),
            os.path.join(self.location, "ct.js"),
        )
        print(" ")

        from shutil import copyfile

        copyfile(
            getAsset("icon.ico"), path.join(self.app.location, "ct.js", "ctjs.ico")
        )

        self.changeStep("installInfoImage_4")
        print(" ")
        platformStuff.shortcuts(self.app)
        print(" ")

        try:
            os.remove(Constants.downloadedFilePath)
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
                        self.app.location, "ct.js", path.basename(application_path)
                    ),
                )
                print(" ")
            except:
                pass
        else:
            print(
                "You may be running from source, not copying the executable to the install dir."
            )
            print(" ")

        self.app.welcomeLabel.setText(Constants.welcomeLabel_3)
        print(" ")
        self.app.changeAbortLabel.setText(Constants.changeAbortLabel_3)
        print(" ")
        self.app.currentStep.load(getAsset("check-circle.svg"))
        print(" ")
        self.app.currentStep = null
        self.app.doneInstalling = true
        self.app.setWindowTitle("Done installing ct.js!")


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

        self.installing = false
        self.doneInstalling = false

        # Border and bottom row

        # First page

        self.welcomeLabel = QLabel(Constants.welcomeLabel_1, parent=self)
        self.welcomeLabel.move(20, 14)
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
            Constants.bottomRowTextLabel_1 + self.location, parent=self
        )
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

    def updateLocation(self):
        self.bottomRowTextLabel.setText(Constants.bottomRowTextLabel_1 + self.location)

    def install(self):
        self.installing = true
        self.setWindowTitle("Installing ct.js...")

        self.welcomeLabel.setText(Constants.welcomeLabel_2)
        self.changeAbortLabel.setText(Constants.changeAbortLabel_2)
        self.bottomRowTextLabel.setText(Constants.bottomRowTextLabel_2)
        self.instructionsLabel.hide()
        self.installButtonLabel.hide()

        self.pbar = QProgressBar(self)
        self.pbar.move(20, 229)
        self.pbar.resize(177, 22)
        # self.setStyleName("pbar")
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
                os.remove(Constants.downloadedFilePath)
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
        pen.setWidth(1.5)
        qp.setPen(pen)
        qp.setBrush(br)
        qp.drawRect(QtCore.QRect(0, 0, self.width, self.height))

        # Bottom row
        br2 = QtGui.QBrush(QtGui.QColor(255, 255, 255, 100))
        pen2 = QtGui.QPen()
        pen2.setColor(QtGui.QColor(200, 205, 209, 200))
        pen2.setWidth(1.5)
        qp.setPen(pen2)
        qp.setBrush(br2)
        qp.drawRect(QtCore.QRect(0, 264, self.width, self.height))

        try:
            currentFrame = self.gif.currentPixmap()
            frameRect = currentFrame.rect()
            frameRect.moveCenter(self.rect().center())
            if frameRect.intersects(event.rect()):
                painter = QPainter(self)
                painter.drawPixmap(frameRect.left(), frameRect.top(), currentFrame)
        except:
            pass

    def setStyleName(self, name: str):
        return self.__dict__[name].setObjectName(name)


if __name__ == "__main__":
    print("Opening application...")

    # https://stackoverflow.com/a/51914685
    # Tries to solve weird scaling that could occur
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QApplication([])

    app.setStyle("Fusion")
    with open(getAsset("stylesheet.css"), "r") as f:
        app.setStyleSheet(f.read())

    installer = Installer()
    installer.show()

    app.setActiveWindow(installer)

    app.exec_()

    print("Application closed")
    sys.exit()
