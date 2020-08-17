# Installer

A python installer for ct.js.

See https://github.com/ct-js/ct-js/issues/200.

## Developing

Run `./install-requirements.sh` to install the python dependencies.

Run `./run.sh` to run the installer.

Run `./format.sh` to format the python file.

Run `./build.sh` to build the installer.

## Todo

-   [x] new gui
    -   [x] style
        -   [x] button hover style may need to be changed
    -   [x] first page
        -   [x] gui
        -   [x] change button
        -   [x] install button
    -   [x] second page
        -   [x] gui
        -   [x] installation status
        -   [x] abort button
        -   [x] rotating in-progress icon
        -   [x] open ct.js button
            -   hopefully works
        -   [x] run bat/sh files that create shortcuts/file rules
        -   [x] eta
            -   was replaced by the progress bar
-   [x] figure out pyinstaller/py2app/py2exe
    -   [x] windows
    -   [x] mac
        -   getting a error when running about not being able to find the python image :/
    -   [x] linux
-   [x] integrate everything into travis
-   [x] copy the installer to the ct.js directory so it can be run from within ct.js to check for updates
-   [ ] improve the progress bar css
-   [ ] transfer repo and setup travis
