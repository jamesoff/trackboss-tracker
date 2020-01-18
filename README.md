# Trackboss Tracker

(or is my trackboss having a heart attack)

## What? Why? How?

Started out as a discussion based on my experience as a DeepRacer track boss especially helping support the 2019 Championship at re:Invent.  Having just chased another fast car around the track and taking a breather in between competitors I thought it might be interesting to be able to show the heart rate (and step data) of the track boss in real time as part of the DeepRacer event experience (and be handy to see if the Trackboss was having a heart attack).

## Components

The repo contains all parts of an application to show real time HR data (currently) in a graph for display at DeepRacer events, the breakdown of code is as below:

### hrm

`hrm.py` is used to connect to the HR chest strap (currently only tested using a [Polar H10](https://www.amazon.co.uk/gp/product/B07PM54P4N/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)).

#### Installing

    $ pip3 install -r requirements.txt

#### Running

    $ python3 hrm.py <device ID>

### trackboss-server

Express.js based application to read HR data from MQTT and push to [socket.io server](https://socket.io/docs/server-api/) for use by the frontend.

#### Installing

    $ npm install

#### Running

To run using data from the MQTT queue (live HR data)

    $ npm run serve

### trackboss-client

[Vue.js](https://vuejs.org/) based front end application to graph the HR data using [socket.io client](https://socket.io/docs/client-api/)

#### Installing

    $ npm install

#### Running

To run using data from the MQTT queue (live HR data)

    $ npm run serve
