from pyshorteners import Shortener

url="https://youtube.com"

url_shortner = Shortener()

print("Short URL {}".format(url_shortner.tinyurl.short(url)))