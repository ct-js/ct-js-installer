# Zips the .app file
cp -v -f -R dist ctjs-installer-mac
zip ctjs-installer-mac ctjs-installer-mac/*.app/**/* ctjs-installer-mac/*.app/**/**/*
mkdir zip
mv ctjs-installer-mac.zip zip
