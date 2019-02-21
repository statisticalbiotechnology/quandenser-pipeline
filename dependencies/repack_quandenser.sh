mkdir -p oldpack/DEBIAN
dpkg-deb -x *.deb oldpack/
dpkg-deb -e *.deb oldpack/DEBIAN
rm -r oldpack/usr/share  # Remove dinosaur, installed by regular quandenser
sed -i 's/quandenser/quandenser-modified/g' oldpack/DEBIAN/control
mv oldpack/usr/bin/quandenser oldpack/usr/bin/quandenser-modified
dpkg-deb -Z gzip -b oldpack/ quandenser-v0-01-linux-amd64_MODIFIED_repack.deb
