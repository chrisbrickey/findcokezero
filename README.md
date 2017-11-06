## FindCokeZero
Mobile-first web app that provides locations of stores filtered by CokeZero flavors and user location. Django REST framework enables browsable API and administrative management. Integration with Google Maps API supports mapping. 

### A very serious mission
I'm building this app because I love CherryCokeZero, but it's not omni-present and retailer inventories of all Coke flavors fluxuate. 
When I find myself in a new location, I have to scout out the stores that carry it regularly.  Surely, I'm not the only one! 
This app keeps track of my store inventory and uses crowd-sourcing to grow the database. 

### Run the Program
- Open virtual environment: `. venv/bin/activate`

- Install dependencies: `pip install -r requirements.txt`

- Migrate the database: `./manage.py makemigrations` then `./manage.py migrate`

- Load data from seed: `./manage.py loaddata initdata.json`

- Run development server locally: `./manage.py runserver`

- If static files are not running locally: `./manage.py collectstatic`

- Run tests: `./manage.py test app1_findcokezero`

### Major Dependencies
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


### Future Development
- Integrate Google Maps API to augment retailer objects with latitude / longitude and facilitate maps on frontend
- Build client that shows map of retailers based on some geographic input (e.g. current user location or manually entered zip code)
- Frontend users can add retailers
- Frontend users can update soda inventory of retailers

