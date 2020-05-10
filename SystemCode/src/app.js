//jshint esversion:9
require('dotenv').config();
const express = require("express");
const bodyParser = require("body-parser");
const ejs = require("ejs");
const app = express();
const https = require('https');
const expressApp = express().use(bodyParser.json());
const {
  WebhookClient
} = require('dialogflow-fulfillment');
const {
  dialogflow,
  Image,
} = require('actions-on-google');
var spawn = require("child_process").spawn;

process.env.DEBUG = 'dialogflow:debug';

app.set('view engine', 'ejs');

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
  extended: true
}));
app.use(express.static( __dirname + '/'));

const clientPOIID = process.env.CLIENT_POIID;
const clientID = process.env.CLIENT_ID;
const clientSecret = process.env.CLIENT_SECRET;
var cities = []; //'singapore','taipei','bangkok'
var fromDate = '2020-09-01'; //yyyy-mm-dd
var toDate = '2020-09-03';
var hotels = []; //['fullerton', 'novotel']
var hotelRating = []; //['4', '5']
const baseURL = 'https://api.amadeus.com';
var age = 18;
var sex = 'female';
var travelType = 'solo';
var adultQty = 1;
var childQty = 0;

var output = [];
var outputpoi = [];

app.get("/", function(req, res) {
  res.render("home", {});
});

app.post("/", function(req, res) {
  res.render("home", {});
});

app.get("/aboutus", function(req, res) {
  res.render("about");
});

app.post("/reset", function(req, res) {
  cities = []; //'singapore','taipei','bangkok'
  fromDate = ''; //yyyy-mm-dd
  toDate = '';
  hotels = []; //['fullerton', 'novotel']
  hotelRating = []; //['4', '5']
  age = 0;
  sex = '';
  travelType = '';
  adultQty = 0;
  childQty = 0;
  output = [];
  outputpoi = [];
  res.redirect("/");
});

app.get("/result", function(req, res) {
  //output.join("");
  res.render("result", {
    resultData: output,
  });
});

app.post("/result", function(req, res) {
  if (output.length === 0) {
    res.render('wait');
  } else {
    return res.redirect('/result');
  }
});

app.get("/poi", function(req, res) {
  res.render("poi", {
    resultPOI: outputpoi,
  });
});

app.post("/poi", function(req, res) {
  if (output.length === 0) {
    res.render('wait');
  } else {
    return res.redirect('/poi');
  }
});


