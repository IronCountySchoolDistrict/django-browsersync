"""Runserver command with bsync"""
from optparse import make_option

from django.conf import settings
from django.core.management.color import color_style
import os

if 'django.contrib.staticfiles' in settings.INSTALLED_APPS:
    from django.contrib.staticfiles.management.commands.runserver import \
        Command as RunserverCommand
else:
    from django.core.management.commands.runserver import \
        Command as RunserverCommand


class Command(RunserverCommand):
    """
    Command for running the development server with bsync.
    """
    if callable(getattr(RunserverCommand, 'add_arguments', None)):
        def add_arguments(self, parser):
            super(Command, self).add_arguments(parser)
            parser.add_argument('--nobsync', action='store_false',
                                dest='use_bsync', default=True,
                                help='Tells Django to NOT use bsync.')
            parser.add_argument('--bsync-port', action='store',
                                dest='bsync_port', default='',
                                help='Port where browser-sync listen.')
    else:
        option_list = RunserverCommand.option_list + (
                make_option('--nobsync', action='store_false',
                            dest='use_bsync', default=True,
                            help='Tells Django to NOT use bsync.'),
                make_option('--bsync-port', action='store',
                            dest='bsync_port', default='',
                            help='Port where browser-sync listen.'),
        )

    help = 'Starts a lightweight Web server for development with browser-sync reload.'

    def message(self, message, verbosity=1, style=None):
        if verbosity:
            if style:
                message = style(message)
            self.stdout.write(message)

    def bsync_request(self, **options):
        """
        Performs the bsync request.
        """
        style = color_style()
        verbosity = int(options['verbosity'])

        bsync_port = options['bsync_port']

        if options['bsync_port']:
            sub_cmd = " --port {}".format(bsync_port)
        else:
            sub_cmd = ""

        cmd = "browser-sync reload{}".format(sub_cmd)

        # host = 'localhost:%s' % options['bsync_port']
        try:
            os.system(cmd)
            #urlopen('http://%s/changed?files=.' % host)
            self.message('bsync request emitted. cmd ={}\n'.format(cmd),
                         verbosity, style.HTTP_INFO)
        except IOError:
            pass

    def get_handler(self, *args, **options):
        """
        Entry point to plug the bsync feature.
        """
        handler = super(Command, self).get_handler(*args, **options)
        if options['use_bsync']:
            self.bsync_request(**options)
        return handler