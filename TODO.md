# TODO

After live:
 1. complete initial layout
   * colour tweak - make it look less bootstrap

Bug:
 - deploy (or content refresh) should symlink media directory
 - node/[id] urls should look at blog and page entries


Before Open Sourcing:
 - key goal: remove security risks and performance risks
 - key goal: clear copyright and licensing
 1. parsing needs to be triggered from the CLI (prevent DoS)
   * bin folder for host level things like hg pull, symlinking and apache restart

steps:
1. hg pull the source data
2. compile into a 'new' location (e.g. timestamp)
3. swap symlinks


 Python 3 and Dependency Refresh
   * bottle - YES # old
   * python-dateutil - YES
   * Markdown - YES # old
   * Jinja2 - YES
   * CherryPy - YES
   * dictshield - ?? # old
   * python-memcached - UNKNOWN (python3-memcached is)
