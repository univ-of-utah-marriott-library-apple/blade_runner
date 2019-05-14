# -*- coding: utf-8 -*-
#################################################################################
# TempApp was developed by mikeymikey, aka pudquick or frogor. The blog post that
# details this script can be found here:
#
#       https://michaellynn.github.io/2015/07/31/customized-python-app-bundles/
#
# It has been modified to fit the purposes of Blade Runner, mainly by adding
# `python_bin` as an argument, an if else statement so that the python binary
# path can be specified, and the ability to use TempApp when run as root.
#
# Big thanks to mikeymikey for allowing us to change Python's icon!
#################################################################################

import sys, os, os.path, tempfile, plistlib, shutil, subprocess


class TempApp(object):
    def __init__(self, infoPlist_dict, app_path=None, bundle_name='TempApp', cleanup=True, app_icon=None, python_bin=None):
        # infoPlist_dict: A dict containing key values that should be set/overridden
        #                 vs. the normal Python.app keys.
        #       app_path: The path to where your app should go. Example: '/usr/local/myOrgStuff'
        #                 This directory needs to pre-exist. If app_path is left at None,
        #                 a temporary directory will be created and used and the value of
        #                 cleanup will be forced to True
        #    bundle_name: The name of your .app. This tends to be what shows in the Dock.
        #                 Spaces in the name are ok, but keep it short.
        #        cleanup: If app_path is provided, cleanup set to False will leave the .app
        #                 bundle behind rather than removing it on object destruction.
        #       app_icon: Set to the path of a .icns file if you wish to have a custom app icon
        #
        # Setup our defaults
        super(type(self), self).__init__()
        self.path           = None
        self.cleanup_parent = False
        self.cleanup        = cleanup
        self.returncode     = 0
        self.python_path    = None
        # First we look up which python we're running with so we know which Python.app to clone
        # ... We'll just cheat and use the path of 'os' which we already imported. The else statement
        # comes into play if the python binary was explicitly specified.
        if python_bin is None:
            base_python = os.__file__.split(os.path.join('lib', 'python2'),1)[0]
        else:
            base_python = os.path.realpath(python_bin).split('bin/python2')[0]

        python_app  = os.path.join(base_python, 'Resources', 'Python.app')

        app_name = '%s.app' % (os.path.basename(bundle_name))
        # Now we setup where we want the new Python.app clone to go
        if app_path is None:
            # Dynamically generate a path and force the value of cleanup
            self.cleanup        = True
            # Also need to cleanup the temp directory we made
            self.cleanup_parent = True
            app_path  = tempfile.mkdtemp()
        else:
            # Verify the parent path exists
            # Trim trailing slashes
            tmp_path = os.path.normpath(app_path)
            if not os.path.exists(tmp_path):
                raise Exception('app_path supplied "%s" does not exist' % app_path)
            elif not os.path.isdir(tmp_path):
                raise Exception('app_path supplied "%s" does not appear to be a directory' % app_path)
            app_path = tmp_path
        if app_icon is not None:
            if not os.path.exists(app_icon):
                raise Exception('app_icon supplied "%s" does not exist' % app_icon)
            elif not os.path.isfile(app_icon):
                raise Exception('app_icon supplied "%s" does not appear to be a file' % app_icon)
        self.path = os.path.join(app_path, app_name)
        # Make the bundle directory
        os.mkdir(self.path)
        os.makedirs(os.path.join(self.path, 'Contents', 'MacOS'))
        # Set up symlink contents
        os.symlink(os.path.join(python_app, 'Contents', 'MacOS', 'Python'), os.path.join(self.path, 'Contents', 'MacOS', 'Python'))
        os.symlink(os.path.join(python_app, 'Contents', 'PkgInfo'), os.path.join(self.path, 'Contents', 'PkgInfo'))
        if app_icon is not None:
            # We create a custom Resources folder and copy the .icns file to the default 'PythonInterpreter.icns' inside
            os.makedirs(os.path.join(self.path, 'Contents', 'Resources'))
            shutil.copyfile(app_icon, os.path.join(self.path, 'Contents', 'Resources', 'PythonInterpreter.icns'))
        else:
            # No app_icon provided, just use the default resources
            os.symlink(os.path.join(python_app, 'Contents', 'Resources'), os.path.join(self.path, 'Contents', 'Resources'))
        os.symlink(os.path.join(python_app, 'Contents', 'version.plist'), os.path.join(self.path, 'Contents', 'version.plist'))
        # Grab the contents of the existing Info.plist ... yes, using plistlib - this Info.plist is so far only XML ...
        original_infoPlist = plistlib.readPlist(os.path.join(python_app, 'Contents', 'Info.plist'))
        # Make our changes from infoPlist_dict
        original_infoPlist.update(infoPlist_dict)
        # Write the contents back to the new location
        plistlib.writePlist(original_infoPlist, os.path.join(self.path, 'Contents', 'Info.plist'))

        self.python_path = os.path.join(self.path, 'Content/MacOS/Python')

        # If run as root, a temp app will be created but inaccessible to the logged in user. To allow access to the
        # temp app, the temp app's owner must be changed to the logged in user.
        if os.geteuid() == 0:
            subprocess.check_output(['chown', '-R', os.getlogin(), os.path.dirname(self.path)])

    def cleanup_app(self):
        # Kill the process if it's still running
        if self.cleanup:
            # Delete the .app bundle, best effort
            try:
                shutil.rmtree(self.path, True)
            except:
                pass
        if self.cleanup_parent:
            # This was an auto-generated directory, remove it as well
            try:
                shutil.rmtree(os.path.dirname(self.path), True)
            except:
                pass

    def __del__(self):
        self.cleanup_app()