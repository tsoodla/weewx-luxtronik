# installer for luxtronik

from weecfg.extension import ExtensionInstaller


def loader():
    return LuxtronikInstaller()

class LuxtronikInstaller(ExtensionInstaller):
    def __init__(self):
        super(LuxtronikInstaller, self).__init__(
            version="0.2",
            name='luxtronik',
            description='Augment station data with data from Luxtronik heatpump controller.',
            author="Tarmo Soodla",
            author_email="tsoodla@gmail.com",
            process_services='user.luxtronik.Luxtronik',
            config={
                'Luxtronik': {
                    'host': 'REPLACE_ME_WITH_CORRECT_IP_ADDRESS',
                    'port': '8889'
                }
            },
            files=[('bin/user', ['bin/user/luxtronik.py'])]
        )

