weewx-luxtronik - WeeWX service for Luxtronik heatpump controller

Installation instructions

1) install the extension

wee_extension --install=weewx-luxtronik

2) put correct ip address to WeeWX configuration file [Luxtronik] host section

3) restart WeeWX

sudo /etc/init.d/weewx stop
sudo /etc/init.d/weewx start


Manual installation instructions

1) copy the weewx-luxtronik service file to the WeeWX user directory

cp luxtronik.py /home/weewx/bin/user

2) in the WeeWX configuration file, add a new [Luxtronik] stanza

[Luxtronik]
    host = REPLACE_ME_WITH_CORRECT_IP_ADDRESS
    port = 8889

3) in the WeeWX configuration file, add the luxtronik service

[Engine]
    [[Services]]
        process_services = ..., user.luxtronik.Luxtronik

4) restart WeeWX

sudo /etc/init.d/weewx stop
sudo /etc/init.d/weewx start
