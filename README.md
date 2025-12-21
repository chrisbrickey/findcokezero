# FindCokeZero
Test-driven Django REST Framework API that maps convenience stores and filters by flavors of CokeZero™ 
- Integration with Google Maps supports geo-location. 
- Django REST framework enables browsable API and administrative management. 
- Landing page with API documentation: www.findcokezero.com 
- Browsable API: www.findcokezero.com/api/ 

## Background
This app tracks CokeZero™ flavor inventories by store and uses crowd-sourcing to grow the database in hopes of always knowing where to reliably find CherryCokeZero™.
Why? I built this app during a time when I drank a LOT of CherryCokeZero™. 
I was living in San Francisco, where the inventory of CokeZero™ flavors fluctuated dramatically between stores. 
Surely, I was not the only person frustrated by this. So I built this app primarily to learn about the Django framework
and secondarily to more reliably find the original formula of CherryCokeZero™ in local stores.

## Tech Stack
*see requirements.txt and requirements-dev.txt for full list*

- uv (package management)
- Python 3.12.1 
- Django 4.2.8 LTS 
- Django REST Framework 3.14.0
- PostgreSQL 
- psycopg2-binary (python driver/adaptor for postreSQL)
- WhiteNoise 6.6.0 (static file serving)
- Gunicorn 21.2.0 (production server)

## Setup

### Environment Variables
This application uses environment variables for configuration via `.env` file (local) or hosting platform config (production).

- `GOOGLEMAPS_KEY`: Google Maps API key for geolocation (required)
- `DEBUG`: Set to `False` in production (defaults to `True` for local development)
- `SECRET_KEY`: Django secret key for cryptographic signing (optional for local development, required for production)
- `DATABASE_URL`: PostgreSQL database connection string (optional, auto-configured for local development)
- `DB_USER`: PostgreSQL username (optional, defaults to empty string for local development)

For local development, default values are provided with the exception of `GOOGLEMAPS_KEY` (instructions below).
In production, `GOOGLEMAPS_KEY`, `DEBUG=False`, and `SECRET_KEY` must be explicitly set. Heroku automatically sets `DATABASE_URL`.

#### Option A: Set environment variables in .env file

1. Configure `.env` file.
- Create a file called `.env` at the top level of the repo. This file is gitignored to prevent committing secrets.
- Copy the content of `.env.example` (committed in this repo) into your new file.

