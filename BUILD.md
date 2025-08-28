# Developer Setup

**Requirements**: Python 3, Node.js (any LTS release), Docker, and a [setlist.fm API key](https://api.setlist.fm/docs/1.0/index.html)

## Backend setup

1. `cd server`
1. Create and activate a virtual environment [using the Flask docs](https://flask.palletsprojects.com/en/3.0.x/installation/#virtual-environments)
1. Install required packages: `pip install -r requirements.txt`
1. Copy `.env.example` to a new file `.env`
1. In `.env`, fill in your setlist.fm API key
1. *(optional)* To show artist images, [create a new app](https://developer.spotify.com/documentation/web-api/concepts/apps) on Spotify for Developers and add the credentials to `.env`: the Client ID and the Client Secret. If not added, artists will display with a default profile picture.
1. Start the Docker container: `docker compose up -d` -- this will be a locally hosted instance of MongoDB.
1. Run the app: `flask run`

The backend API will run at `http://localhost:8000`.

To shut down the Docker container, run `docker compose down`.

### Backend Tests

The app has tests for the backend, though not for the frontend. To run all tests, use `python test.py`. This will also generate a coverage report in text and HTML.

Some tests run slowly by design because the implementation uses timers (for example, to wait and retry requests to an external API). To run only the tests that don't have timeouts, use `pytest -m "not timer"`.

## Frontend setup

1. `cd client`
1. `yarn install`
1. Run the development server with `yarn run dev`
1. *(optional)* To build the frontend for production, use `yarn run build` to transpile & bundle the code into `dist/`. Then use `yarn run preview` to test that production build locally.

(The dev server will not check TypeScript, but the build script will.)

## Additional steps for production

These notes are mostly for myself.

### Setting up the backend with Apache as a reverse proxy

(nginx can also be used; I just decided to try out Apache)

1. The Flask app needs to be run within some process control system, so it can run in the background and auto-restart if necessary. One way to do this is to run the app with Gunicorn and control the process with [Supervisor](http://supervisord.org/). Aside from the default config, this is all that needs to be added to `server/supervisord.conf`:

    ```conf
    [program:cm]
    command=gunicorn app:create_app()
    autorestart=true
    ```
1. Start the app with `supervisorctl start cm`.
1. Now we must set up a Virtual Host with Apache to serve the production domain name. Create a new config file under `/etc/apache2/sites-available`, named `<domain_name>.conf`.
1. Use this config to beam any requests for `/api/*` to the Flask app. This example uses the domain `concertmapper.eastus2.cloudapp.azure.com`.

    ```conf
    <VirtualHost *:443>
      ServerName concertmapper.eastus2.cloudapp.azure.com
      ServerAlias www.concertmapper.eastus2.cloudapp.azure.com

      # Backend
      ProxyPass /api http://127.0.0.1:8000/api
      ProxyPassReverse /api http://127.0.0.1:8000/api
    </VirtualHost>
    ```
    If you don't have an SSL certificate, use `<VirtualHost *:80>` to serve the site over HTTP. If you do, a tool like `certbot` should help in adding the proper lines to the config. (Make sure `certbot` doesn't create a *new* config file)
1. Enable the new virtual host: `sudo a2ensite <domain_name>.conf`
1. Validate the config with `sudo apache2ctl configtest`
1. Restart Apache to apply the changes: `sudo systemctl restart apache2`

Now the backend API should be up. Test it out with something simple (like `curl <domain_name>/api/artists/foo`)

### Setting up the client assets to be also served by Apache

1. In `/client`, copy `.env.example` to a new file `.env` and fill in the URL for the backend API and websocket.
    - The .env file I use for production:
    ```
    VITE_API_BASE_URL_PROD=https://concertmapper.eastus2.cloudapp.azure.com
    VITE_WEBSOCKET_BASE_URL_PROD=wss://concertmapper.eastus2.cloudapp.azure.com
    ```
1. Use `yarn run build` to produce a copy of the assets in `dist/`. (NOTE: If this command hangs forever, it's because the TypeScript compiler ate up all the system memory, and the output won't tell you this because it runs in parallel with `vite build`. [Adding swap space](https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-20-04) can fix this)
1. Add the following to our Apache virtual host config from earlier. The trailing slashes of file paths must appear (or not appear) exactly as shown, or it breaks.
    ```conf
    # Frontend
    Alias / /PATH-TO-DIST-DIR/

    <Directory /PATH-TO-DIST-DIR>
        Require all granted

        # Direct all sub paths to index.html so they get handled by Vue
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    # WebSocket...
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} =websocket
    RewriteRule /(.*) ws://127.0.0.1:5001/$1 [P,QSA,L]
    ```
1. Validate config again: `sudo apache2ctl configtest`
1. Restart Apache again: `sudo systemctl restart apache2`

Now Apache should be set up to serve both the backend API and the frontend's assets at the same domain name.

Here is the final config for production:

```conf
<VirtualHost *:80>
  ServerName concertmapper.eastus2.cloudapp.azure.com
  ServerAlias www.concertmapper.eastus2.cloudapp.azure.com

  # Redirect to HTTPS
  RewriteEngine on
  RewriteCond %{SERVER_NAME} =www.concertmapper.eastus2.cloudapp.azure.com [OR]
  RewriteCond %{SERVER_NAME} =concertmapper.eastus2.cloudapp.azure.com
  RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>

<VirtualHost *:443>
  ServerName concertmapper.eastus2.cloudapp.azure.com
  ServerAlias www.concertmapper.eastus2.cloudapp.azure.com

  ErrorLog ${APACHE_LOG_DIR}/error.log
  CustomLog ${APACHE_LOG_DIR}/access.log combined

  # Backend
  ProxyPass /api http://127.0.0.1:8000/api
  ProxyPassReverse /api http://127.0.0.1:8000/api

  # Frontend
  Alias / /home/kite/cm/client/dist/

  <Directory /home/kite/cm/client/dist>
    Require all granted

    # Direct all sub paths to index.html so they get handled by Vue
    RewriteEngine On
    RewriteBase /
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /index.html [L]
  </Directory>

  # SSL put by certbot
  SSLCertificateFile /etc/letsencrypt/live/concertmapper.eastus2.cloudapp.azure.com/fullchain.pem
  SSLCertificateKeyFile /etc/letsencrypt/live/concertmapper.eastus2.cloudapp.azure.com/privkey.pem
  Include /etc/letsencrypt/options-ssl-apache.conf

  # WebSocket...
  RewriteEngine On
  RewriteCond %{HTTP:Upgrade} =websocket
  RewriteRule /(.*) ws://127.0.0.1:5001/$1 [P,QSA,L]
</VirtualHost>
```
