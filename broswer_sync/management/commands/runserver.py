"""Runserver command with bsync"""
import atexit
import os
import psutil
import subprocess
import sys
import traceback

from __future__ import print_function
from colors import 
from concurrent.futures import ThreadPoolExecutor
from env_tools import load_env
from optparse import 
from signal import SIGTERM

from django.contrib.staticfiles.management.commands.runserver import Command \
    as StaticfilesRunserverCommand
from django.core.management.base import CommandError
from django.core.servers import basehttp
from django.conf import settings
from django.core.management.color import color_style

@staticmethod
def log_local_message(message_format, *args):
    """
    Log a request so that it matches our local log format.
    """
    prefix = '{} {}'.format(color('INFO', fg=248), color('request', fg=5))
    message = message_format % args

    sys.stderr.write('{} {}\n'.format(prefix, message))

basehttp.WSGIRequestHandler.log_message = log_local_message

class Command(StaticfilesRunserverCommand):
    """
    Subclass the RunserverCommand from Staticfiles to set up our gulp
    environment.
    """

    def __init__(self, *args, **kwargs):
        self.cleanup_closing = False
        self.gulp_process = None

        super(Command, self).__init__(*args, **kwargs)

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

    @staticmethod
    def gulp_exited_cb(future):
        if future.exception():
            print(traceback.format_exc())

            children = psutil.Process().children(recursive=True)

            for child in children:
                print('>>> Killing pid {}'.format(child.pid))

                child.send_signal(SIGTERM)

            print('>>> Exiting')

            # It would be nice to be able to raise a CommandError or use
            # sys.kill here but neither of those stop the runserver instance
            # since we're in a thread. This method is used in django as well.
            os._exit(1)
    
    def kill_gulp_process(self):
        if self.gulp_process.returncode is not None:
            return

        self.cleanup_closing = True
        self.stdout.write('>>> Closing gulp process')

        self.gulp_process.terminate()

    def start_gulp(self):
        self.stdout.write('>>> Starting gulp')

        gulp_command = getattr(settings, 'GULP_DEVELOP_COMMAND', 'gulp')
        self.gulp_process = subprocess.Popen(
            gulp_command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=self.stdout,
            stderr=self.stderr)

        if self.gulp_process.poll() is not None:
            raise CommandError('gulp failed to start')

        self.stdout.write('>>> gulp process on pid {0}'
                          .format(self.gulp_process.pid))

        atexit.register(self.kill_gulp_process)

        self.gulp_process.wait()

        if self.gulp_process.returncode != 0 and not self.cleanup_closing:
            raise CommandError('gulp exited unexpectedly')

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
        try:
            env = load_env()
        except IOError:
            env = {}

        # XXX: In Django 1.8 this changes to:
        # if 'PORT' in env and not options.get('addrport'):
        #     options['addrport'] = env['PORT']

        if 'PORT' in env and not args:
            args = (env['PORT'],)

        # We're subclassing runserver, which spawns threads for its
        # autoreloader with RUN_MAIN set to true, we have to check for
        # this to avoid running gulp twice.
        if not os.getenv('RUN_MAIN', False):
            pool = ThreadPoolExecutor(max_workers=1)

            gulp_thread = pool.submit(self.start_gulp)
            gulp_thread.add_done_callback(self.gulp_exited_cb)

        handler = super(Command, self).get_handler(*args, **options)
        
        if options['use_bsync']:
            self.bsync_request(**options)
        return handler