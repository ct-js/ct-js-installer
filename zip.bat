:: Zips the .exe file
copy dist /Y ctjs-installer-windows
powershell "Compress-Archive ctjs-installer-windows/*.exe ctjs-installer-windows.zip"
mkdir zip
move ctjs-installer-windows.zip zip
