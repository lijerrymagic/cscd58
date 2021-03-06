"""
  CLI interface for iis_service_backbone management.
"""

from __future__ import print_function

import argparse
import os
import sys

import pbr
import six
from oslo_config import cfg
from oslo_log import log as logging

from iis_service_backbone import config
from iis_service_backbone import context
from iis_service_backbone import db
from iis_service_backbone import exception
from iis_service_backbone import version
from iis_service_backbone.common import cliutils
from iis_service_backbone.db import migration
from iis_service_backbone.i18n import _
from iis_service_backbone.plugin import manager

CONF = cfg.CONF


# Decorators for actions
def args(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('args', []).insert(0, (args, kwargs))
        return func
    return _decorator


class ShellCommands(object):
    def bpython(self):
        """Runs a bpython shell.

        Falls back to Ipython/python shell if unavailable
        """
        self.run('bpython')

    def ipython(self):
        """Runs an Ipython shell.

        Falls back to Python shell if unavailable
        """
        self.run('ipython')

    def python(self):
        """Runs a python shell.

        Falls back to Python shell if unavailable
        """
        self.run('python')

    @args('--shell', metavar='<bpython|ipython|python >',
          help='Python shell')
    def run(self, shell=None):
        """Runs a Python interactive interpreter."""
        if not shell:
            shell = 'bpython'

        if shell == 'bpython':
            try:
                import bpython
                bpython.embed()
            except ImportError:
                shell = 'ipython'
        if shell == 'ipython':
            try:
                from IPython import embed
                embed()
            except ImportError:
                try:
                    # Ipython < 0.11
                    # Explicitly pass an empty list as arguments, because
                    # otherwise IPython would use sys.argv from this script.
                    import IPython

                    shell = IPython.Shell.IPShell(argv=[])
                    shell.mainloop()
                except ImportError:
                    # no IPython module
                    shell = 'python'

        if shell == 'python':
            import code
            try:
                # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try',
                # because we already know 'readline' was imported successfully.
                readline.parse_and_bind("tab:complete")
            code.interact()

    @args('--path', metavar='<path>', help='Script path')
    def script(self, path):
        """Runs the script from the specified path with flags set properly.

        arguments: path
        """
        exec(compile(open(path).read(), path, 'exec'), locals(), globals())


def _db_error(caught_exception):
    print(caught_exception)
    print(_("The above error may show that the database has not "
            "been created.\nPlease create a database using "
            "'iis_service_backbone-manage db sync' before running this command."))
    exit(1)


class DbCommands(object):
    """Class for managing the main database."""

    def __init__(self):
        pass

    @args('--version', metavar='<version>', help='Database version')
    @args('--plugin', metavar='<plugin>', help='Business plugin')
    def sync(self, version=None, plugin=None):
        """Sync the database up to the most recent version."""

        if plugin is not None:
            return manager.sync_db(version, plugin)
        return migration.db_sync(version)

    @args('--plugin', metavar='<plugin>', help='Business plugin')
    def version(self,plugin=None):
        """Print the current database version."""
        if plugin is not None:
            print(manager.db_version(plugin))
        else:
            print(migration.db_version())

    @args('--max_rows', metavar='<number>',
          help='Maximum number of deleted rows to archive')
    def archive_deleted_rows(self, max_rows):
        """Move up to max_rows deleted rows from production tables to shadow
        tables.
        """
        if max_rows is not None:
            max_rows = int(max_rows)
            if max_rows < 0:
                print(_("Must supply a positive value for max_rows"))
                return(1)
        admin_context = context.get_admin_context()
        db.archive_deleted_rows(admin_context, max_rows)


class GetLogCommands(object):
    """Get logging information."""

    def errors(self):
        """Get all of the errors from the log files."""
        error_found = 0
        if CONF.log_dir:
            logs = [x for x in os.listdir(CONF.log_dir) if x.endswith('.log')]
            for file in logs:
                log_file = os.path.join(CONF.log_dir, file)
                lines = [line.strip() for line in open(log_file, "r")]
                lines.reverse()
                print_name = 0
                for index, line in enumerate(lines):
                    if line.find(" ERROR ") > 0:
                        error_found += 1
                        if print_name == 0:
                            print(log_file + ":-")
                            print_name = 1
                        linenum = len(lines) - index
                        print((_('Line %(linenum)d : %(line)s') %
                               {'linenum': linenum, 'line': line}))
        if error_found == 0:
            print(_('No errors in logfiles!'))

    @args('--num_entries', metavar='<number of entries>',
          help='number of entries(default: 10)')
    def syslog(self, num_entries=10):
        """Get <num_entries> of the iis_service_backbone syslog events."""
        entries = int(num_entries)
        count = 0
        log_file = ''
        if os.path.exists('/var/log/syslog'):
            log_file = '/var/log/syslog'
        elif os.path.exists('/var/log/messages'):
            log_file = '/var/log/messages'
        else:
            print(_('Unable to find system log file!'))
            return(1)
        lines = [line.strip() for line in open(log_file, "r")]
        lines.reverse()
        print(_('Last %s iis_service_backbone syslog entries:-') % (entries))
        for line in lines:
            if line.find("iis_service_backbone") > 0:
                count += 1
                print("%s" % line)
            if count == entries:
                break

        if count == 0:
            print(_('No iis_service_backbone entries in syslog!'))


CATEGORIES = {
    'db': DbCommands,
    'logs': GetLogCommands,
    'shell': ShellCommands,
}


def methods_of(obj):
    """Get all callable methods of an object that don't start with underscore

    returns a list of tuples of the form (method_name, method)
    """
    result = []
    for i in dir(obj):
        if callable(getattr(obj, i)) and not i.startswith('_'):
            result.append((i, getattr(obj, i)))
    return result


def add_command_parsers(subparsers):
    parser = subparsers.add_parser('version')

    parser = subparsers.add_parser('bash-completion')
    parser.add_argument('query_category', nargs='?')

    for category in CATEGORIES:
        command_object = CATEGORIES[category]()

        desc = getattr(command_object, 'description', None)
        parser = subparsers.add_parser(category, description=desc)
        parser.set_defaults(command_object=command_object)

        category_subparsers = parser.add_subparsers(dest='action')

        for (action, action_fn) in methods_of(command_object):
            parser = category_subparsers.add_parser(action, description=desc)

            action_kwargs = []
            for args, kwargs in getattr(action_fn, 'args', []):
                # FIXME(markmc): hack to assume dest is the arg name without
                # the leading hyphens if no dest is supplied
                kwargs.setdefault('dest', args[0][2:])
                if kwargs['dest'].startswith('action_kwarg_'):
                    action_kwargs.append(
                        kwargs['dest'][len('action_kwarg_'):])
                else:
                    action_kwargs.append(kwargs['dest'])
                    kwargs['dest'] = 'action_kwarg_' + kwargs['dest']

                parser.add_argument(*args, **kwargs)

            parser.set_defaults(action_fn=action_fn)
            parser.set_defaults(action_kwargs=action_kwargs)

            parser.add_argument('action_args', nargs='*',
                                help=argparse.SUPPRESS)


category_opt = cfg.SubCommandOpt('category',
                                 title='Command categories',
                                 help='Available categories',
                                 handler=add_command_parsers)


def main():
    """Parse options and call the appropriate class/method."""
    CONF.register_cli_opt(category_opt)
    try:
        config.configure()

        CONF(
            args=sys.argv[1:],
            version=pbr.version.VersionInfo('iis_service_backbone').version_string(),
            project='iis_service_backbone',
            default_config_files=None)
        config.setup_logging()
    except cfg.ConfigFilesNotFoundError:
        cfgfile = CONF.config_file[-1] if CONF.config_file else None
        if cfgfile and not os.access(cfgfile, os.R_OK):
            st = os.stat(cfgfile)
            print(_("Could not read %s. Re-running with sudo") % cfgfile)
            try:
                os.execvp('sudo', ['sudo', '-u', '#%s' % st.st_uid] + sys.argv)
            except Exception:
                print(_('sudo failed, continuing as if nothing happened'))

        print(_('Please re-run iis_service_backbone-manage as root.'))
        return(2)

    if CONF.category.name == "version":
        print(version.version_string_with_package())
        return(0)

    if CONF.category.name == "bash-completion":
        if not CONF.category.query_category:
            print(" ".join(CATEGORIES.keys()))
        elif CONF.category.query_category in CATEGORIES:
            fn = CATEGORIES[CONF.category.query_category]
            command_object = fn()
            actions = methods_of(command_object)
            print(" ".join([k for (k, v) in actions]))
        return(0)

    fn = CONF.category.action_fn
    fn_args = [arg.decode('utf-8') for arg in CONF.category.action_args]
    fn_kwargs = {}
    for k in CONF.category.action_kwargs:
        v = getattr(CONF.category, 'action_kwarg_' + k)
        if v is None:
            continue
        if isinstance(v, six.string_types):
            v = v.decode('utf-8')
        fn_kwargs[k] = v

    # call the action with the remaining arguments
    # check arguments
    try:
        cliutils.validate_args(fn, *fn_args, **fn_kwargs)
    except cliutils.MissingArgs as e:
        # NOTE(mikal): this isn't the most helpful error message ever. It is
        # long, and tells you a lot of things you probably don't want to know
        # if you just got a single arg wrong.
        print(fn.__doc__)
        CONF.print_help()
        print(e)
        return(1)
    try:
        ret = fn(*fn_args, **fn_kwargs)
        return(ret)
    except Exception:
        print(_("Command failed, please check log for more info"))
        raise
