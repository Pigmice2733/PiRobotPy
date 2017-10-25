#!/bin/bash
if [[ $(hostname) = "localhost" || $(hostname) = "raspberrypi" ]]; then
  printf "Please give this system a unique hostname\nYou will have to do this manually in the following prompt:\n[ENTER to continue]"
  read
  sudo raspi-config
  echo "Rebooting since manually changing the hostname doesn't act as expected... (You could have just said \"yes\" at the last screen."
  read
  sudo reboot
fi
Pass_Phrase=pi2733hotspot
while test $# -gt 0
do
    case "$1" in
        --enable)
            enable_ap=y
            ;;
        --disable)
            enable_ap="n"
            ;;
        --info)
            echo "SSID \"Pi$(hostname)\""
            echo "Pass \"${Pass_Phrase}\""
            exit
            ;;
        --help)
            echo "./wifi_enable.sh"
            echo "    --enable - enables access point"
            echo "    --disable - disables access point"
            echo "    --info - prints out the SSID and Pass"
            echo "             assumes that the AP is enabled"
            exit
            ;;
    esac
    shift
done
while true; do
  if [[ $enable_ap = "" ]]; then
    echo "Enable Access Point [Y/n]"
    read enable_ap
  fi
  if [[ $enable_ap = "" || $enable_ap = "y" || $enable_ap = "Y" ]]; then
    echo "Enabling Access Point..."
    enable_ap=y
    break
  elif [[ $enable_ap = "n" || $enable_ap = "N" ]]; then
    echo "Disabling Access Point..."
    break
  else
    enable_ap=
  fi
done
sudo apt-get install -y hostapd dnsmasq
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo ifdown wlan0 --force
# Remove any previous denyinterfaces
# Probably overkill, better safe than sorry
sudo perl -0777 -pi -e 's/\n{0,2}denyinterfaces wlan0//g' /etc/dhcpcd.conf
if [ $enable_ap = "y" ]; then
  echo "denyinterfaces wlan0" | sudo tee -a /etc/dhcpcd.conf > /dev/null
fi
sudo service dhcpcd restart
sudo perl -0777 -pi -e 's/\n?allow-hotplug wlan0\niface wlan0 inet [a-zA-Z]+(?:\n    .*)*//g' /etc/network/interfaces
if [ $enable_ap = "y" ]; then
echo "allow-hotplug wlan0
iface wlan0 inet static
    address 192.168.0.1
    netmask 255.255.255.0
    network 192.168.0.0
    #wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf" | sudo tee -a /etc/network/interfaces > /dev/null
else
echo "allow-hotplug wlan0
iface wlan0 inet manual
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf" | sudo tee -a /etc/network/interfaces > /dev/null
fi
echo "interface=wlan0
  dhcp-range=192.168.0.2,192.168.0.20,255.255.255.0,24h" | sudo tee /etc/dnsmasq.conf > /dev/null
echo "interface=wlan0
ssid=Pi$(hostname)
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=${Pass_Phrase}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP" | sudo tee /etc/hostapd/hostapd.conf > /dev/null
if [ $enable_ap = "y" ]; then
  sudo sed -i 's/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/g' /etc/default/hostapd
else
  sudo sed -i 's/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/#DAEMON_CONF=""/g' /etc/default/hostapd
fi
if [ $enable_ap = "y" ]; then
  sudo systemctl restart hostapd
  sudo systemctl enable hostapd
  sudo service dnsmasq restart
  sudo systemctl enable dnsmasq
else
  sudo systemctl disable dnsmasq
  sudo systemctl disable dnsmasq
fi
if [ $enable_ap = "y" ]; then
  sudo ifdown wlan0
  sudo ifconfig wlan0 192.168.0.1
else
  sudo ifdown wlan0 > /dev/null
  sudo ifup wlan0
fi
echo "Reboot for the changes to take effect? (Shouldn't be necessary, but if it doesn't work try it)"
echo "SSID \"Pi$(hostname)\""
echo "Pass \"${Pass_Phrase}\""
