import requests
from bs4 import BeautifulSoup

URL = "https://restaurants.subway.com"

OUTPUT_FILE = "subway_locations.csv"

result_file = open(OUTPUT_FILE, "w")

class SubwayLocation:
  def __init__(self, name, url, longitude, latitude, address1, address2, city, state, zipcode, country, phone):
    self.name = name
    self.url = url
    self.longitude = longitude
    self.latitude = latitude
    self.address1 = address1
    self.address2 = address2
    self.city = city
    self.state = state
    self.zipcode = zipcode
    self.country = country
    self.phone = phone
  
  def output(self):
    return "\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"".format(self.name, self.url, self.longitude, self.latitude, self.address1, self.address2, self.city, self.state, self.zipcode, self.country, self.phone)

  def names():
    return "\"name\",\"url\",\"longitude\",\"latitude\",\"address1\",\"address2\",\"city\",\"state\",\"zipcode\",\"country\",\"phone\""

def get_from_selector(soup, selector):
  result = soup.select(selector)
  if len(result) == 0:
    return None
  else:
    return result[0]

def parse_location(soup, url):
  found_name = get_from_selector(soup, ".Heading--lead.Hero-heading")
  latitude = get_from_selector(soup, ".Core .coordinates meta[itemprop=latitude]")["content"]
  longitude = get_from_selector(soup, ".Core .coordinates meta[itemprop=longitude]")["content"]
  address1elem = get_from_selector(soup, ".Core .c-address-street-1")
  address1 = "" if address1elem is None else address1elem.text
  address2elem = get_from_selector(soup, ".Core .c-address-street-2")
  address2 = "" if address2elem is None else address2elem.text
  cityelem = get_from_selector(soup, ".Core .c-address-city")
  city = "" if cityelem is None else cityelem.text
  stateelem = get_from_selector(soup, ".Core .c-address-state")
  state = "" if stateelem is None else stateelem.text
  zipcodeelem = get_from_selector(soup, ".Core .c-address-postal-code")
  zipcode = "" if zipcodeelem is None else zipcodeelem.text
  countryelem = get_from_selector(soup, ".Core .c-address-country-name")
  country = "" if countryelem is None else countryelem.text
  phoneelem = get_from_selector(soup, ".Core .Phone-link")
  phone = "" if phoneelem is None else phoneelem["href"][5:-1]
  result = SubwayLocation(found_name.text, "{}/{}".format(URL, url.strip("../")), longitude, latitude, address1, address2, city, state, zipcode, country, phone)
  print(result.output())
  result_file.write("{}\n".format(result.output()))

  return result

def get_links(baseurl, url):
  fullurl = "{}/{}".format(baseurl, url)
  page = requests.get(fullurl)
  if page.status_code < 200 or page.status_code >= 300:
    print("[{}] -------- '{}'".format(page.status_code, fullurl))
    return []
  #print(fullurl)
  soup = BeautifulSoup(page.content, "html.parser")
  found_links = [x["href"] for x in soup.find_all(class_="Directory-listLink")]
  results = []
  if len(found_links) > 0:
    # recurse to directory page
    #print("directory {}".format(url))
    results = [get_links(baseurl, x) for x in found_links]
  else:
    found_teasers = [x["href"] for x in soup.select(".Directory-listTeaser .Teaser-title")]
    if len(found_teasers) > 0:
      # recurse final page
      #print("teasers {}".format(url))
      results = [get_links(baseurl, x) for x in found_teasers]
    else:
      #print("final {}".format(url))
      results = [parse_location(soup, url)]
  return results

result_file.write(SubwayLocation.names())
result_file.write("\n")
results = get_links(URL, "")
result_file.close()
