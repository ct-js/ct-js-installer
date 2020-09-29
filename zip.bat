:: Zips the .exe file
cmd /C "timeout 5 /nobreak"
robocopy ./dist /S /V /MIR ./ctjs-installer-windows
mkdir zip
:: powershell "Compress-Archive ctjs-installer-windows/*.exe ctjs-installer-windows.zip"
:: move ctjs-installer-windows.zip zip
move ctjs-installer-windows/*.exe zip