app.post("/webhook", function(request, response) {
  const agent = new WebhookClient({
    request: request,
    response: response
  });

  let intent = agent.intent;
  console.log(intent);

  function cityIntent(agent) {
    let citiesPre = agent.parameters.geocity;
    //citiesPre.unshift('Singapore');
    if (citiesPre.length < 3) {
      agent.add('Your chosen cities are ' + citiesPre + '. I require at least 3 cities for me to perform my magic. Kindly input your cities again.');
    } else if (citiesPre.length > 5) {
      agent.add('Your chosen cities are ' + citiesPre + '.' + citiesPre.length + ' cities are too many for me to handle. Kindly input your cities again.');
    } else {
      agent.add('Your departure city is ' + citiesPre[0] + '.Your destination cities are ' + citiesPre.slice(1) + ". Please input your departure date - your return date (Format eg: 2020-08-20 - 2020-08-28)");
      cities = citiesPre;
      console.log(cities);
    }
  }

  function dateIntent(agent) {
    let periodDate = agent.parameters.date;
    fromDate = periodDate.startDate.substr(0, 10);
    toDate = periodDate.endDate.substr(0, 10);
    let d1 = new Date(fromDate);
    let d2 = new Date(toDate);
    const oneday = 1000 * 60 * 60 * 24;
    let duration = ((d2 - d1) / oneday);
    let durationMin = cities.length * 2 - 1;
    console.log(duration);
    let currentDate = new Date();
    if (d1 < currentDate || d2 < currentDate) {
      agent.add('Sorry. Even with my intelligence, we are unable to time travel back to the past.  Please input upcoming dates. (Format eg: 2020-08-20 - 2020-08-28)');
    } else if (d2 < d1) {
      agent.add('Return date needs to be after arrival date. Please input your dates again. (Format eg: 2020-08-20 - 2020-08-28)');
    } else if (duration < durationMin) {
      agent.add('Your travel period is ' + duration + ' days. The minimum is ' + duration + ' days for ' + cities.length + ' cities. Please input your dates again. (Format eg: 2020-08-20 - 2020-08-28)');
    } else {
      agent.add('Your departure date is ' + fromDate + ' and your return date is ' + toDate + '. Please input stars rating (between 1-5) of the hotels that you looking for. (Format eg: 5 stars or 3,4,5stars )');  //Which hotel(s) would you like to stay at? (You may specify one hotel for each destination city in the same order as above.)
      console.log(periodDate);
      console.log(fromDate);
      console.log(toDate);
    }
  }

  //for future implementation of hotel name
  /*function hotelsIntent(agent) {
    hotels = agent.parameters.hotels;
    agent.add('Your hotels are ' + hotels + '. Please input stars rating (between 1-5) of the hotels that you looking for. (Format eg: 5 stars or 3,4,5stars )');
    console.log(hotels);
  }*/

  function hotelRatingIntent(agent) {
    hotelRating = agent.parameters.hotelrating;
    agent.add('Your hotel rating is ' + hotelRating + ' stars. What is your age? (Format eg: 18 years old)');
    console.log(hotelRating);
  }

  function ageIntent(agent) {
    age = agent.parameters.age;
    agent.add('Your age is ' + age + '. What is your gender?');
    console.log(age);
  }

  function sexIntent(agent) {
    sex = agent.parameters.gender;
    agent.add('Your gender is ' + sex + '. How will you be travelling? (solo, friends,family)');
    console.log(sex);
  }

  function travelTypeIntent(agent) {
    travelType = agent.parameters.traveltype;
    runPOI();
    console.log(' Resfeber is using her Intelligence');
    if (travelType == 'solo') {
      agent.add('You will be travelling solo. Please hold on while I plan out your travel plan using my Intelligence.  After a few seconds, you can click on the "Generate Travel Plan" button on the left to view your customized travel plan.');
      console.log(travelType);
      runScript();
      console.log(' Resfeber is using her Intelligence');
    } else {
      console.log(travelType);
      //runPOI();
      //console.log(' Resfeber is using her Intelligence');
      agent.add('You will be travelling with ' + travelType + '. How many adults will be travelling? (Format eg: 3 adult)');
    }
  }

  function adultQtyIntent(agent) {
    adultQty = agent.parameters.adultqty;
    agent.add('Total no of adults is ' + adultQty + '. How many children will be travelling? (Format eg: 4 child)');
    console.log(adultQty);
  }

  function childQtyIntent(agent) {
    childQty = agent.parameters.childqty;
    agent.add('Total no of children is ' + childQty + '. Please hold on while I plan out your travel plan using my Intelligence.  After a few seconds, you can click on the "Generate Travel Plan" button on the left to view your customized travel plan.');
    console.log(childQty);
    runScript();
  }

  let intentMap = new Map();
  intentMap.set('city-intent', cityIntent);
  intentMap.set('date-intent', dateIntent);
  //intentMap.set('hotels-intent', hotelsIntent);
  intentMap.set('hotelrating-intent', hotelRatingIntent);
  intentMap.set('age-intent', ageIntent);
  intentMap.set('sex-intent', sexIntent);
  intentMap.set('traveltype-intent', travelTypeIntent);
  intentMap.set('adultqty-intent', adultQtyIntent);
  intentMap.set('childqty-intent', childQtyIntent);
  agent.handleRequest(intentMap);

});


function runScript() {
  var spawn = require("child_process").spawn;
  var process = spawn('py', ["./scripts/TravelAI.py",
    clientID, clientSecret, JSON.stringify(cities), fromDate, toDate, JSON.stringify(hotels), JSON.stringify(hotelRating), adultQty, childQty, baseURL
  ], {
    maxBuffer: 1000 * 1000 * 10
  });

  process.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
    //output += data.toString();
    output.push(data);
    //console.log(output);
  });

  process.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  process.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    //output.join("");
  });
}

function runPOI() {
  var spawn = require("child_process").spawn;
  var process = spawn('py', ["./scripts/TravelAI_POI.py",
    clientPOIID, JSON.stringify(cities), age, sex, travelType
  ], {
    maxBuffer: 1000 * 1000 * 10
  });

  process.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
    outputpoi.push(data);
  });

  process.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  process.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });
}


let port = process.env.PORT;
if (port == null || port == "") {
  port = 3000;
}

app.listen(port, function() {
  console.log("Server started successfully");
});
