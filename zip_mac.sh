# Zips the .app file
cp -v -f -R dist ctjs-installer-mac
mkdir zip
zip ctjs-installer-mac ctjs-installer-mac/*.app/**/* ctjs-installer-mac/*.app/**/**/*
mv ctjs-installer-mac.zip zip
