:: Zips the .exe file
robocopy ./dist /S /V /MIR ./ctjs-installer-windows
mkdir zip
powershell "Compress-Archive ctjs-installer-windows/*.exe ctjs-installer-windows.zip"
move ctjs-installer-windows.zip zip
move ctjs-installer-windows/ctjs-installer-windows.exe zip