2. Set `GOOGLEMAPS_KEY`.
- Get a free API key [here](https://developers.google.com/maps/documentation/geocoding/get-api-key).
- Replace `your-google-maps-api-key-here` in `.env` with the actual API key.

_To run the app locally, the above are the only required steps with regard to environment variables._

3. (optional) Set `SECRET_KEY`.
- Some value must be defined for this variable in order for Django to start. 
- This variable is optional for local development because a real cryptographic key is not necessary for handling test/seed data on a local server. 
- The `settings.py` file includes fallback logic which preconfigures this variable for you by defaulting to an obviously insecure string: `django-insecure-dev-key-only-for-local-development-do-not-use-in-production`.
- If you want to use a real cryptographic key for local development, generate a secret key (using below commands) and paste it in `.env`.
     ```
     python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
     ```
- Never use the insecure default string in production.

4. (optional) Set `DATABASE_URL`.
- The `settings.py` file includes a default PostgreSQL configuration for local development.
- If `DATABASE_URL` is explicitly set, it will override that default.
- This environment variable is automatically set by Heroku in production.

5. (optional) Set `DB_USER`.
- PostgreSQL username for database connection.
- Defaults to empty string, which works for most local PostgreSQL installations.
- Only needed if your local PostgreSQL requires authentication.

6. (optional) Set `DEBUG`.
- Defaults to `True` for local development.
- **Must be set to `False` in production** for security.
- Example: `DEBUG=False` in production `.env` or hosting platform configuration.

#### Option B: Store environment variables in terminal shell
```
export GOOGLEMAPS_KEY="your-api-key-here" # required for local development
export SECRET_KEY="your-secret-key-here" # optional for local development
```
_NB: These terminal exports are temporary and only persist for the current terminal session._

### Development Environment

1. Install uv package manager
   [uv](https://docs.astral.sh/uv/)
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create virtual environment
   ```
   uv venv .venv
   ```

3. Install dependencies
   ```
   # to install only core dependencies sufficient for running the app locally
   uv pip install -r requirements.txt

   # to install core dependencies plus additional tools for testing, debugging, and development work
   uv pip install -r requirements.txt -r requirements-dev.txt
   ```

4. Activate the virtual environment
   ```
   source .venv/bin/activate
   ```
   
### Database

1. Install PostgreSQL
   ```
   brew install postgresql@14
   ```
   _Note: PostgreSQL 14 or later should work. Version 14 is specified for consistency._

2. Start PostgreSQL service
   ```
   brew services start postgresql@14

   # alternative: start the service temporarily (stops when terminal closes)
   pg_ctl -D /opt/homebrew/var/postgresql@14 start
   ```

3. Create local PostgreSQL database
   ```
   createdb findcoke_dev1
   
   # verify database was created
   psql -l | grep findcoke_dev1
   ```

4. Migrate the database
   ```
   ./manage.py makemigrations
   ./manage.py migrate
   ```

5. Load seed data 

   ```
   ./manage.py loaddata initdata.json
   
   # alternatively with uv
    uv run ./manage.py loaddata initdata.json
   ```
   
   Seed data is located in `app1_findcokezero/fixtures/initdata.json` and includes:
   - 6 Soda types: CherryCokeZero™ (CH), CokeZero™ (CZ), DietCoke™ (DC), VanillaCokeZero™ (VN), OrangeVanillaCokeZero™ (OV), Unspecified (UN)
   - 6 Retailers: San Francisco stores with geographic coordinates and soda inventory

## Run the Program

1. Start development server
   ```
    ./manage.py runserver
   
   # alternatively with uv
   uv run ./manage.py runserver
   ```

2. View in browser
- Landing page with API documentation: http://127.0.0.1:8000/
- Browsable API:  http://127.0.0.1:8000/api/

## Local Development

### Run tests
   ```
   ./manage.py test app1_findcokezero
   
   # alternatively with uv
   uv run ./manage.py test app1_findcokezero
   ```
_Django automatically creates and destroys a test database when running tests. The test database is named `test_findcoke_dev1` and is isolated from your development data._

### Working with static files
   **If static files are not running locally:**
   ```
   ./manage.py collectstatic
   ```

### Common Database Operations

   **Create new migrations after model changes**
   ```
   ./manage.py makemigrations
   ```

   **Apply migrations**
   ```
   ./manage.py migrate
   ```

   **Load seed data**
   ```
   ./manage.py loaddata initdata.json
   ```

   **Flush database (clear all data, keep schema)**
   ```
   ./manage.py flush
   ```

   **Drop, recreate, and reseed database**
   ```
   dropdb findcoke_dev1
   createdb findcoke_dev1
   ./manage.py migrate
   ./manage.py loaddata initdata.json
   ```

## API Endpoints

#### LANDING PAGE

- `GET /` - serves HTML template at www.findcokezero.com

#### JSON API
*Don't forget closing slash unless url includes a query string*

### Retailers

|Endpoint                                         | Description                                   | Example
|-------------------------------------------------|-----------------------------------------------|------------
| GET /api/retailers/                             | retrieve all retailers                        | www.findcokezero.com/api/retailers/
| GET /api/retailers/:retailer_id/                | retrieve specific retailer                    |
| GET /api/retailers/:retailer_id/sodas/          | retrieve all retailers with specific soda     | www.findcokezero.com/api/retailers/2/sodas/
| GET /api/retailers/?postcode=:retailer_postcode | retrieve all retailers with specific postcode | www.findcokezero.com/api/retailers/?postcode=11111
| GET /api/retailers/?postcode=:retailer_postcode&sodas=:soda_abbreviations | retrieve all retailers with specific postcode and selection of soda types | www.findcokezero.com/api/retailers/?postcode=94108&sodas=CH,CZ
| POST /api/retailers                             | create retailer                               |
| PATCH /api/retailers/:retailer_id/              | edit retailer                                 |
| DELETE /api/retailers/:retailer_id/             | remove retailer                               |


### Sodas

|Endpoint                             | Description                               | Example
|-------------------------------------|-------------------------------------------|------------
| GET /api/sodas/                     | retrieve all sodas                        | www.findcokezero.com/api/sodas
| GET /api/sodas/:soda_id/            | retrieve specific soda                    |
| GET /api/sodas/:soda_id/retailers/  | retrieve all sodas at a specific retailer | www.findcokezero.com/api/sodas/2/retailers/
| POST /api/sodas/                    | create soda                               |
| PATCH /api/sodas/:soda_id/          | edit soda                                 |
| DELETE /api/sodas/:soda_id/         | remove soda                               |

## Future Development
Build client that shows map of retailers based on some geographic input (e.g., current user location or manually entered zip code)

### Wireframes
- [development docs](./docs/)
- [mobile sample](https://res.cloudinary.com/dckkkjkuz/image/upload/v1513744099/findcokezero/Mobile2.png)
- [web sample](https://res.cloudinary.com/dckkkjkuz/image/upload/v1513744057/findcokezero/Web1.png)