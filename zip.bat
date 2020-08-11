:: Zips the .exe file
powershell "Compress-Archive dist/*.exe ctjs-installer-windows.zip"
mkdir zip
move ctjs-installer-windows.zip zip
