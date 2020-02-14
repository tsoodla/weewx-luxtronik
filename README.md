# WeeWX service for Luxtronik heatpump controller

This is a service for [WeeWX](http://weewx.com/) that collects data from Luxtronik heatpump controllers.

## Installation instructions

1) install the extension

```
sudo wee_extension --install=weewx-luxtronik.tar.gz
```

2) put correct IP address to WeeWX configuration file [Luxtronik] host section

3) restart WeeWX

```
sudo systemctl stop weewx
sudo systemctl start weewx
```


## Manual installation instructions

1) copy the weewx-luxtronik service file to the WeeWX user directory

```
cp luxtronik.py /home/weewx/bin/user
```

2) in the WeeWX configuration file, add a new [Luxtronik] stanza

```
[Luxtronik]
    host = REPLACE_ME_WITH_CORRECT_IP_ADDRESS
    port = 8889
```

3) in the WeeWX configuration file, add the luxtronik service

```
[Engine]
    [[Services]]
        process_services = ..., user.luxtronik.Luxtronik
```

4) restart WeeWX

```
sudo systemctl stop weewx
sudo systemctl start weewx
```

Available variables to monitor: https://www.loxwiki.eu/display/LOX/Java+Webinterface
