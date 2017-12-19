# FindCokeZero
Mobile-first web app that provides locations of stores filtered by CokeZero flavors and user location. Django REST framework enables browsable API and administrative management. Integration with Google Maps API supports mapping.

## A very serious mission
I'm building this app because I love CherryCokeZero, but it's not omni-present and retailer inventories of all Coke flavors fluctuate.
When I find myself in a new location, I have to scout out the stores that carry it regularly.  Surely, I'm not the only one!
This app keeps track of my store inventory and uses crowd-sourcing to grow the database.

## Run the Program
- Open virtual environment: `. venv/bin/activate`

- Install dependencies: `pip install -r requirements.txt`

- Migrate the database: `./manage.py makemigrations` then `./manage.py migrate`

- Load data from seed: `./manage.py loaddata initdata.json`

- Run development server locally: `./manage.py runserver`

- If static files are not running locally: `./manage.py collectstatic`

- Run tests: `./manage.py test app1_findcokezero`


## API Endpoints

#### HTML ROOT
*All urls that omit closing slash will redirect to root and return html, unless url includes a query string*

- `GET /` - serves HTML template  


#### JSON API
*Don't forget closing slash unless url includes a query string*

##### Retailers

- `GET /api/retailers/` - retrieve all retailers
- `GET /api/retailers/:retailer_id/sodas/` - retrieve all retailers with specific soda
- `GET /api/retailers/?postcode=post_code` - retrieve all retailers with specific postcode
- `POST /api/retailers/` - create retailer


##### Sodas

- `GET /api/sodas/` - retrieve all sodas
- `GET /api/sodas/:soda_id/` - retrieve specific soda
- `GET /api/sodas/:soda_id/retailers/` - retrieve all sodas at specific retailer




## Major Dependencies
*see requirements.txt and requirements-dev.txt for full list*
- python 2.7.10
- pip 9.0.1
- virualenv 15.1.0
- Django-1.11.4
- pytz-2017.2


## Wireframes

#### Mobile Sample
![Mobile](https://res.cloudinary.com/dckkkjkuz/image/upload/v1509942572/findcokezero/Mobile2.png)


#### Web Sample
![Web](https://res.cloudinary.com/dckkkjkuz/image/upload/v1509942572/findcokezero/Web1.png)



See all [development documents][docs]

[docs]: docs/


## Future Development
- See [development documents][docs] for future API endpoints
- Integrate Google Maps API to augment retailer objects with latitude / longitude and facilitate maps on frontend
- Build client that shows map of retailers based on some geographic input (e.g. current user location or manually entered zip code)

[docs]: docs/
