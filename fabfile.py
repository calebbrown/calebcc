import os
import datetime

from fabric.api import put, task, local, run, cd, env

if 'CALEBCC_DEPLOY_HOST' in os.environ:
    env.hosts = [os.environ['CALEBCC_DEPLOY_HOST']]
if 'CALEBBC_SSH_KEY_FILE' in os.environ:
    env.key_filename = os.environ['CALEBBC_SSH_KEY_FILE']

remote_dir = '~/webapps/calebcc_bottle'
remote_static_dir = '~/webapps/calebcc_static'
repo_url = 'ssh://hg@bitbucket.org/calebbrown/calebcc_site'


@task
def init_env():
    with cd(remote_dir):
        run('mkdir cache')
        run('mkdir versions')
        run('hg clone %s cache/calebcc_site' % repo_url)


@task
def update_cache():
    with cd(os.path.join(remote_dir, 'cache/calebcc_site')):
        run('hg pull -u')


@task
def prepare(version=None, version_timestamp=None):
    update_cache()

    if not version_timestamp:
        version_timestamp = datetime.datetime.now().strftime('%s')

    # copy the source code
    with cd(os.path.join(remote_dir, 'versions')):
        run('hg clone %s %s' % (os.path.join(remote_dir, 'cache/calebcc_site'), version_timestamp))

    # create the version file
    version_tmp_file = '/tmp/version.%s.py' % version_timestamp
    fd = open(version_tmp_file, 'w+')
    fd.write('DEPLOY_VERSION = "%s"\n' % version_timestamp)
    fd.close()

    put(version_tmp_file, os.path.join(remote_dir, 'versions', version_timestamp, 'main', 'version.py'))
    local('rm %s' % version_tmp_file)

    with cd(os.path.join(remote_dir, 'versions', version_timestamp)):
        run('virtualenv --python=python2.7 --distribute --no-site-packages env')
        run('pip install -E env -r requirements.txt')
        run('env/bin/python -m compileall -q .')

    run('ln -sfn %s %s' % (os.path.join(remote_dir, 'versions', version_timestamp, 'static'), os.path.join(remote_static_dir, version_timestamp)))
    run('ln -sfn %s %s' % (os.path.join(remote_dir, 'site_data/media'), os.path.join(remote_static_dir, 'media')))


@task
def apache_restart():
    with cd(os.path.join(remote_dir)):
        run('apache2/bin/restart')


@task
def clean_old_releases():
    with cd(os.path.join(remote_dir, 'versions')):
        run('ls -1td * | tail -n +6 | xargs rm -r')

    with cd(os.path.join(remote_static_dir)):
        run('ls -1td * | tail -n +6 | xargs rm -r')


@task
def deploy(version=None):
    version_timestamp = datetime.datetime.now().strftime('%s')

    prepare(version_timestamp=version_timestamp)

    # move the symlink
    with cd(os.path.join(remote_dir)):
        run('ln -sfn %s project' % os.path.join(remote_dir, 'versions', version_timestamp))

    apache_restart()
    clean_old_releases()
