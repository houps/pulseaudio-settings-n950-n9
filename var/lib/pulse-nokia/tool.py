#!/usr/bin/env python2.6

import os
import sys
from optparse import OptionParser, OptionGroup, SUPPRESS_HELP

global DEBUG_PRINT
DEBUG_PRINT=False
ALGS_DIR="algs"
MODES_DIR="modes"

def main():
    parser = OptionParser(description="Simple script to list how different algorithm sets "
                                      "are enabled for particular audio mode.")
    group = OptionGroup(parser, "Arguments")
    # string arguments
    group.add_option("", "--alg", dest="algorithm_name",
            help="Algorithm name", metavar="NAME")
    group.add_option("", "--set", dest="set_name",
            help="Algorithm set name", metavar="NAME")
    group.add_option("", "--mode", dest="mode_name",
            help="Mode name", metavar="NAME")
    parser.add_option_group(group)

    # actions
    parser.add_option("-l", "--list", action="store_true", dest="list_data",
            help="List algorithm sets, default to \"all\"")
    parser.add_option("-u", "--unused", action="store_true", dest="list_unused",
            help="List unused algorithm sets, default to \"all\"")
    parser.add_option("-m", "--list-mode", action="store_true", dest="list_mode",
            help="List sets used in a mode, default to \"all\"")
    parser.add_option("-a", "--add", action="store_true", dest="add_mode",
            help="Add algorithm set to mode")
    parser.add_option("-d", "--del", action="store_true", dest="del_mode",
            help="Remove algorithm set from mode")
    parser.add_option("-e", "--edit", action="store_true", dest="edit",
            help="Run '$EDITOR algs/ALGORITHM/SET'")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
            help=SUPPRESS_HELP)

    options, args = parser.parse_args()

    pulse_alg_dir = os.environ.get("PULSE_ALG_DIR", None)
    if (pulse_alg_dir):
        os.chdir(pulse_alg_dir)

    if not os.path.isdir(MODES_DIR) and not os.path.isdir(ALGS_DIR):
        eprint("Error: are you running this from var/lib/pulse-nokia ?")
        eprint("(or enable PULSE_ALG_DIR environment variable)", exit=1)
        return

    if len(args) > 0:
        parser.print_help()
        return

    if options.verbose:
        global DEBUG_PRINT
        DEBUG_PRINT=True

    alg_dict, mode_dict = generate_tree()

    if options.list_data or options.list_unused:
        if options.algorithm_name:
            name = options.algorithm_name
        else:
            name = None

        if options.list_data:
            list(alg_dict, name)
        else:
            list_unused(alg_dict, name)

    elif options.list_mode:
        if options.mode_name:
            name = options.mode_name
        else:
            name = None

        list_mode(mode_dict, name)

    elif options.add_mode:
        if options.algorithm_name and options.mode_name and options.set_name:
            add_mode(alg_dict, mode_dict, options.algorithm_name, options.mode_name, options.set_name)
        else:
            eprint("Arguments: algorithm, mode, and set names required.", exit=2)

    elif options.del_mode:
        if options.algorithm_name and options.mode_name:
            del_mode(mode_dict, options.algorithm_name, options.mode_name)
        else:
            eprint("Arguments: algorithm and mode names required.", exit=2)

    elif options.edit:
        if options.algorithm_name and options.set_name:
            os.system("$EDITOR %s" % os.path.join(ALGS_DIR, options.algorithm_name, options.set_name))
        else:
            eprint("Arguments: algorithm and set names required.", exit=2)

    else:
        parser.print_help()

def list_single_mode(mode):
    assert mode

    print "Mode \"%s\":" % mode.name
    for alg_set in mode.enabled_sets:
        print "%s\"%s\",  \"%s\"" % (" "*2, alg_set.parent.name, alg_set.name)

def list_mode(mode_dict, mode_name=None):
    assert mode_dict

    if (mode_name):
        if not mode_name in mode_dict:
            eprint("Error: mode \"%s\" not found." % mode_name, exit=3)
        else:
            list_single_mode(mode_dict[mode_name])
    else:
        for k,mode in mode_dict.iteritems():
            list_single_mode(mode)


def del_mode(mode_dict, alg_name, mode_name):
    assert mode_dict
    assert alg_name
    assert mode_name

    if not mode_name in mode_dict:
        eprint("Error: mode \"%s\" not found." % mode_name, exit=3)
        return

    mode = mode_dict[mode_name]

    for alg_set in mode.enabled_sets:
        if alg_set.parent.name == alg_name:
            os.remove(os.path.join(MODES_DIR, mode_name, alg_name))
            return

    # error
    eprint("Error: couldn't find algorithm set for \"%s\"." % alg_name, exit=3)

