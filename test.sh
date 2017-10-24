#!/usr/bin/env python

asdf = 1+3
print "%d", asdf

# echo "fuzzy"
#
# ## POST to retailers/ with name="My Special Store"
# ## GET to retailers/ with name="My Special Store"
#
#
# curl 'http://localhost:8000/retailers/' \
#   -H 'Cookie: csrftoken=pSwozdb6EOg99b1hT6fy7ZswiZrByyzvM32PlfxQrixAdexiErLsrrPJkGp8GHZo; tabstyle=raw-tab' \
#   -H 'Origin: http://localhost:8000' \
#   -H 'Accept-Encoding: gzip, deflate, br' \
#   -H 'Accept-Language: en-US,en;q=0.8' \
#   -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36' \
#   -H 'Content-Type: application/json' \
#   -H 'Accept: application/json; q=1.0, */*' \
#   -H 'Referer: http://localhost:8000/retailers/' \
#   -H 'X-CSRFTOKEN: pSwozdb6EOg99b1hT6fy7ZswiZrByyzvM32PlfxQrixAdexiErLsrrPJkGp8GHZo' \
#   -H 'X-Requested-With: XMLHttpRequest' \
#   -H 'Connection: keep-alive' \
#   --data-binary $'{"city": "SF", "name": "McJSONs Store", "country": "", "longtitude": null, "postcode": null,  "latitude": null, "street_address": "Bush St"}' \
#   --compressed
