## FindCokeZero
iOS mobile app that provides locations of CokeZero retailers based on user input. Django REST framework enables browsable API and administrative management. Link to Google Maps API provides visual map of retailers carrying the multiple flavors of CokeZero.

### A very serious mission
I'm building this app because I love CherryCokeZero, but it's not omni-present. When I find myself in a new location, I have to scout out the stores that carry it. Surely, I'm not the only one! This app will keep track of those retailers and capture the knowledge of other CherryCokeZero consumers. This is an especially serious concern now that the Coca-Cola Company has announced the discontinuation of CokeZero.  

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
- Add model for soda types and link to retailers with join table  
- Incorporate Google Maps API to augment retailer objects with latitude / longitude
- Build client that shows map of retailers based on some geographic input (e.g. current user location or manually entered zip code)
- Allow users to filter retailers by soda type
- Allow users to add new retailers (including soda types) to database using form and/or click on map
