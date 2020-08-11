# Zips the executable
cp -v -f -R dist ctjs-installer-linux
zip ctjs-installer-linux ctjs-installer-linux/*.app/**/* ctjs-installer-linux/*.app/**/**/*
mkdir zip
mv ctjs-installer-linux.zip zip
