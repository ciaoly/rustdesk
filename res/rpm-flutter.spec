Name:       rustdesk
Version:    1.4.6
Release:    0
Summary:    RPM package
License:    GPL-3.0
URL:        https://rustdesk.com
Vendor:     rustdesk <info@rustdesk.com>
Requires:   gtk3 libxcb libXfixes alsa-lib libva pam gstreamer1-plugins-base
Recommends: libayatana-appindicator-gtk3 libxdo
Provides:   libdesktop_drop_plugin.so()(64bit), libdesktop_multi_window_plugin.so()(64bit), libfile_selector_linux_plugin.so()(64bit), libflutter_custom_cursor_plugin.so()(64bit), libflutter_linux_gtk.so()(64bit), libscreen_retriever_plugin.so()(64bit), libtray_manager_plugin.so()(64bit), liburl_launcher_linux_plugin.so()(64bit), libwindow_manager_plugin.so()(64bit), libwindow_size_plugin.so()(64bit), libtexture_rgba_renderer_plugin.so()(64bit)

# https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/

%description
The best open-source remote desktop client software, written in Rust.

%prep
# we have no source, so nothing here

%build
# we have no source, so nothing here

# %global __python %{__python3}

%install

mkdir -p "%{buildroot}/usr/share/rustdesk" && cp -r ${HBB}/flutter/build/linux/x64/release/bundle/* -t "%{buildroot}/usr/share/rustdesk"
mkdir -p "%{buildroot}/usr/bin"
install -Dm 644 $HBB/res/rustwallpaper.service -t "%{buildroot}/usr/share/rustdesk/files"
install -Dm 644 $HBB/res/rustdesk.desktop -t "%{buildroot}/usr/share/rustdesk/files"
install -Dm 644 $HBB/res/rustdesk-link.desktop -t "%{buildroot}/usr/share/rustdesk/files"
install -Dm 644 $HBB/res/128x128@2x.png "%{buildroot}/usr/share/icons/hicolor/256x256/apps/rustdesk.png"
install -Dm 644 $HBB/res/scalable.svg "%{buildroot}/usr/share/icons/hicolor/scalable/apps/rustdesk.svg"

%files
/usr/share/rustdesk/*
/usr/share/rustdesk/files/rustwallpaper.service
/usr/share/icons/hicolor/256x256/apps/rustdesk.png
/usr/share/icons/hicolor/scalable/apps/rustdesk.svg
/usr/share/rustdesk/files/rustdesk.desktop
/usr/share/rustdesk/files/rustdesk-link.desktop

%changelog
# let's skip this for now

%pre
# can do something for centos7
case "$1" in
  1)
    # for install
  ;;
  2)
    # for upgrade
    systemctl stop rustwallpaper || true
    systemctl stop rustdesk || true
  ;;
esac

%post
# clean up the legacy `rustdesk`/`RustWallpaper` names from previous builds
systemctl disable rustdesk >/dev/null 2>&1 || true
rm -f /etc/systemd/system/rustdesk.service /usr/lib/systemd/system/rustdesk.service /usr/bin/rustdesk /usr/bin/RustWallpaper
cp /usr/share/rustdesk/files/rustwallpaper.service /etc/systemd/system/rustwallpaper.service
cp /usr/share/rustdesk/files/rustdesk.desktop /usr/share/applications/
cp /usr/share/rustdesk/files/rustdesk-link.desktop /usr/share/applications/
ln -sf /usr/share/rustdesk/rustwallpaper /usr/bin/rustwallpaper
systemctl daemon-reload
systemctl enable rustwallpaper
systemctl start rustwallpaper
update-desktop-database

%preun
case "$1" in
  0)
    # for uninstall
    systemctl stop rustwallpaper || true
    systemctl disable rustwallpaper || true
    rm /etc/systemd/system/rustwallpaper.service || true
  ;;
  1)
    # for upgrade
  ;;
esac

%postun
case "$1" in
  0)
    # for uninstall
    rm -f /usr/bin/rustwallpaper || true
    rmdir /usr/lib/rustdesk || true
    rmdir /usr/local/rustdesk || true
    rmdir /usr/share/rustdesk || true
    rm /usr/share/applications/rustdesk.desktop || true
    rm /usr/share/applications/rustdesk-link.desktop || true
    update-desktop-database
  ;;
  1)
    # for upgrade
    rmdir /usr/lib/rustdesk || true
    rmdir /usr/local/rustdesk || true
  ;;
esac
