:: Zips the .exe file
robocopy ./dist /S /V /MIR ./ctjs-installer-windows
powershell "Compress-Archive ctjs-installer-windows/*.exe ctjs-installer-windows.zip"
mkdir zip
move ctjs-installer-windows.zip zip
