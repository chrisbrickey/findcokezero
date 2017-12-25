# API Endpoints

## HTML API

### Root

- `GET /` - serves HTML template  



## JSON API
*Don't forget closing slash unless url includes a query string*

### Retailers

|Endpoint                                         | Description                                   | Example
|-------------------------------------------------|-----------------------------------------------|------------
| GET /api/retailers/                             | retrieve all retailers                        | www.findcokezero.com/api/retailers/
| GET /api/retailers/:retailer_id/                | retrieve specific retailer                    | www.findcokezero.com/api/retailers/1/
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
| GET /api/sodas/:soda_id/            | retrieve specific soda                    | www.findcokezero.com/api/sodas/1
| GET /api/sodas/:soda_id/retailers/  | retrieve all sodas at a specific retailer | www.findcokezero.com/api/sodas/2/retailers/
| POST /api/sodas/                    | create soda                               |
| PATCH /api/sodas/:soda_id/          | edit soda                                 |
| DELETE /api/sodas/:soda_id/         | remove soda                               |
