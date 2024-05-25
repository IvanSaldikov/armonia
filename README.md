# AI Assistant Communication Framework
*_**by Ivan Saldikov**_*

**Social**: https://www.linkedin.com/in/ivansaldikov/

**Email**: i at armonia.day

*Tech Stack*:
- `Docker` (everything is packed here)
- `Django`
- `Postgres`
- `Redis`
- `RabbitMQ`
- `Celery`
 
Supported Anthropic API, but also can be used OpenAI and TogetherAI APIs. 

This framework can be used for developing different AI Assistants in the Web.

This framework is used by such projects:
- Armonia.day [https://armonia.day](https://armonia.day)
- MyAIGf.online [https://myaigf.online](https://myaigf.online)
- StDiff.io [https://stdiff.io](https://stdiff.io)


# Armonia.day

Source code of AI Theraphist Project: https://armonia.day.

## HOW TO BUILD

### Build and run the whole stack locally

Ensure you have `docker-compose` at least of version 2.*.

1. Copy `.env` to `.env.local` and modify it according to your needs.


2. Run the command

```
make b
```

3. If you're doing this first time please run these commands:

```
make migs
make mig
make csup
```

Once all this is done, you can navigate to `http://localhost:8007/api/ping` to see is everything working.

### Development in IDE

1. `pip install -r app/requirements.txt`
2. Django Root is the `app` folder. `settings.py` is in `config` folder.

### Admin Panel

Go to http://localhost:8007/admin/ and enter your superuser credentials to enter to the Admin panel.

`docker-compose down`

**Run production environment**

`make b`

`make mig`

`make coll`

**Check for errors in the logs**

`docker-compose logs -f [CONTAINERNAME]`

You can also filter log to get specific celery task logs.

`docker-compose logs -f worker | sed -n '<SEACH_STRING>'`


## Install pre-commit

We use some pre-commit hooks to ensure that:

- Each new commit respect the recommended coding style conventions [(PEP-8)](https://peps.python.org/pep-0008/).
- We have a more harmonious code.
- No discussion between developers, we all agree to follow Black, isort & flake8 instructions.
- More time to focus on the functionalities rather than the coding style.

*How to install it?*

```
pip install pre-commit
pre-commit install
```

[Further details about installation here](https://pre-commit.com/#install)

You might also need to install *packer*

```
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install packer
```

Then initialize packer

```packer init provisioning/packer/source.pkr.hcl```

And also install ansible

```sudo apt install ansible```

## Enable app at server startup

1. `sudo nano /etc/systemd/system/armonia.service`
2. Copy this block of code:

```
[Unit]
Description=Start docker app

[Service]
ExecStart=/bin/bash -c 'cd /home/ubuntu/armonia; docker-compose -f docker-compose.server.yml up -d --build;'

[Install]
WantedBy=multi-user.target
```

3. `sudo systemctl daemon-reload`
4. `sudo systemctl enable armonia.service`

## Test Django channel layer can communicate with Redis

```
$ python3 manage.py shell
>>> import channels.layers
>>> channel_layer = channels.layers.get_channel_layer()
>>> from asgiref.sync import async_to_sync
>>> async_to_sync(channel_layer.send)('test_channel', {'type': 'hello'})
>>> async_to_sync(channel_layer.receive)('test_channel')
{'type': 'hello'}
```

## Connecting to database

To connect to database on the prod you need to use SSH tunnel.

## Code style checking

To check code style in the Python files of the project before a Pull Request use the command:

```
make lint
```

which is equivalent of the command (see the `Makefile` in the root directory):

```
flake8 --ignore=E501,F401,E402 --exclude=node_modules app
```

Before using this you need to install flake8 in your Terminal by:

```
pip install flake8
```

To use `make` command in Microsoft Windows OS install it by:

```
choco install make
```

## CI/CD - Gitlab

### Gitlab CI Local

After changing of .gitlab-ci.yml you can use CI Lint at Gitlab Pipelines section to verify that the file works fine.


## Collect static to S3

TODO:
https://tartarus.org/james/diary/2013/07/18/fun-with-django-storage-backends

Make collect static not to the server, but to the S3 storage.

## If Available Disk Space is out (Google Cloud)

1. Just got to Google Console and increase the disk size:
2. SSH to VM and use this commands to tell Linux to update the volume size:
   https://cloud.google.com/compute/docs/disks/resize-persistent-disk
   `sudo resize2fs /dev/nvme0n1`

## Deploy to Prod

1. Install Docker.
2. Create new user `devops_user`: https://linuxhint.com/addinng_new_user_debian/
3. Allow `devops_user` user to run docker
   without `sudo`: https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
4. Copy SSH keys to `/home/devops_user/.ssh`: https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-debian-11
5. To Generate Certificates - see section below (certbot).
6. Copy `default.conf` from `servers/main/nginx` folder to `/opt/armonia/nginx/` folder on remote machine.
7. Create `docker-comose.prod.yml` in `/opt/armonia` folder.
8. Create `/mnt/media` and `/mnt/static` folder for media and static files and make devops_user the owner of it:
   ```bash
   mkdir /mnt/media
   mkdir /mnt/static
   chown 911:911 /mnt/media
   chown 911:911 /mnt/static
   ```
   `911` is a UID of app user in the app docker containers.
10. Use Gitlab CI/CD to build and deploy the app.

## Limiting user connection speed and number of connections (NGINX optimizations)

To optimize it we can use these settings:
https://docs.nginx.com/nginx/admin-guide/security-controls/controlling-access-proxied-tcp/

## 3rd Parties Libraries

### Box Icons

Box-Icons for showing "G" icon when Google Auth is used: https://boxicons.com/?query=home

## Cleaning disk

Remove all unused Docker things (safe to execute):

`docker system prune -a`

Then we need manually run the command `docker compose up -d --build` and
run migrations (with the help of Gitlab is okay).

# Country related content

We need to show user country related content to provide good service. It's always better to communicate with your own culture
instead of anything else.

To achieve that we use the middleware from countries app. We can use API to get IP2Country or a database file with
the list of correspond countries from ips.

Local database file:

1. Download: https://ipinfo.io/account/data-downloads
2. Use: https://dev.maxmind.com/geoip/geolocate-an-ip/databases?lang=en

API:

1. https://github.com/ipinfo/python
2. or this one (less paid per month, but no free plans): https://dev.maxmind.com/geoip/geolocate-an-ip

# Certbot

Ref:
https://mindsers.blog/en/post/https-using-nginx-certbot-docker/

Renew:
`docker compose run --rm certbot renew`

1. Dry run (when no certificates) - comment them in nginx.conf:
   `docker compose --profile=certbot run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d armonia.day`
2. Real Run - still need to be commented in nginx.conf (see nginx.conf.init):
   `docker compose --profile=certbot run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ -d armonia.day`
3. Run the renew command sometimes:
   `docker compose --profile=certbot run --rm certbot renew`

# Analyze disk space via command line

https://superuser.com/questions/300606/how-to-analyse-disk-usage-in-command-line-linux

`ncdu -q .`


# Additional recommendations for an AI Therapist

Intro:

```
### System Prompt
You are a psychologist who helps the user with their issues.

Your task, using different approaches from psycology, conduct therapy with the user so that he feels better.

First of all you need to understand user issue, try to figure out what you need to solve the problem, plan the therapy and conduct it step by step after user's replies.
```

## How to create Websockets app with HTMX and Django Channels

https://www.meetgor.com/django-htmx-chat-app/

## Sounds library

Like we use in chats incoming messages.

https://pixabay.com/sound-effects/search/sound/


## Swap Files on Digital Ocean Droplets/VMs

https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-22-04