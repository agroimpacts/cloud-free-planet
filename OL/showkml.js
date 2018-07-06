function init(kmlPath, kmlName, assignmentId, tryNum, resultsAccepted, mapPath, workerId, wmsUrl, wmsAttributes) {

    var saveStrategyActive = false;
    var workerFeedback = false;
    // If this is a mapping HIT or training map, let user save changes.
    if (assignmentId.length > 0) {
        saveStrategyActive = true;
    // Else, check if this is a worker feedback map.
    } else if (workerId.length > 0) {
        workerFeedback = true;
    }

    //
    // *** Create map, overlays, and view ***
    //
    var map = new ol.Map({
        controls: ol.control.defaults({
            attributionOptions:  ({
                collapsible: false
            })
        }).extend([new ol.control.MousePosition({
            coordinateFormat: ol.coordinate.createStringXY(3),
            projection: 'EPSG:4326',
            undefinedHTML: '&nbsp;'
        })]),
        interactions: ol.interaction.defaults({
            doubleClickZoom :false
        }),
        // NOTE: the zIndex convention (higher number = higher layer) is as follows:
        // 0-9: Base layers (only one at a time is visible)
        // 10-99: WMS layers (zIndex specified in DB)
        // 100: KML layer (not visible in layer switcher)
        // 101: Fields layer (mapped by worker)
        // 102: Reference map layer (worker feedback case)
        // 103: Worker map layer (worker feedback case)
        layers: [
            // Create overlay layer(s) group.
            new ol.layer.Group({
                title: 'Field Overlay(s)',
                layers: []
            }),
            // Create multi-band image layer group.
            new ol.layer.Group({
                title: 'Satellite Image Overlays',
                layers: []
            }),
            // Create base layer group.
            new ol.layer.Group({
                title: 'Base Layer',
                layers: [bingLayer, mapboxLayer, dg1Layer]
            })
        ],
        // Use the specified DOM element
        target: document.getElementById('kml_display')
    });
    // Set view and zoom.
    map.setView(new ol.View({
        projection: 'EPSG:4326',
        center: [0,0],
        zoom: 14,
        minZoom: 4,
        maxZoom: 19
    }));
    // Disable right-click context menu to allow right-click map panning.
    map.getViewport().addEventListener('contextmenu', function (evt) {
        evt.preventDefault();
    });
    
    // *** Create grid cell ***
    // White bounding box KML layer: URL defined in configuration table.
    // No title: so not in layer switcher.
    var kmlUrl = eval(`\`${kmlPath}\``);
    var kmlLayer = new ol.layer.Vector({
        zIndex: 100,
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
            // OL4 change
            //kmlSource.unByKey(key);
            ol.Observable.unByKey(key);
            var extent = kmlSource.getExtent();
            // Center map around KML
            map.getView().fit(extent, map.getSize());
        }   
    });
    kmlLayer.setMap(map);

    // *** If not a worker feedback case, add mapped fields and WMS layers ***
    if (!workerFeedback) {
        var fieldsLayer = new ol.layer.Vector({
            title: "Mapped Fields",
            zIndex: 101,
            source: new ol.source.Vector({
                features: new ol.Collection()
            }),
            style: function (feature) {
                // If not a Point then style normally.
                if (feature.getGeometry().getType() !== 'Point') {
                    return [
                        new ol.style.Style({
                            fill: new ol.style.Fill({
                                // Edit line below to change unselected shapes' transparency.
                                color: 'rgba(255, 255, 255, 0.2)'
                            }),
                            stroke: new ol.style.Stroke({
                                color: '#ffcc33',
                                width: 2
                            })
                        }),
                        new ol.style.Style({
                            image: new ol.style.Circle({
                                radius: 3,
                                fill: new ol.style.Fill({
                                    color: '#ffcc33'
                                })
                            }),
                            geometry: function(feature) {
                                // return the coordinates of the first ring of the polygon
                                var coordinates = feature.getGeometry().getCoordinates()[0];
                                return new ol.geom.MultiPoint(coordinates);
                            }
                        })
                    ];
                // Else, just draw a circle.
                } else {
                    return [
                        new ol.style.Style({
                            image: new ol.style.Circle({
                                radius: 5,
                                fill: new ol.style.Fill({
                                    color: '#ffcc33'
                                })
                            })
                        })
                    ];
                }
            }
        });
        // Add fieldsLayer as a managed layer (i.e., don't use setMap()).
        map.getLayers().getArray()[0].getLayers().push(fieldsLayer);
        
        //
        //*** Create the WMS layers  based on wms_data table ***
        //
        // Named constants (must match order in getWMSAttributes()).
        var PROVIDER = 0;
        var IMAGE_NAME = 1;
        var STYLE = 2;
        var ZINDEX = 3;
        var VISIBLE = 4;
        var DESCRIPTION = 5;

        // Array is assumed to be in ascending zIndex order, so process in reverse.
        var wmsLayer = [];
        for (var i = wmsAttributes.length - 1; i >= 0; i--) {
            wmsAttribute = wmsAttributes[i];
            wmsLayer[i] = new ol.layer.Image({
                zIndex: wmsAttribute[ZINDEX],
                visible: wmsAttribute[VISIBLE],
                title: wmsAttribute[DESCRIPTION],
                source: new ol.source.ImageWMS({
                    url: wmsUrl,
                    params: {
                        VERSION: '1.1.1',
                        LAYERS: wmsAttribute[PROVIDER] + ':' + wmsAttribute[IMAGE_NAME],
                        STYLES: wmsAttribute[PROVIDER] + ':' + wmsAttribute[STYLE]
                    }
                })
            });    
            // Add new WMS layer to Satellite Image Overlays in Layer Switcher.
            map.getLayers().getArray()[1].getLayers().push(wmsLayer[i]);
        }

    // Else, create reference map and worker map layers
    } else {
        var wMapLayer = new ol.layer.Vector({
            title: "Worker Map",
            zIndex: 103,
            source: new ol.source.Vector({
                url: mapPath + '/' + workerId + '/' + kmlName + '_w.kml',
                format: new ol.format.KML({extractStyles: false})
                //url: mapPath + '/' + workerId + '/' + kmlName + '_w.json',
                //format: new ol.format.GeoJSON()
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
        map.getLayers().getArray()[0].getLayers().push(wMapLayer);

        var rMapLayer = new ol.layer.Vector({
            title: "Reference Map",
            zIndex: 102,
            source: new ol.source.Vector({
                url: mapPath + '/' + workerId + '/' + kmlName + '_r.kml',
                format: new ol.format.KML({extractStyles: false})
                // Replace with the next 2 lines if we switch to GeoJSON.
                //url: mapPath + '/' + workerId + '/' + kmlName + '_r.json',
                //format: new ol.format.GeoJSON()
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
        map.getLayers().getArray()[0].getLayers().push(rMapLayer);
    }

    // *** Add miscellaneous controls ***
    //
    // Zoom control
    var zoomSlider = new ol.control.ZoomSlider();
    map.addControl(zoomSlider);

    // Scale line
    var scaleLine = new ol.control.ScaleLine();
    map.addControl(scaleLine);
    
    // Layer Switcher control
    if (!workerFeedback) {
        showPanel = false;
    } else {
        showPanel = true;
    }
    var layerSwitcher = new ol.control.LayerSwitcher({
        reverse: false,
        showPanel: showPanel,
        tipLabel: 'Layer Switcher'
    });
    map.addControl(layerSwitcher);

    // Main control bar with sub-menus
    if (!workerFeedback) {
        var retVals = addControlBar(map, fieldsLayer, checkSaveStrategy, checkReturnStrategy, kmlName);
        var mainbar = retVals[0];
        var selectButton = retVals[1];

    // Worker feedback field selection.
    } else{
        selectFeedback = new ol.interaction.Select({
            condition: ol.events.condition.click,
            layers: [wMapLayer, rMapLayer]
        });
        map.addInteraction(selectFeedback);

        // Adjust labeling block so fields are read-only and save button is invisible.
        document.getElementById("categLabel").setAttribute("disabled", true);
        document.getElementById("commentLabel").setAttribute("readonly", true);
        document.getElementById("labelDone").style.display = "none";
    }

    // *** Handle the labeling block ***
    // Mapping cases.
    if (!workerFeedback) {
        // Add event handler to execute each time a shape is drawn.
        var mainbarVisible = true;
        var activeControl = null;
        fieldsLayer.getSource().on('addfeature', function(event) {
            // Render the control bar invisible and inactive.
            mainbar.setVisible(false);
            // Remember which drawing control is active so we can reactivate it later.
            var ctrls = mainbar.getControls()[0].getSubBar().getControls();
            for (var i = 0; i < ctrls.length; i++) {
                activeControl = ctrls[i];
                if (activeControl.getActive()) {
                    break;
                }
            }
            mainbar.setActive(false);
            mainbarVisible = false;
            // Clear all shape selections.
            selectButton.getInteraction().getFeatures().clear();
            // Display the labeling block.
            showLabelBlock(event.feature);
        });
        // Add event handler to execute each time a shape is selected.
        selectButton.getInteraction().getFeatures().on('add', function (event) {
            // Display the labeling block, but only if a single feature is selected.
            if (selectButton.getInteraction().getFeatures().getLength() == 1) {
                showLabelBlock(event.element);
            } else {
                // Hide the labeling block, in case visible.
                document.getElementById("labelBlock").style.display = "none";
            }
        });
        // Add event handler to execute each time a shape is unselected.
        selectButton.getInteraction().getFeatures().on('remove', function (event) {
            // Hide the labeling block, in case visible.
            document.getElementById("labelBlock").style.display = "none";
        });
        // Add event handler to clear selection and hide labeling block when layerswitcher makes layer invisible.
        fieldsLayer.on('propertychange', function(event) {
            if (event.key == 'visible' && !fieldsLayer.getVisible()) {
                // Clear all shape selections.
                selectButton.getInteraction().getFeatures().clear();
                // Hide the labeling block, in case visible.
                document.getElementById("labelBlock").style.display = "none";
            }
        });
    // Worker feedback case.
    } else {
        // Add event handler to execute each time a shape is selected.
        selectFeedback.getFeatures().on('add', function(event) {
            // Ensure that only one layer is enabled.
            if (rMapLayer.getVisible() && wMapLayer.getVisible()) {
                // Clear all shape selections.
                selectFeedback.getFeatures().clear();
                // Hide the labeling block, in case visible.
                document.getElementById("labelBlock").style.display = "none";
                // setTimeout() allows the background tasks above to complete in the 1 second allowed.
                setTimeout("alert('Please deselect the Reference Map or the Worker Map so that your click uniquely identifies a field on a specific layer.');", 1);
            // Display the labeling block, but only if a single feature is selected.
            } else {
                if (selectFeedback.getFeatures().getLength() == 1) {
                    showLabelBlock(event.element);
                } else {
                    // Hide the labeling block, in case visible.
                    document.getElementById("labelBlock").style.display = "none";
                }
            }
        });
        // Add event handler to execute each time a shape is unselected.
        selectFeedback.getFeatures().on('remove', function (event) {
            // Hide the labeling block, in case visible.
            document.getElementById("labelBlock").style.display = "none";
        });
        // Add event handler to clear selection and hide labeling block when layerswitcher makes layer invisible.
        rMapLayer.on('propertychange', function(event) {
            if (event.key == 'visible' && !rMapLayer.getVisible()) {
                // Clear all shape selections.
                selectFeedback.getFeatures().clear();
                // Hide the labeling block, in case visible.
                document.getElementById("labelBlock").style.display = "none";
            }
        });
        // Add event handler to clear selection and hide labeling block when layerswitcher makes layer invisible.
        wMapLayer.on('propertychange', function(event) {
            if (event.key == 'visible' && !wMapLayer.getVisible()) {
                // Clear all shape selections.
                selectFeedback.getFeatures().clear();
                // Hide the labeling block, in case visible.
                document.getElementById("labelBlock").style.display = "none";
            }
        });
    }
    // Display the label block for the specified feature.
    var curFeature;
    function showLabelBlock(feature) {
        // Get the pixel coordinates of the center of the feature.
        curFeature = feature;
        var extent = feature.getGeometry().getExtent();
        var coords = ol.extent.getCenter(extent);
        var pixel = map.getPixelFromCoordinate(coords);

        // Adjust as needed for offscreen locations.
        var left = Math.round(pixel[0]);
        var top = Math.round(pixel[1]);
        var limits = map.getSize();
        var leftLimit = 20;
        var topLimit = 30;
        var rightLimit = limits[0] - 180;
        var bottomLimit = limits[1] - 50;
        if (left < leftLimit) left = leftLimit;
        if (left > rightLimit) left = rightLimit;
        if (top < topLimit) top = topLimit;
        if (top > bottomLimit) top = bottomLimit;

        // Position the labeling block at the computed location.
        var style = document.getElementById("labelBlock").style;
        style.left = left + "px";
        style.top = top + "px";
        //console.log('left: ' + left + "px");
        //console.log('top: ' + top + "px");

        // Set the category and categComment values.
        category = feature.get('category');
        // If attributes are present in the feature, use them.
        if (category !== undefined) {
            categComment = feature.get('categ_comment');
            document.getElementById("categLabel").value = category;
            document.getElementById("commentLabel").value = categComment;
        // Else, initialize the input elements.
        } else {
            // Use select default for normal case, empty selection for worker feedback case.
            if (!workerFeedback) {
                document.getElementById("categLabel").selectedIndex = 0;
            } else {
                document.getElementById("categLabel").value = "";
            }
            document.getElementById("commentLabel").value = "";
        }
        // Display the labeling block.
        style.display = "block";
    };
    // Add event handler to process post-drawing labeling.
    $(document).on("click", "button#labelDone", function() {
        var category = document.getElementById("categLabel").value;
        curFeature.set('category', category);
        var comment = document.getElementById("commentLabel").value;
        curFeature.set('categ_comment', comment);

        // Clear all shape selections.
        selectButton.getInteraction().getFeatures().clear();

        // Hide the labeling block.
        document.getElementById("labelBlock").style.display = "none";

        // Render the control bar active and visible if needed.
        if (!mainbarVisible) {
            mainbarVisible = true;
            mainbar.setActive(true);
            // Reactivate the control that was active prior to labeling.
            activeControl.setActive(true);
            mainbar.setVisible(true);
        }
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
        // NOTE: the KML writeFeatures() function does not support extended attributes.
        // So we need to extract them from each feature and pass them separately as arrays.
        if (features != '') {
            var i = 1;
            for (var feature in features) {
                features[feature].set('name', kmlName + '_' + i);
                i = i + 1;
            }
            var kmlFormat = new ol.format.KML();
            var kmlData = kmlFormat.writeFeatures(features, {featureProjection: 'EPSG:4326', dataProjection: 'EPSG:4326'});
            // Save the kmlData in the HTML mappingform.
            document.mappingform.kmlData.value = kmlData;
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
