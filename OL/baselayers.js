//
// *** All base layers go here ***
//

// Define Bing base layer.
var bingLayer = new ol.layer.Tile({
    title: 'Bing Aerial',
    type: 'base',
    visible: true,
    source: new ol.source.BingMaps({
        key: 'esMqD5pajkiIvp26krWq~xK2nID-glxBU5PYtVmuoMw~AhanXg6fK3a8vRhyc1O-FgeHTWfzerYO4ptmwz9eGjcUh53y7Zu5cU4BT_en6fzW',
        imagerySet: 'Aerial'
    })
});

// Define Mapbox base layer.
var mapboxLayer = new ol.layer.Tile({
    title: 'Mapbox',
    type: 'base',
    visible: false,
    source: new ol.source.XYZ({
        attributions: '&copy; <a href="https://www.mapbox.com/map-feedback/">Mapbox</a>',
        tileSize: [512, 512],
        url: 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibGluZHplbmciLCJhIjoiY2lwNzJ0amIwMDBqN3Q2bHl5anJqZXowbyJ9.dauHM2mZRuajvxcAOALHsA'
    })
});

// Define the Digital Globe Recent base layer.
// (replace the 'access_token' and 'Map ID' values with your own)
var dg1Layer = new ol.layer.Tile({
    title: 'DG Recent',
    type: 'base',
    visible: false,
    source: new ol.source.XYZ({
        url: 'http://api.tiles.mapbox.com/v4/digitalglobe.nal0g75k/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZDRsaWhoNTF3MGEycXFkbWp2dTQ2bGgifQ.atgDhFJtnYI4dTm4a08-PQ', 
    })
});

// Define the Digital Globe Vivid base layer.
//var dg2Layer = new ol.layer.Tile({
//    title: 'DigitalGlobe Vivid',
//    type: 'base',
//    visible: false,
//    source: new ol.source.XYZ({
//        url: 'http://api.tiles.mapbox.com/v4/digitalglobe.3602132d/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZDRsaWhoNTF3MGEycXFkbWp2dTQ2bGgifQ.atgDhFJtnYI4dTm4a08-PQ', 
//        attribution: "© DigitalGlobe, Inc"
//    })
//});

// Define the Digital Globe Terrain base layer.
//var dg3Layer = new ol.layer.Tile({
//    title: 'DigitalGlobe Terrain',
//    type: 'base',
//    visible: false,
//    source: new ol.source.XYZ({
//        url: 'http://api.tiles.mapbox.com/v4/digitalglobe.nako1fhg/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZDRsaWhoNTF3MGEycXFkbWp2dTQ2bGgifQ.atgDhFJtnYI4dTm4a08-PQ', 
//    })
//});

// Define Planet base layer.
//var planetLayer = new ol.layer.Tile({
//    title: 'PlanetScope',
//    type: 'base',
//    visible: false,
//    source: new ol.source.XYZ({
//        tileSize: [512, 512],
//        url: 'https://tiles{1-3}.planet.com/v1/PSScene3Band/20170419_051605_0c45/{z}/{x}/{y}.png?api_key=86ba55123d60492ab315935bf9e62945'
//    })
//});
