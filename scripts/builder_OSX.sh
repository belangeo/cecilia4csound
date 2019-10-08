export DMG_DIR="Cecilia4Csound 4.3"
export DMG_NAME="Cecilia4Csound_5.3.dmg"

rm -rf build dist
python setup.py py2app --plist=scripts/info.plist
rm -rf build
mv dist Cecilia4Csound_OSX

if cd Cecilia4Csound_OSX;
then
    find . -name .svn -depth -exec rm -rf {} \
    find . -name *.pyc -depth -exec rm -f {} \
    find . -name .* -depth -exec rm -f {} \;
else
    echo "Something wrong. Cecilia4Csound_OSX not created"
    exit;
fi

rm Cecilia4Csound.app/Contents/Resources/Cecilia.ico
rm Cecilia4Csound.app/Contents/Resources/CeciliaFileIcon.ico

# keep only 64-bit arch
ditto --rsrc --arch x86_64 Cecilia4Csound.app Cecilia4Csound-x86_64.app
rm -rf Cecilia4Csound.app
mv Cecilia4Csound-x86_64.app Cecilia4Csound.app

cd ..

cp -R Cecilia4Csound_OSX/Cecilia4Csound.app .

echo "assembling DMG..."
mkdir "$DMG_DIR"
cd "$DMG_DIR"
cp -R ../Cecilia4Csound.app .
ln -s /Applications .
cd ..

hdiutil create "$DMG_NAME" -srcfolder "$DMG_DIR"

rm -rf "$DMG_DIR"
rm -rf Cecilia4Csound_OSX
rm -rf Cecilia4Csound.app
