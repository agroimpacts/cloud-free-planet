function init(kmlPath, kmlName, assignmentId, tryNum, resultsAccepted, mapPath, workerId) {

    var saveStrategyActive, workerFeedback;
    saveStrategyActive = false;
    workerFeedback = false;

    // If this is a mapping HIT or training map, let user save changes.
    if (assignmentId.length > 0) {
        saveStrategyActive = true;
    } else if (workerId.length > 0) {
        workerFeedback = true;
    }

    // Mouse position
    var mousePositionControl = new ol.control.MousePosition({
        coordinateFormat: ol.coordinate.createStringXY(3),
        projection: 'EPSG:4326',
        undefinedHTML: '&nbsp;'
    });
    
    // You will need to replace the 'access_token' and 'Map ID' values with your own.
    var dg1Layer = new ol.layer.Tile({
        title: 'DG Recent',
        type: 'base',
        visible: false,
        source: new ol.source.XYZ({
            url: 'http://api.tiles.mapbox.com/v4/digitalglobe.nal0g75k/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZDRsaWhoNTF3MGEycXFkbWp2dTQ2bGgifQ.atgDhFJtnYI4dTm4a08-PQ', 
        })
    });

    //var dg2Layer = new ol.layer.Tile({
    //    title: 'DigitalGlobe Vivid',
    //    type: 'base',
    //    visible: false,
    //    source: new ol.source.XYZ({
    //        url: 'http://api.tiles.mapbox.com/v4/digitalglobe.3602132d/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZDRsaWhoNTF3MGEycXFkbWp2dTQ2bGgifQ.atgDhFJtnYI4dTm4a08-PQ', 
    //        attribution: "© DigitalGlobe, Inc"
    //    })
    //});

    //var dg3Layer = new ol.layer.Tile({
    //    title: 'DigitalGlobe Terrain',
    //    type: 'base',
    //    visible: false,
    //    source: new ol.source.XYZ({
    //        url: 'http://api.tiles.mapbox.com/v4/digitalglobe.nako1fhg/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZDRsaWhoNTF3MGEycXFkbWp2dTQ2bGgifQ.atgDhFJtnYI4dTm4a08-PQ', 
    //    })
    //});

    //Define Planet base layer.
    //var planetLayer = new ol.layer.Tile({
    //    title: 'PlanetScope',
    //    type: 'base',
    //    visible: false,
    //    source: new ol.source.XYZ({
    //        tileSize: [512, 512],
    //        url: 'https://tiles{1-3}.planet.com/v1/PSScene3Band/20170419_051605_0c45/{z}/{x}/{y}.png?api_key=86ba55123d60492ab315935bf9e62945'
    //    })
    //});

    //Define Mapbox base layer.
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

    //Define Bing base layer.
    var bingLayer = new ol.layer.Tile({
        title: 'Bing Aerial',
        type: 'base',
        visible: true,
        source: new ol.source.BingMaps({
            key: 'esMqD5pajkiIvp26krWq~xK2nID-glxBU5PYtVmuoMw~AhanXg6fK3a8vRhyc1O-FgeHTWfzerYO4ptmwz9eGjcUh53y7Zu5cU4BT_en6fzW',
            imagerySet: 'Aerial'
        })
    });

    // Create overlay layer(s) group.
    overlayGroup = new ol.layer.Group({
        title: 'Overlay(s)',
        layers: []
    })
    // Create the map using the specified DOM element
    map = new ol.Map({
        controls: ol.control.defaults({
            attributionOptions:  ({
                collapsible: false
            })
        }).extend([mousePositionControl]),
        layers: [
            // Create overlay layer(s) group.
            overlayGroup,
            // Create base layer group.
            new ol.layer.Group({
                title: 'Base Layer',
                //layers: [dg3Layer, dg2Layer, dg1Layer, planetLayer, mapboxLayer, bingLayer]
                layers: [dg1Layer, mapboxLayer, bingLayer]
            })
            // Create multi-band image layer group.
            //new ol.layer.Group({
            //    title: 'Satellite Image Overlays',
            //  *** TODO: add WMS layer definitions here. ***
            //    layers: []
            //})
        ],
        target: document.getElementById('kml_display')
    });

    // Set view and zoom.
    map.setView(new ol.View({
        projection: 'EPSG:4326',
        center: [0,0],
        zoom: 14,
        minZoom: 1,
        maxZoom: 19
    }));
    
    // White bounding box KML layer: URL defined in configuration table.
    var kmlUrl = eval(`\`${kmlPath}\``);
    var kmlLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
            url: kmlUrl,
            format: new ol.format.KML({extractStyles: false})
        }),
        style: new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.0)'
            }),
            stroke: new ol.style.Stroke({
                color: 'rgba(255, 255, 255, 1.0)',
                width: 2
            })
        })
    });
    // KML must be fully loaded before getting extent info
    var kmlSource = kmlLayer.getSource();
    var key = kmlSource.on('change', function(e){
        if (kmlSource.getState() === 'ready') {
            kmlSource.unByKey(key);
            var extent = kmlSource.getExtent();
            // Center map around KML
            map.getView().fit(extent, map.getSize());
        }   
    });
    kmlLayer.setMap(map);

    // Mapped Fields layer
    var fields = new ol.Collection();
    // Add special id for all drawn features for dragging purposes.
    fields.on('add', function(event){
        var feature = event.element;
        feature.set('id', 'bounding-box');
    }); 
    var fieldsLayer = new ol.layer.Vector({
        title: "Mapped Fields",
        source: new ol.source.Vector({features: fields}),
        style: new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.2)'
            }),
            stroke: new ol.style.Stroke({
                color: '#ffcc33',
                width: 2
            }),
            image: new ol.style.Circle({
                radius: 7,
                fill: new ol.style.Fill({
                    color: '#ffcc33'
                })
            })
        })
    });
    fieldsLayer.setMap(map);
    
    //var recentLayer = new ol.layer.Image({
    //    source: new ol.source.ImageWMS({
    //        url: geoserverUrl,
    //        params: {
    //            layers: 'MappingAfrica:' + image_name,
    //            styles: 'true_color'
    //        },
    //        serverType: 'geoserver'
    //    });
    //});    
    //recentLayer.setMap(map);

    // If this is a worker-feedback map, create two additional layers.
    if (workerFeedback) {
        var rMapLayer = new ol.layer.Vector({
            title: "Reference Map",
            source: new ol.source.Vector({
                url: mapPath + '/' + workerId + '/' + kmlName + '_r.kml',
                format: new ol.format.KML({extractStyles: false})
            }),
            style: new ol.style.Style({
                fill: new ol.style.Fill({
                    color: 'rgba(255, 204, 51, 0.4)'
                }),
                stroke: new ol.style.Stroke({
                    color: '#ffcc33',
                    width: 2
                }),
            })
        });
        rMapLayer.setMap(map);

        var wMapLayer = new ol.layer.Vector({
            title: "Worker Map",
            source: new ol.source.Vector({
                url: mapPath + '/' + workerId + '/' + kmlName + '_w.kml',
                format: new ol.format.KML({extractStyles: false})
            }),
            style: new ol.style.Style({
                fill: new ol.style.Fill({
                    color: 'rgba(0, 0, 255, 0.2)'
                }),
                stroke: new ol.style.Stroke({
                    color: '#0000ff',
                    width: 2
                })
            })
        });
        wMapLayer.setMap(map);

        overlayGroup.getLayers().push(wMapLayer);
        overlayGroup.getLayers().push(rMapLayer);
    } else {
        //overlayGroup.getLayers().push(recentLayer);
        overlayGroup.getLayers().push(fieldsLayer);
    }

    // Add drag interaction.
    var dragFeature = null;
    var dragCoordinate = null;
    var dragCursor = 'pointer';
    var dragPrevCursor = null;

    var dragInteraction = new ol.interaction.Pointer({
        handleDownEvent : function(event){
            var feature = map.forEachFeatureAtPixel(event.pixel,    
                function(feature, layer) {
                    return feature;
                }
            );
            if(feature && feature.get('id') === 'bounding-box') {
                dragCoordinate = event.coordinate;
                dragFeature = feature;
                return true;
            }
            return false;
        },
        handleDragEvent : function(event){
            var deltaX = event.coordinate[0] - dragCoordinate[0];
            var deltaY = event.coordinate[1] - dragCoordinate[1];
            var geometry = dragFeature.getGeometry();
            geometry.translate(deltaX, deltaY);
            dragCoordinate[0] = event.coordinate[0];
            dragCoordinate[1] = event.coordinate[1];
        },
        handleMoveEvent : function(event){
            if (dragCursor) {
                var map = event.map;
                var feature = map.forEachFeatureAtPixel(event.pixel,
                    function(feature, layer) {
                      return feature;
                    });
                var element = event.map.getTargetElement();
                if (feature) {
                    if (element.style.cursor != dragCursor) {
                        dragPrevCursor = element.style.cursor;
                        element.style.cursor = dragCursor;
                    }
                } else if (dragPrevCursor !== undefined) {
                    element.style.cursor = dragPrevCursor;
                    dragPrevCursor = undefined;
                }
            }
        },
        handleUpEvent : function(event){
            dragCoordinate = null;
            dragFeature = null;
            return false;
        }
    });
    map.addInteraction(dragInteraction);
 
    // Add controls to Africa maps:
    // Zoom control and scale line.
    var zoomSlider = new ol.control.ZoomSlider();
    map.addControl(zoomSlider);
    var scaleLine = new ol.control.ScaleLine();
    map.addControl(scaleLine);
    
    // Layer Switcher control (OL3 doesn't have one, using another script)
    var layerSwitcher = new ol.control.LayerSwitcher({
        tipLabel: 'Layer Switcher'
    });
    map.addControl(layerSwitcher);
    
    if (!workerFeedback) {
        // Create control bar 
        var mainbar = new ol.control.Bar({
            autoDeactivate: true,   // deactivate controls in bar when parent control off
        	toggleOne: true,	    // one control active at the same time
            group: false	        // group controls together
        });
        mainbar.setPosition("top-right");
        map.addControl(mainbar);

        // Add editing tools to the editing sub control bar
        var drawBar = new ol.control.Bar({
        	toggleOne: true,    	// one control active at the same time
            autoDeactivate: true,   // deactivate controls in bar when parent control off
            group: false		    // group controls together
        });
        drawBar.addControl( new ol.control.Toggle({
            html: '<i class="icon-polygon-o" ></i>',
            title: 'Polygon creation: Click at each corner of field; double-click when done.',
            autoActivate: true,
            interaction: new ol.interaction.Draw({
            	type: 'Polygon',
                features: fields,
                //pixelTolerance: 0,
                //condition: function(event){
                //    return !ol.events.condition.shiftKeyOnly(event);
                //},
                style: new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: 'rgba(255, 255, 255, 0.2)',
                    }),
                    stroke: new ol.style.Stroke({
                        color: 'rgba(0, 153, 255, 1.0)',
                        width: 2
                    }),
                    image: new ol.style.Circle({
                        radius: 7,
                        fill: new ol.style.Fill({
                            color: 'rgba(0, 153, 255, 0.5)'
                        })
                    })
                })
            })
        }));
        drawBar.addControl( new ol.control.Toggle({
            html: '<i class="icon-circle-thin" ></i>',
            title: 'Circle creation: Click at center of field; slide mouse to expand and click when done.',
            interaction: new ol.interaction.Draw({
            	type: 'Circle',
                features: fields,
                //pixelTolerance: 0,
                // Create circle from polygon, otherwise not recognized by KML
                geometryFunction: ol.interaction.Draw.createRegularPolygon(),
                style: new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: 'rgba(255, 255, 255, 0.2)',
                    }),
                    stroke: new ol.style.Stroke({
                        color: 'rgba(0, 153, 255, 1.0)',
                        width: 2
                    }),
                    image: new ol.style.Circle({
                        radius: 7,
                        fill: new ol.style.Fill({
                            color: 'rgba(0, 153, 255, 0.5)'
                        })
                    })
                })
            })
        }));
        drawBar.addControl( new ol.control.Toggle({
            html: '<i class="icon-rectangle-o" ></i>',
            title: 'Rectangle creation: Click at corner of field; slide mouse to expand and click when done.',
            interaction: new ol.interaction.Draw({
            	type: 'LineString',
                features: fields,
                //pixelTolerance: 0,
                // Use diagonal to form rectangle
                geometryFunction: function(coordinates, geometry) {
                    if (!geometry) {
                        geometry = new ol.geom.Polygon(null);
                    }
                    var start = coordinates[0];
                    var end = coordinates[1];
                    geometry.setCoordinates([
                        [start, [start[0], end[1]], end, [end[0], start[1]], start]
                    ]);
                    return geometry;
                },
                style: new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: 'rgba(255, 255, 255, 0.2)',
                    }),
                    stroke: new ol.style.Stroke({
                        color: 'rgba(0, 153, 255, 1.0)',
                        width: 2
                    }),
                    image: new ol.style.Circle({
                        radius: 7,
                        fill: new ol.style.Fill({
                            color: 'rgba(0, 153, 255, 0.5)'
                        })
                    })
                }),
                maxPoints: 2,
            })
        }));
        drawBar.addControl( new ol.control.Toggle({
            html: '<i class="icon-square-o" ></i>',
            title: 'Square creation: Click at center of field; slide mouse to expand and click when done.',
            interaction: new ol.interaction.Draw({
            	type: 'Circle',
                features: fields,
                //pixelTolerance: 0,
                geometryFunction: ol.interaction.Draw.createRegularPolygon(4),
                style: new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: 'rgba(255, 255, 255, 0.2)',
                    }),
                    stroke: new ol.style.Stroke({
                        color: 'rgba(0, 153, 255, 1.0)',
                        width: 2
                    }),
                    image: new ol.style.Circle({
                        radius: 7,
                        fill: new ol.style.Fill({
                            color: 'rgba(0, 153, 255, 0.5)'
                        })
                    })
                })
            })
        }));

        // Add drawing sub control bar to the drawButton control
        var drawButton = new ol.control.Toggle({
        	html: '<i class=" icon-draw" ></i>',
            title: 'To create mapped fields, click on one of the tools to the left.',
            autoActivate: true, // activate controls in bar when parent control on
            active: true,
            bar: drawBar
        });
        mainbar.addControl(drawButton);
        // Need the following  to be last to ensure Modify tool processes clicks before Draw tool.
        // Add edit tool.
        var editButton = new ol.control.Toggle({
        	html: '<i class=" icon-edit" ></i>',
            title: 'To edit any mapped field, drag center of field to move it; drag any border line to stretch it; shift-click on any field corner to delete vertex.',
            interaction: new ol.interaction.Modify({
                features: fields,
                //pixelTolerance: 4,
                // The SHIFT key must be pressed to delete vertices, so that new
                // vertices  can be drawn at the same position as existing vertices.
                deleteCondition: function(event) {
                    return ol.events.condition.shiftKeyOnly(event) &&
                    ol.events.condition.singleClick(event);
                },
                style: new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: 7,
                        fill: new ol.style.Fill({
                            color: '#ffcc33'
                        }),
                        stroke: new ol.style.Stroke({
                            color: 'white',
                            width: 2
                        })
                    })
                }) 
            })
        });
        mainbar.addControl(editButton);
        //map.addInteraction(modify);

        // Add selection tool (a toggle control with a select interaction)
        var delBar = new ol.control.Bar();
        var selectCtrl = new ol.control.Toggle({
            html: '<i class="icon-select-o"></i>',
            title: "Select tool: Click a mapped field to select for deletion. Shift-click to select multiple fields.",
            interaction: new ol.interaction.Select({ layers: [fieldsLayer] }),
            bar: delBar
        });
        mainbar.addControl(selectCtrl);

        delBar.addControl( new ol.control.Toggle({
            html: '<i class="icon-delete-o"></i>',
            title: "Click this button to delete selected mapped field(s).",
            className: "noToggle",
            onToggle: function() {
                var features = selectCtrl.getInteraction().getFeatures();
                if (!features.getLength()) alert("Please click on one or more mapped fields to select for deletion first.");
                for (var i=0, f; f=features.item(i); i++) {
                    fieldsLayer.getSource().removeFeature(f);
                }
                selectCtrl.getInteraction().getFeatures().clear();
            }
        }));

        // Add a return button with on active event
        var returnButton = new ol.control.Toggle(
                {	html: '<i class="icon-back"></i>',
                    title: 'Return map: Click this button if you wish to return this map and be provided with another one. NOTE: this may result in a reduction of your quality score.',
                    className: "noToggle"
                });
        mainbar.addControl(returnButton);
        returnButton.on("change:active", function(e)
        {	
            if (e.active) {
                checkReturnStrategy(kmlName);
            }
        });

        // Add a save button with on active event
        var saveButton = new ol.control.Toggle(
                {	html: '<i class="icon-save"></i>',
                    title: 'Save changes: Click this button only ONCE when all mapped fields have been created, and you are satisfied with your work. Click when done even if there are NO fields to draw on this map.',
                    className: "noToggle"
                });
        mainbar.addControl(saveButton);
        saveButton.on("change:active", function(e)
        {	
            if (e.active) {
                checkSaveStrategy(kmlName);
            }
        });
    }

    // Current feature.
    var curFeature;

    // Add event handler to execute each time a shape is drawn.
    fieldsLayer.getSource().on('addfeature', function(event) {
        // TODO: prevent user from reactivating controls. Make invisible?
        // Deactivate the control bar.
        mainbar.setActive(false);

        // Get the pixel coordinates of the center of the new feature.
        curFeature = event.feature;
        var extent = curFeature.getGeometry().getExtent();
        var coords = ol.extent.getCenter(extent);
        var pixel = map.getPixelFromCoordinate(coords);

        // Position the labeling block at this location, and make it visible.
        var style = document.getElementById("labelBlock").style;
        // NOTE: this next line should be in style.css since it's cosmetic.
        style.fontSize = "small";
        style.left = Math.round(pixel[0]) + "px";
        style.top = (Math.round(pixel[1])) + "px";
        style.display = "block";
    });

    // Add event handler to process post-drawing labeling.
    $(document).on("click", "button#labelDone", function() {
        var category = document.getElementById("categLabel").value;
        curFeature.set('category', category);
        var comment = document.getElementById("commentLabel").value;
        curFeature.set('comment', comment);

        // Hide the labeling block and reset the imputs.
        document.getElementById("labelBlock").style.display = "none";
        document.getElementById("categLabel").selectedIndex = 0;
        document.getElementById("commentLabel").value = "";

        // Reactivate the control bar to the create-fields position.
        mainbar.setActive(true);
    });

    // Training case only.
    if (tryNum > 0) {
        if (resultsAccepted == 1) {
            alert("Congratulations! You successfully mapped the crop fields in this map. Please click OK to work on the next training map.");
        } else if (resultsAccepted == 2) {
            alert("We're sorry, but you failed to correctly map the crop fields in this map. Please click OK to try again.");
        }
    }
    // Mapping HIT or training map cases.
    if (resultsAccepted == 3) {
        alert("Error! Through no fault of your own, your work could not be saved. Please try the same map again. We apologize for the inconvenience.");
    }

    function checkSaveStrategy(kmlName) {
        var msg;

        // Check if the Save button is enabled.
        if (!saveStrategyActive) {
            return;
        }
        var features = fieldsLayer.getSource().getFeatures();
        if (features != '') {
            msg = 'You can only save your mapped fields ONCE!\nPlease confirm that you\'re COMPLETELY done mapping fields.\nIf not done, click Cancel.';
        } else {
            msg = 'You have not mapped any fields!\nYou can only save your mapped fields ONCE!\nPlease confirm that you\'re COMPLETELY done mapping fields.\nIf not done, click Cancel.'
        }
        if (!confirm(msg)) {
            return;
        }
        // Don't allow Save button to be used again.
        saveStrategyActive = false

        // Save the current polygons if there are any.
        if (features != '') {
            categories = [];
            categComments = [];
            var i = 1;
            for (var feature in features) {
                features[feature].set('name', kmlName + '_' + i);
                categories.push(features[feature].get('category'));
                //console.log("category: " + categories[i-1]);
                categComments.push(features[feature].get('comment'));
                //console.log("comment: " + categComments[i-1]);
                i = i + 1;
            }
            var kmlFormat = new ol.format.KML();
            var kmlData = kmlFormat.writeFeatures(features, {featureProjection: 'EPSG:4326', dataProjection: 'EPSG:4326'});
            // Save the kmlData in the HTML mappingform.
            document.mappingform.kmlData.value = kmlData;
            document.mappingform.categories.value = categories;
            document.mappingform.categComments.value = categComments;
        }
        // Mark that we saved our results.
        document.mappingform.savedMaps.value = true;

        document.mappingform.submit();
    }

    function checkReturnStrategy(kmlName) {
        var msg;

        // Check if the Return button is enabled.
        if (!saveStrategyActive) {
            return;
        }
        msg = 'You are about to return this map without saving any results!\nPlease confirm that this is what you want to do.\nNOTE: this may result in a reduction of your quality score.\nIf you do not wish to return this map, click Cancel.';
        if (!confirm(msg)) {
            return;
        }
        // Don't allow Return button to be used again.
        saveStrategyActive = false

        // Mark that we returned this map.
        document.mappingform.savedMaps.value = false;

        document.mappingform.submit();
    }

}
