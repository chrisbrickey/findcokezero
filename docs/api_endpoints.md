# API Endpoints

## HTML API

### Root
*All urls that omit closing slash will redirect to root and return html, unless url includes a query string*

- `GET /` - serves HTML template  



## JSON API
*Don't forget closing slash unless url includes a query string*

### Retailers

- `GET /api/retailers/` - retrieve all retailers
- `GET /api/retailers/:retailer_id/` - retrieve specific retailer
- `GET /api/retailers/:retailer_id/sodas/` - retrieve all retailers with specific soda
- `GET /api/retailers/?postcode=post_code` - retrieve all retailers with specific postcode
- `POST /api/retailers/` - create retailer
- `PATCH /api/retailers/:retailer_id/` - edit retailer
- `DELETE /api/retailers/:retailer_id/` - remove retailer


### Sodas

- `GET /api/sodas/` - retrieve all sodas
- `GET /api/sodas/:soda_id/` - retrieve specific soda
- `GET /api/sodas/:soda_id/retailers/` - retrieve all sodas at specific retailer
- `POST /api/sodas/` - create soda
- `PATCH /api/sodas/:soda_id/` - edit soda
- `DELETE /api/sodas/:soda_id/` - remove soda
