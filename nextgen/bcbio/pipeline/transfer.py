"""File transfer handling
"""
import os

try:
    import fabric.api as fabric
    import fabric.contrib.files as fabric_files
except ImportError:
    fabric, fabric_files = (None, None)

from bcbio.pipeline import log


def remote_copy(remote_info, base_dir, protocol):
    """Securely copy files between servers.
    """
    # fc_dir = os.path.join(base_dir, os.path.basename(remote_info['directory']))
    fc_dir = base_dir

    if not fabric_files.exists(fc_dir):
        fabric.run("mkdir %s" % fc_dir)

    if protocol == "scp" or protocol == None:
        for fcopy in remote_info['to_copy']:
            target_loc = os.path.join(fc_dir, fcopy)
            if not fabric_files.exists(target_loc):
                target_dir = os.path.dirname(target_loc)
                if not fabric_files.exists(target_dir):
                    fabric.run("mkdir -p %s" % target_dir)

                cl = ["scp", "-r", "%s@%s:%s/%s" %
                      (remote_info["user"], remote_info["hostname"],
                      remote_info["directory"], fcopy),
                      target_loc]

                log.debug(cl)
                fabric.run(" ".join(cl))

    elif protocol == "rsync":
        include = []
        for fcopy in remote_info['to_copy']:
            # include.append("--include='%s/%s'" % \
            # (remote_info["directory"], fcopy))
            include.append("--include='%s/*'" % (fcopy,))
            include.append("--include='%s'" % (fcopy,))
            # By including both these patterns we get the entire directory
            # if a directory is given, or a single file if a single file is
            # given.
        # for fcopy in remote_info['to_copy']:
        #     target_loc = os.path.join(fc_dir, fcopy)
        #     target_dir = os.path.dirname(target_loc)

        #     if not fabric_files.exists(target_dir):
        #         fabric.run("mkdir -p %s" % target_dir)

        #     if os.path.isdir("%s/%s" % (remote_info["directory"], fcopy)) \
        #     and fcopy[-1] != "/":
        #         fcopy += "/"

        #     # Option -P --append should enable resuming progress on
        #     # partial transfers.
        #     cl = ["rsync", "--checksum", "--recursive", "--archive", \
        #             "--compress", "--partial", "--progress", "--append", \
        #             "--prune-empty-dirs", "--verbose", "%s@%s:%s/%s" % \
        #             (remote_info["user"], remote_info["hostname"], \
        #             remote_info["directory"], fcopy), fc_dir]

        #     logger.debug(cl)
        #     fabric.run(" ".join(cl))

        cl = ["rsync", "--append", "--checksum", "--archive", \
                "--compress", "--inplace", "--partial", "--progress", \
                "--prune-empty-dirs", "--verbose", "--include='*/'", " ".join(include), "--exclude='*'", \
                "%s@%s:%s" % \
                (remote_info["user"], remote_info["hostname"], \
                remote_info["directory"]), fc_dir]

        logger.debug(cl)
        fabric.run(" ".join(cl))

    # Note: rdiff-backup doesn't have the ability to resume a partial transfer,
    # and will instead transfer the backup from the beginning if it detects a
    # partial transfer.
    elif protocol == "rdiff-backup":
        include = []
        for fcopy in remote_info['to_copy']:
            include.append("--include %s/%s" % \
            (remote_info["directory"], fcopy))

        cl = ["rdiff-backup", " ".join(include), "--exclude '**'",
              "%s@%s::%s" % (remote_info["user"], remote_info["hostname"],
              remote_info["directory"]), fc_dir]

        log.debug(cl)
        fabric.run(" ".join(cl))

    return fc_dir
