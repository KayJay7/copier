## Copicat

`copicat` is a simple automated file copying utility, meant to simplify some common file management needs. The project was born when trying to store dotfiles and system configuration files in a repository, changing ownership and permissions of files as needed. It then expanded to also be used to easily move media files between folders.

Get it from [pypi](https://pypi.org/project/copicat/) using your favourite python package manager, no external dependencies required!
* UV: `uv tool install copicat`
* pip: `pip install copicat`

---

Common problems solved by `copicat`:
* Copy files from sparse locations to a new location, with configured common permissions
  * `copicat in [-h] [-D] [config] [owner] [group] [mode]`
* Copy those files back to the original location, with per file permissions
  * `copicat out [-h] [-D] [config]`
* Copy or hardlink all files with a certain mime type from a location to another
  * `copicat type [-h] [-k] [-H] [-T] [-D] source dest [mime]`

You can use the `--dry-run` option, to test your configuration without overwriting files by accident. You can also use it to decide if the tool works for you!

Neat "quality of life" features:
* The `in` and `out` modes operate in opposite way, so the tool is "bidirectional"
* The `--dry-run` option makes for easy testing
* Using a config file for `in` and `out` modes keeps the command simple and readable
* The config file offer very fine control, while avoiding unnecessary repetition
* In `type` mode you can make hardlink instead of copying to save space
  * Hardlinks wouldn't make sense for the other modes
* In case of error the tool will print the problem and continue to the next file without stopping

"Why use this instead of a bunch of symlinks?":
* Symlinks don't work with tools like git
* Symlinks do not change permissions of the file
* Tools like `bindfs` that make symlink transparent to other programs will convert symlinks into regular files without warning

### Configuration file

The `copicat in` and `copicat out` subcommands are meant to operate on the same config file. The config file is a yaml that specifies, user, group and mode for every file to copy, as well as the source and target location of the file.

The basic structure is:
```yaml
user:
    group:
        mode:
            /path/to/source: path/to/target
```

> [!IMPORTANT]
> In yaml sections must be unique in their parent section. I.E.: you cannot have a two section for group `media` inside the section for user `alice`, but you can have one in the section for user `alice` and another one in the section for user `bob`.

`user` and `group` can be both the entity name or numerical id, while mode must be numeric.

If the source is a directory, it will be copied recursively. Because of that, the mode is provided in a custom format that allows specifying different modes for directory. The format also allows specifying special permission like the sticky bit. When directory permission are unspecified, file permissions `+x` will be used.

> [!TIP]
> The config file is processed in order, so you can first copy a full directory all using the same user, group, and mode, and later copy again some files inside that folder to change their permissions.
> This will result in unnecessary copies, but might produce a tidier config file.

> [!WARNING]
> **DO NOT** include **leading zeroes** in the modes! In yaml `0644` and `644` are different numbers.
> If you need to specify mode `070` write only `70`.

Full format description:

```
The first digit in 4 digits modes specify setuid, setgid and sticky bit:

   .----------------- setuid
   |.---------------- setgid
   ||.--------------- sticky bit
   |||  .------------ owner read
   |||  |.----------- owner write
   |||  ||.---------- owner execute/search
   |||  ||| .-------- group read
   |||  ||| |.------- group write
   |||  ||| ||.------ group execute/search
   |||  ||| ||| .---- other read
   |||  ||| ||| |.--- other write
   |||  ||| ||| ||.-- other execute/search
   |||  ||| ||| |||
  (...) ... ... ...
  (421) 421 421 421


If a copy point is a folder, an additional set of permissions can be provided,
the msb permissions will be used on directories.
the fourth digit is now required for the lsb permissions.
if missing, lsb+x permissions will be used:
  (...) ... ... ...  ... ... ... ...
  (421) 421 421 421  421 421 421 421
```

> [!WARNING]
> **DID YOU skip the previous warning?** Make sure you didn't skip it, as this might cause you to lose access to your own files!

Example of a full config file, take your time to read it and understand what it means:
```yml
alvise:
  alvise:
    640:
      "testdir/source1/inner1/c.txt": "testdir/dest1/f.txt"
      "testdir/source1/inner2/d.txt": "testdir/dest1/inner/g.txt"
1000:
  1000:
    2600:
      "testdir/source1/e.txt": "testdir/dest2/h.txt"
  wlanUD:
    644:
      "testdir/source2/a.txt": "testdir/dest2/inner/i.txt"
      "testdir/source2/./a.txt": "testdir/dest2/inner/non-existent/i.txt"
    666:
      "testdir/source2/b.txt": "testdir/dest2/inner/j.txt"
    7440600:
      "testdir/source3": "testdir/dest3"
0:
  0:
    666:
      "testdir/source2/b.txt": "testdir/dest2/inner/k.txt"
# root:
#   root:
#     644:
#       backup/fstab: /etc/fstab
```

> [!NOTE]
> `copicat` will never create parent directories. If a destination's parent directory is missing, it will print an error.

### Copy `in` mode

```
usage: copicat in [-h] [-D] [config] [owner] [group] [mode]

positional arguments:
  config         Path to YAML config file. Default is "copicat.yml"
  owner          Username or UID of the owner of the files
  group          Group name or GID of the group of the files
  mode           Mode of the crated files in the same format as the config file

options:
  -h, --help     show this help message and exit
  -D, --dry-run  Print the operation without performing any action
```

The `in` subcommand is the simplest mode of operation, and the opposite of the `out` subcommand, it's meant as "copying from source locations ***in***to the storage location".
The command takes in input the the owner, group, and mode (in the same format as the config file).
This will copy all files from their source location to the target location, using the user, group, and mode received from cli, ignoring those specified in the config file.

### Copy `out` mode

```
usage: copicat out [-h] [-D] [config]

positional arguments:
  config         Path to YAML config file. Default is "copicat.yml"

options:
  -h, --help     show this help message and exit
  -D, --dry-run  Print the operation without performing any action
```

The `out` subcommand is the opposite of the `in` subcommand, it's meant as "copying files ***out*** of the storage and back to their source location".
This subcommand takes nothing in input, because all the information about owner, group and mode are already in the configuration file.

Remember that you might need root access to change ownership and permissions of files.

### Copy `type` mode

```
usage: copicat type [-h] [-k] [-H] [-T] [-D] source dest [mime]

positional arguments:
  source                Source directory or file
  dest                  Destination directory
  mime                  Half or full of mime type to copy
                        (i.e.: both "video" and "video/x-matroska" will match a file with mimetype
                        "video/x-matroska"). Default is "video"

options:
  -h, --help            show this help message and exit
  -k, --keep-structure  Keep the directory structure in the destination.
                        Without this, only the files from the first level will be copied
  -H, --hard-link       Hard-link files into destination instead of copying
  -T, --dry-types       Just print the types of all candidate source files.
                        Different implementations might identify types differently
  -D, --dry-run         Print the operation without performing any action
```

`type` mode copies based on the files mime types instead of using a config file. This mode doesn't manage owners and permission. It's mostly intended to easily move media files around (e.g.: copy all the videos from `/removable-media/movie-folder` to `/jellyfin/movies` keeping the directory structure).
The command takes in input the source and destination, and a mimetype ("video" by default). The specified type can be either the first half (e.g.: "text" to match all text format) or the full type (e.g.: "text/markdown" to only match markdown files).

> [!TIP]
> You can use the `--dry-types` option to check the types detected by the tool before trying to copy. Different mimetype guessing libraries might detect less specific or even different types for the same file.

Using the `--hard-link` option will hardlink files instead of copying them. This might require being the owner of the file or setting `fs.protected_hardlinks=0` with `sysctl`. This requires that target and source reside on the same storage device. Remember that hardlinked file share the same permissions (which is why they cannot be used with `in` and `out`).

By default, the tool doesn't check the folder recursively, but only checks the files in the first level and copies them directly inside the destination (without creating a top-level parent directory). You can change this behaviour with the `--keep-structure` switch. This will enter inside the folder recursively, an create parent folders as needed to create the same structure inside dest, this includes creating a top-level parent directory. None of this preserves permissions, directory and files will be created following the OS's default.