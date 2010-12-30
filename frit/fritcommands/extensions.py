#!/usr/bin/python
"""
extensions command.
Used to manipulate file based on their extensions.
count is used to count extensions by filesystem.
list is used to list the filenames and path of the specified extensions.
extract is used to extract the specified extensions.
"""
import sys
import os.path
import shutil
import fritutils
import fritutils.termout
import fritutils.fritdb as fritModel

def extractFile(toExtract,destination):
    extractBasename = os.path.basename(toExtract)
    if not os.path.exists(destination):
        os.makedirs(destination)
    if not os.path.exists(destination+extractBasename):
        print 'Extracting "%s" to "%s"' % (toExtract,destination)
        try:
            shutil.copy2(toExtract,destination)
        except IOError:
            fritutils.termout.printWarning('Could not copy "%s" due to IO Error.' % toExtract)


def factory(Evidences, args):
    validArgs = ('count', 'extract','list')
    if not args or len(args) == 0:
        fritutils.termout.printWarning('extensions command need at least an argument to define an action (count, extract or list).')
        sys.exit(1)
    elif args[0] not in validArgs:
        fritutils.termout.printWarning('extensions command need a valid argument (%s)' % ', '.join(validArgs))
        sys.exit(1)
    else:
        if args[0] == 'count':
            # the remaining args should be the extensions that we want to list
            # if there is no more args, we list all extensions
            args.remove('count')
            if not args or len(args) == 0:
                extList = []
                for ex in fritModel.elixir.session.query(fritModel.Extension.extension).all():
                    extList.append(ex[0])
            else:
                extList = []
                for ex in args:
                    extList.append(fritutils.unicodify(ex))
            fritModel.listExtensions(Evidences,extList)
                    
        elif args[0] == 'list':
            args.remove('list')
            if not args or len(args) == 0:
                extList = []
                for ex in fritModel.elixir.session.query(fritModel.Extension.extension).all():
                    extList.append(ex[0])
            else:
                extList = []
                for ex in args:
                    extList.append(fritutils.unicodify(ex))
            for evi in Evidences:
                fritutils.termout.printMessage(evi.configName)
                for fs in evi.fileSystems:
                    fritutils.termout.printMessage("\t%s" % fs.configName)
                    for ext in sorted(extList):
                        for fp in fs.ExtensionsFritFiles(ext,u'Normal'):
                            fritutils.termout.printNormal(fp)
        elif args[0] == 'extract':
            args.remove('extract')
            # The '--merge' option is used to merge extractions in a single
            # directory base instead of having a directory by extension.            
            merge = False
            if '--merge' in args:
                merge = True
                args.remove('--merge')
            if not args or len(args) == 0:
                extList = []
                for ex in fritModel.elixir.session.query(fritModel.Extension.extension).all():
                    extList.append(ex[0])
            else:
                extList = []
                for ex in args:
                    extList.append(fritutils.unicodify(ex))
            for evi in Evidences:
                fritutils.termout.printMessage(evi.configName)
                evi.mount('extensions', 'Extracting files based on extensions')
                for fs in evi.fileSystems:
                    fritutils.termout.printMessage("\t%s" % fs.configName)
                    fs.mount('extensions', 'Extracting files based on extensions')
                    for ext in sorted(extList):
                        nbe = fs.dbCountExtension(ext)
                        fritutils.termout.printMessage("Extracting %d files (%s)" % (nbe['count'],fritutils.humanize(nbe['size'])))
                        for filepath in fs.ExtensionsOriginalFiles(ext,u'Normal'):
                            if ext == "No Extension":
                                extPath = "no_extension"
                            else:
                                extPath = ext[1:]
                            basePath = os.path.dirname(filepath)
                            if merge:
                                Destination = unicode(os.path.join('.frit/extractions/by_extensions/',evi.configName,fs.configName,basePath))
                            else:
                                Destination = unicode(os.path.join('.frit/extractions/by_extensions/',evi.configName,fs.configName,extPath,basePath))
                            mountedPath = os.path.join(fs.fsMountPoint,filepath)
                            extractFile(mountedPath,Destination)
                    fs.umount('extensions')
                evi.umount('extensions')
