:: Zips the .exe file
timeout 5
robocopy ./dist /S /V /MIR ./ctjs-installer-windows
mkdir zip
:: powershell "Compress-Archive ctjs-installer-windows/*.exe ctjs-installer-windows.zip"
:: move ctjs-installer-windows.zip zip
move ctjs-installer-windows/*.exe zip
