# TCU
_TCU is an independent production by MathArtBang and is not affiliated with the Melsonian Arts Council._

Live version https://kk49.github.io/tcu/

A tool to generate a G**gle Maps style web map that can place graphics and a popup on a zoomable background. 
I'd like to use it to use it to track Troika! projects (modules, games people run, missed connections, etc...) 
on the web. I'll probably break out the source data into another repo once the format is settled.

## Get your stuff on here
To get something on here, you need to submit a json file named `sphere.json` and supporting files.
The json file format is currently something like this.
* Position should be within (+- 320, +-120) to be in "known space"
* Let's start with a size of 1.0
* Type should currently be one of these
  * "module" - for a Troika! Compatible module/art thing
  * "game" - for an actively run sphere
  * "missed-connection" - for a missed connection

```json
{
  "type": "module",
  "name": "Earth",
  "position": [64.0, 32.0],
  "size": 1.0,
  "description": "It's alright, I guess",
  "author": "Wouldn't you like to know",
  "link": 
    "<a href='https://en.wikipedia.org/wiki/Earth' target='_blank'>Wikipedia: Earth</a>",
  "image": "PIA21961.png",
  "image_src": 
    "<a href='https://photojournal.jpl.nasa.gov/catalog/PIA21961' target='_blank'>Image Source</a>"
}
```


## DETAILS
#### assets
* Nebula
    * https://photojournal.jpl.nasa.gov/catalog/PIA22568
    * https://photojournal.jpl.nasa.gov/tiff/PIA22568.tif
* Earth
    * https://photojournal.jpl.nasa.gov/catalog/PIA21961
    * https://photojournal.jpl.nasa.gov/tiff/PIA21961.tif
