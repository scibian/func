##
## NetApp Filer 'Vol' Module
##
## Copyright 2008, Red Hat, Inc
## John Eckersberg <jeckersb@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import re
from func.minion.modules import func_module
from func.minion.modules.netapp.common import *

class Vol(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Interface to the 'vol' command"

    def create(self, filer, vol, aggr, size):
        """
        TODO: Document me ...
        """
        regex = """Creation of volume .* has completed."""
        cmd_opts = ['vol', 'create', vol, aggr, size]
        output = ssh(filer, cmd_opts)
        return check_output(regex, output)

    def destroy(self, filer, vol):
        """
        TODO: Document me ...
        """
        regex = """Volume .* destroyed."""
        cmd_opts = ['vol', 'destroy', vol, '-f']
        output = ssh(filer, cmd_opts)
        return check_output(regex, output)

    def offline(self, filer, vol):
        """
        TODO: Document me ...
        """
        regex = """Volume .* is now offline."""
        cmd_opts = ['vol', 'offline', vol]
        output = ssh(filer, cmd_opts)
        return check_output(regex, output)

    def online(self, filer, vol):
        """
        TODO: Document me ...
        """
        regex = """Volume .* is now online."""
        cmd_opts = ['vol', 'online', vol]
        output = ssh(filer, cmd_opts)
        return check_output(regex, output)

    def status(self, filer, vol=None):
        """
        TODO: Document me ...
        """
        cmd_opts = ['vol', 'status']
        output = ssh(filer, cmd_opts)

        output = output.replace(',', ' ')
        lines = output.split('\n')[1:]

        vols = []
        current_vol = {}
        for line in lines:
            tokens = line.split()
            if len(tokens) >= 2 and tokens[1] in ('online', 'offline', 'restricted'):
                if current_vol: vols.append(current_vol)
                current_vol = {'name': tokens[0],
                               'state': tokens[1],
                               'status': [foo for foo in tokens[2:] if '=' not in foo],
                               'options': [foo for foo in tokens[2:] if '=' in foo]}
            else:
                current_vol['status'].extend([foo for foo in tokens if '=' not in foo])
                current_vol['options'].extend([foo for foo in tokens if '=' in foo])
        vols.append(current_vol)

        if vol:
            try:
                return [foo for foo in vols if foo['name'] == vol][0]
            except:
                raise NetappCommandError, "No such volume: %s" % vol
        else:
            return vols

    def size(self, filer, vol, delta=None):
        """
        TODO: Document me ...
        """
        stat_regex = """vol size: Flexible volume .* has size .*."""
        resize_regex = """vol size: Flexible volume .* size set to .*."""
        cmd_opts = ['vol', 'size', vol]

        if delta:
            cmd_opts.append(delta)
            output = ssh(filer, cmd_opts)
            return check_output(resize_regex, output)
        else:
            output = ssh(filer, cmd_opts)
            check_output(stat_regex, output)
            return output.split()[-1][:-1]

    def options(self, filer, args):
        """
        TODO: Document me ...
        """
        pass

    def rename(self, filer, args):
        """
        TODO: Document me ...
        """
        pass

    def restrict(self, filer, args):
        """
        TODO: Document me ...
        """
        pass

    def register_method_args(self):
        """
        Implementing the method argument getter
        """
        vol = {
                'type':'string',
                'optional':False,
                'description':"The name of the volume"
                }

        filer = {
                'type':'string',
                'optional':False,
                'description':"Resolvable name of the target filer"
                }

        return {

                'create':{
                    'args':{
                        'filer':filer,
                        'vol':vol,
                        'aggr':{
                            'type':'string',
                            'optional':False,
                            'description':'Aggregate in which to create the new volume (e.g. aggr0)'
                            },
                        'size':{
                            'type':'string',
                            'optional':False,
                            'description':'Size of the new volume (e.g. 500g)'
                            }
                        },
                    'description':"Returns True if volume is created successfully"

                    },
                'destroy':{
                    'args':{
                        'filer':filer,
                        'vol':vol
                        },
                    'description':"Returns True if volume is successfully destroyed"

                    },
                'offline':{
                    'args':{
                        'filer':filer,
                        'vol':vol
                        },
                    'description':"Returns True if volume is successfully offlined"
                    },
                'online':{
                    'args':{
                        'filer':filer,
                        'vol':vol
                        },
                    'description':"Returns True if volume is successfully onlined"
                        },
                'status':{
                    'args':{
                        'filer':filer,
                        'vol':vol
                        },
                    'description':"If vol is not given, returns a list of dictionaries containing the status information of each volume in the system If vol is given, return just the dictionary for the given volume "
                        },
                'size':{
                    'args':{
                        'filer':filer,
                        'vol':vol,
                        'delta':{
                            'type':'string',
                            'optional':True,
                            'description':'Optional change in size (e.g. +200g or -50g)'
                            }
                        },
                    'description':"If delta is not given, return the size of the given volume (e.g. '500g') If delta is given, return True if volume is successfully resized "
                    }
                }