def add_mode(alg_dict, mode_dict, alg_name, mode_name, set_name):
    assert alg_dict
    assert type(alg_name) == type("")
    assert type(mode_name) == type("")
    assert type(set_name) == type("")

    if not alg_name in alg_dict:
        eprint("Error: algorithm \"%s\" not found." % alg_name, exit=3)
        return

    alg = alg_dict[alg_name]

    if not set_name in alg.sets:
        eprint("Error: set \"%s\" not found in algorithm \"%s\"." % (set_name, alg_name), exit=3)
        return

    s = alg.sets[set_name]

    if mode_name in s.modes:
        eprint("Error: set \"%s\" is already enabled for mode \"%s\"." % (set_name, mode_name), exit=3)
        return

    if not mode_name in mode_dict:
        eprint("Error: mode \"%s\" not available (tip: mkdir %s)." % (mode_name, os.path.join(MODES_DIR, mode_name)), exit=3)
        return

    m = mode_dict[mode_name]
    for alg_set in m.enabled_sets:
        if alg_set.parent == alg:
            eprint("Error: algorithm set \"%s\" already enabled for mode \"%s\"." % (alg_set.name, mode_name), exit=3)
            return

    os.symlink("../../%s/%s/%s" % (ALGS_DIR, alg_name, set_name), "%s/%s/%s" % (MODES_DIR, mode_name, alg_name))

def list_unused_alg(alg):
    assert alg

    header_printed = False
    for j,alg_set in alg.sets.iteritems():
        if len(alg_set.modes) == 0:
            if not header_printed:
                header_printed = True
                print "Algorithm \"%s\":" % alg.name
            print "%sset \"%s\"" % (" "*2, alg_set.name)

def list_unused(alg_dict, string=None):
    assert alg_dict

    if string:
        if string in alg_dict:
            list_unused_alg(alg_dict[string])
        else:
            eprint("Error: algorithm \"%s\" not found." % string, exit=3)
    else:
        for k,alg in alg_dict.iteritems():
            list_unused_alg(alg)

def list_alg(alg):
    assert alg

    print "Algorithm \"%s\":" % alg.name
    for k,alg_set in alg.sets.iteritems():
        if len(alg_set.modes) > 0:
            print "%sset \"%s\" used in mode(s):" % (" "*2, alg_set.name)
            for j,mode in alg_set.modes.iteritems():
                print "%s%s" % (" "*4, mode.name)
        else:
            print "%sset \"%s\" not used at all" % (" "*2, alg_set.name)


def list(alg_dict, string=None):
    assert alg_dict

    if string:
        if string in alg_dict:
            list_alg(alg_dict[string])
        else:
            eprint("Error: algorithm \"%s\" not found." % string, exit=3)
    else:
        for k,alg in alg_dict.iteritems():
            list_alg(alg)

def dprint(string):
    if DEBUG_PRINT:
        print string

def eprint(string, exit=None):
    sys.stderr.write("%s\n" % string)
    if not exit is None:
        sys.exit(exit)

class Algorithm:
    def __init__(self, name):
        assert type(name) == type("")
        self.name = name
        self.sets = {} # string (set name) : AlgorithmSet()

    def dir(self):
        return self.name

class AlgorithmSet:
    def __init__(self, parent, name, realpath):
        # parent is Algorithm
        assert parent
        assert parent.__class__.__name__ == Algorithm.__name__
        assert type(name) == type("")
        assert type(realpath) == type("")
        self.parent = parent
        self.name = name
        self.realpath = realpath
        self.modes = {} # string (mode name) : AlgorithmMode()

    def dir(self):
        return "/".join([self.parent.dir(), self.name])

class AlgorithmMode:
    def __init__(self, name, realpath):
        assert type(name) == type("")
        assert type(realpath) == type("")
        self.name = name
        self.realpath = realpath
        self.enabled_sets = []

    def add(self, alg): # add to algorithm set
        assert alg
        assert alg.__class__.__name__ == AlgorithmSet.__name__
        self.enabled_sets.append(alg)

def generate_tree():
    algs = {} # string(algorithm dir name) : Algorithm()
    modes = {} # available modes, string(mode dir name) : AlgorithmMode()

    # first add algorithms and sets
    for root, dirs, files in os.walk(ALGS_DIR):
        if root == ALGS_DIR:
            dprint("check algs root")
            for dir in dirs:
                algs[dir] = Algorithm(dir)
            continue

        alg_name = os.path.basename(root)
        if alg_name in algs:
            alg = algs[alg_name]
            dprint("adding sets to algorithm %s" % alg.name)
            for file in files:
                realpath = os.path.realpath(os.path.join(root, file))
                alg.sets[file] = AlgorithmSet(alg, file, realpath)
                dprint(" -> %s ( %s )" % (file, alg.sets[file].dir()))

    # then add modes and associate sets to modes
    for root, dirs, files in os.walk(MODES_DIR):
        if root == MODES_DIR:
            dprint("check modes root")
            for dir in dirs:
                realpath = os.path.realpath(os.path.join(root, dir))
                modes[dir] = AlgorithmMode(dir, realpath)
                dprint("mode %s" % dir)
            continue

        mode_name = os.path.basename(root)
        if mode_name in modes:
            m = modes[mode_name]
            for file in files:
                realpath = os.path.realpath(os.path.join(root, file))
                for k,alg in algs.iteritems():
                    for j,alg_set in alg.sets.iteritems():
                        if realpath == alg_set.realpath:
                            alg_set.modes[m.name] = m
                            m.add(alg_set)

    return algs, modes

if __name__ == "__main__":
    main()

