//
// Static variables denoting the order of the drawing tools.
// NOTE: These must be changed if the order of the drawing tools in drawBar is changed.
//
var POLYGON = 0;
var CIRCLE = 1;
var RECTANGLE = 2;
var SQUARE = 3;
var HOLE = 4;
var POINT = 5;

// 
// *** Create control bar ***
//
function addControlBar(map, fieldsLayer, checkSaveStrategy, checkReturnStrategy, kmlName, snapTolerance) {
    // JSTS is used to prevent feature overlaps.
    var jstsParser = new jsts.io.OL3Parser();
    var geomFactory = new jsts.geom.GeometryFactory();
    var LI = new jsts.algorithm.RobustLineIntersector();

    // Check for self-intersection.
    // Used in polygon/polygon-hole 'condition' and 'finishCondition' clauses, and for 'modifyend' processing.
    function hasSelfIntersection(geom, closed) {
        // Only applies to quadrilaterals or greater.
        if (geom && geom.getCoordinates()[0].length >= 5) {
            // Convert to JSTS geometry and coordinates.
            var jsts_geom = jstsParser.read(geom);
            // First check the exterior ring of the polygon.
            var jsts_coords = jsts_geom.getExteriorRing().getCoordinates();
            // Make it into a linear ring.
            var linRing = geomFactory.createLinearRing(jsts_coords);
            // If linear ring is not simple, then it self-intersects.
            intersects = !linRing.isSimple();
            if (intersects) {
                console.log("hasSelfIntersection: true");
                return true;
            }
            // Then check all interior rings, if any.
            for (i = 0; i < jsts_geom.getNumInteriorRing(); i++) {
                jsts_coords = jsts_geom.getInteriorRingN(i).getCoordinates(); 
                // Make each ring's coordinates into a linear ring.
                var linRing = geomFactory.createLinearRing(jsts_coords);
                // If linear ring is not simple, then it self-intersects.
                intersects = !linRing.isSimple();
                if (intersects) {
                    console.log("hasSelfIntersection: true");
                    return true;
                }
            }
        }
        console.log("hasSelfIntersection: false");
        return false;
    }

    // Check most-recent drawn segment against all other shapes on the canvas for any intersection.
    // Used in polygon 'condition' clause.
    function hasLastSegmentIntersection(geom) {
        if (!(geom && geom.getCoordinates()[0].length >= 3)) {
            return false;
        }
        // If drawing first segment, handle as special case
        // since JSTS considers this an invalid geometry.
        if (geom.getCoordinates()[0].length == 3) {
            var coords = geom.getCoordinates()[0];
            uniqCoords = [];
            uniqCoords.push(new jsts.geom.Coordinate(coords[0][0], coords[0][1]));
            uniqCoords.push(new jsts.geom.Coordinate(coords[1][0], coords[1][1]));
            i = 0;
        // Convert polygon being drawn to JSTS geometry and coordinates.
        } else if (geom.getCoordinates()[0].length >= 4) {
            var jsts_geom = jstsParser.read(geom);
            var jsts_coords = jsts_geom.getCoordinates();
            // Remove any adjacent duplicate coordinates (caused by closing shape).
            // Also leave off final duplicate coordinate.
            uniqCoords = [];
            for (i = 0; i < jsts_coords.length - 1; i++) {
                if (!(jsts_coords[i].x == jsts_coords[i + 1].x &&
                        jsts_coords[i].y == jsts_coords[i + 1].y)) {
                    uniqCoords.push(jsts_coords[i]);
                }
            }
            // Specify the index of the last segment's starting coorninate.
            i = uniqCoords.length - 2;
        }
        // Compare last polygon segment drawn to the segments of all shapes on the canvas.
        var features = fieldsLayer.getSource().getFeatures();
        for (var f in features) {
            var feature = features[f];
            var jsts_featureGeom = jstsParser.read(feature.getGeometry());
            // Create a negative 1-pixel buffer to allow for border sharing.
            var resolution = map.getView().getResolution();
            var jsts_bufGeom = jsts_featureGeom.buffer(-resolution);
            var jsts_bufCoords = jsts_bufGeom.getExteriorRing().getCoordinates();
            for (j = 0; j < jsts_bufCoords.length - 1; j++) {
                intersects = LI.hasIntersection(LI.computeIntersection(
                    uniqCoords[i],
                    uniqCoords[i + 1],
                    jsts_bufCoords[j],
                    jsts_bufCoords[j +1]
                ));
                console.log("hasLastSegmentIntersection: " + i + "-" + j + ": " + intersects);
                if (intersects) {
                    return true;
                }
            }
        }
        return false;
    }

    // Used in all Draw tool 'condition' clause for point overlap testing.
    function pointOverlapCheck(event) {
        var feature = getClickFeature(event, 0);

        // If we found an overlap, check to see if it's inside the feature's boundary.
        // If it's only on the border, we return true to allow adding the vertex.
        if (feature) {
            // Create JSTS geometries for the click coordinates and the feature it overlaps with.
            var jsts_point = geomFactory.createPoint(
                new jsts.geom.Coordinate(event.coordinate[0], event.coordinate[1])
            );
            var jsts_feature = jstsParser.read(feature.getGeometry());
            // Create a negative 1-pixel buffer to allow for border sharing.
            var resolution = map.getView().getResolution();
            jsts_feature = jsts_feature.buffer(-resolution);
            // See if the point overlaps with the buffered feature.
            // Return the negation (false if it overlaps); true otherwise.
            // Returning false will prevent adding the point.
            var overlap = jsts_feature.contains(jsts_point);
            return !overlap;
        }
        // No overlap: add the vertex.
        return true;
    };

    // Function to return feature at click event.
    // Used by pointOverlapCheck().
    function getClickFeature(event, clickTolerance) {
        var features = map.getFeaturesAtPixel(
            event.pixel, 
            {
                // Only check the fieldsLayer for overlaps.
                layerFilter: function(layer) {
                    if (layer.getZIndex() == 101) {
                        return true;
                    }
                    return false;
                },
                hitTolerance: clickTolerance
            }
        );
        // Return the feature's starting coordinates if there's only one.
        if (features && features.length == 1) {
            return features[0];
        } else {
            if (!features) {
                console.log("getClickFeature: No feature at pixel.");
            } else {
                console.log("getClickFeature: " + features.length + " feature(s) at pixel.");
            }
            return undefined;
        }
    };

    // Function to check if specified geometry overlaps with other existing features.
    // Used in Draw tool 'finishCondition' clauses, 'modifyend' processing, and 'translateend' processing.
    function hasOverlap(geom) {
        var jsts_geom = jstsParser.read(geom);
        // Create a negative 1-pixel buffer to allow for border sharing.
        var resolution = map.getView().getResolution();
        jsts_geomBuf = jsts_geom.buffer(-resolution);
        var features = fieldsLayer.getSource().getFeatures();
        for (var i in features) {
            var feature = features[i];
            var jsts_featureGeom = jstsParser.read(feature.getGeometry());
            try {
                // Don't compare to feature being modified.
                if (jsts_geom.equals(jsts_featureGeom)) {
                    continue;
                }
                if (jsts_geomBuf.intersects(jsts_featureGeom)) {
                    console.log("hasOverlap: feature intersects.");
                    return true;
                }
            } catch (e) {
                if (e.name == "TopologyException") {
                    console.log(e.name + ": " + e.message);
                    console.log("hasOverlap: feature intersects.");
                    return true;
                } else {
                    throw e;
                }
            }
        }
        console.log("hasOverlap: feature does not intersect.");
        return false;
    };

    // Create new control bar and add it to the map.
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
    var polyGeom = undefined;
    drawBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-polygon-o" ></i>',
        title: 'Polygon creation: Click at each corner of field; press ESC key to remove most recent corner. Double-click to complete field.',
        autoActivate: true,
        interaction: new ol.interaction.Draw({
            type: 'Polygon',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            // Store the geometry being currently drawn for use by the finishCondition.
            geometryFunction: function(coords, geom) {
                polyGeom = geom;
                if (!polyGeom) {
                    polyGeom = new ol.geom.Polygon(null);
                }
                // Close the polygon each time we come through here.
                drawCoords = coords[0].slice();
                if (drawCoords.length > 0) {
                    drawCoords.push(drawCoords[0].slice());
                }
                polyGeom.setCoordinates([drawCoords]);
                return polyGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                if (hasSelfIntersection(polyGeom, false)) {
                    return false;
                }
                if (hasLastSegmentIntersection(polyGeom)) {
                    return false;
                }
                return pointOverlapCheck(event);
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            finishCondition: function(event) {
                if (hasSelfIntersection(polyGeom, true)) {
                    // Remove last point.
                    var ctrl = drawBar.getControls()[POLYGON];
                    ctrl.getInteraction().removeLastPoint();
                    return false;
                }
                if (hasOverlap(polyGeom)) {
                    // Remove last point.
                    var ctrl = drawBar.getControls()[POLYGON];
                    ctrl.getInteraction().removeLastPoint();
                    return false;
                }
                return true;
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
            })
        })
    }));
    var circleGeom = undefined;
    drawBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-circle-thin" ></i>',
        title: 'Circle creation: Click at center of field; slide mouse to expand and click when done.',
        interaction: new ol.interaction.Draw({
            type: 'Circle',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            geometryFunction: function(coords, geom) {
                func = ol.interaction.Draw.createRegularPolygon();
                circleGeom = func(coords, geom);
                return circleGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                return pointOverlapCheck(event);
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            // NOTE: Requires a specially patched version of OpenLayers v4.6.5.
            finishCondition: function(event) {
                return !hasOverlap(circleGeom);
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
            })
        })
    }));
    var rectGeom = undefined;
    drawBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-rectangle-o" ></i>',
        title: 'Rectangle creation: Click at corner of field; slide mouse to expand and click when done.',
        interaction: new ol.interaction.Draw({
            type: 'Circle',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            geometryFunction: function(coords, geom) {
                func = ol.interaction.Draw.createBox();
                rectGeom = func(coords, geom);
                return rectGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                return pointOverlapCheck(event);
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            // NOTE: Requires a specially patched version of OpenLayers v4.6.5.
            finishCondition: function(event) {
                return !hasOverlap(rectGeom);
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
            })
        })
    }));
    var squareGeom = undefined;
    drawBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-square-o" ></i>',
        title: 'Square creation: Click at center of field; slide mouse to expand and click when done.',
        interaction: new ol.interaction.Draw({
            type: 'Circle',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            geometryFunction: function(coords, geom) {
                func = ol.interaction.Draw.createRegularPolygon(4);
                squareGeom = func(coords, geom);
                return squareGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                return pointOverlapCheck(event);
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            // NOTE: Requires a specially patched version of OpenLayers v4.6.5.
            finishCondition: function(event) {
                return !hasOverlap(squareGeom);
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
            })
        })
    }));
    var holeGeom = undefined;
    drawBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-polygon-o" ></i>',
        title: 'Polygon Hole creation: Click at each corner of field; press ESC key to remove most recent corner. Double-click to complete field.',
        interaction: new ol.interaction.DrawHole({
            // Use a layer filter to select the fieldsLayer only.
            layers: function(layer) {
                if (layer.getZIndex() == 101) {
                    return true;
                }
                return false;
            },
            // Store the geometry being currently drawn for use by condition and  finishCondition.
            geometryFunction: function(coords, geom) {
                //console.log('holeGeom: ' + coords);
                holeGeom = geom;
                if (!holeGeom) {
                    holeGeom = new ol.geom.Polygon(null);
                }
                // Close the polygon each time we come through here.
                drawCoords = coords[0].slice();
                if (drawCoords.length > 0) {
                    drawCoords.push(drawCoords[0].slice());
                }
                holeGeom.setCoordinates([drawCoords]);
                return holeGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                if (hasSelfIntersection(holeGeom, false)) {
                    return false;
                }
                return true;
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            finishCondition: function(event) {
                console.log('holeGeom: finishCondition');
                return true;
                if (hasSelfIntersection(holeGeom, true)) {
                    // Remove last point.
                    var ctrl = drawBar.getControls()[HOLE];
                    ctrl.getInteraction().removeLastPoint();
                    return false;
                }
                if (hasOverlap(holeGeom)) {
                    // Remove last point.
                    var ctrl = drawBar.getControls()[HOLE];
                    ctrl.getInteraction().removeLastPoint();
                    return false;
                }
                return true;
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
            })
        })
    }));
    drawBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-bullseye" ></i>',
        title: 'Point creation: Click on map at desired location.',
        interaction: new ol.interaction.Draw({
            type: 'Point',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            // Check for feature overlap on each click.
            condition: function(event) {
                return pointOverlapCheck(event);
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

    // Remove last drawn vertex when Esc key pressed.
    document.addEventListener('keydown', function(event) {
        if (event.which == 27) {
            // Ensure that the polygon or polygon-hole drawing control is currently active.
            var ctrl = drawBar.getControls()[POLYGON];
            if (ctrl.getActive()) {
                // If so, remove its last drawn vertex.
                ctrl.getInteraction().removeLastPoint();
            }
            var ctrl = drawBar.getControls()[HOLE];
            if (ctrl.getActive()) {
                // If so, remove its last drawn vertex.
                ctrl.getInteraction().removeLastPoint();
            }
        }
    });

    // Add the new drag interaction. It will be active in edit mode only.
    // Interaction must be added before the Modify interaction below so 
    // that they will allow both editing and dragging.
    var dragInteraction = new ol.interaction.Translate({
        layers: function (layer) {
            // If it's the fieldsLayer and we are in edit mode, allow dragging.
            if (layer.getZIndex() == 101 && editButton.getActive()) {
                return true;
            }
            // Otherwise, no dragging allowed.
            return false;
        }
    });
    map.addInteraction(dragInteraction);
 
    // Prevent overlap while dragging.
    // Save the feature being dragged's initial coordinates at the start.
    var translateCoords;
    dragInteraction.on('translatestart', function(event) {
        // Save the current feature's starting coordinates.
        if (event.features.getArray().length == 1) {
            var modifyFeature = event.features.getArray()[0];
            translateCoords = modifyFeature.getGeometry().getCoordinates().slice();
            //translateCoords = [...modifyFeature.getGeometry().getCoordinates()];
            //translateCoords = new Array(modifyFeature.getGeometry().getCoordinates());
            console.log("translatestart");
            console.log(translateCoords);
        }
    });
    // At the end, compare the feature being dragged (with a 1-pixel negative buffer)
    // to all other features. If any intersect, restore the coordinates of the
    // feature being dragged to its saved starting coordinates.
    dragInteraction.on('translateend', function(event) {
        if (event.features.getArray().length == 1) {
            var modifyFeature = event.features.getArray()[0];
            console.log("translateend");
            console.log(modifyFeature.getGeometry().getCoordinates());
            // If current feature intersects with another feature,
            // restore current feature to pre-modification coordinates.
            if (hasOverlap(modifyFeature.getGeometry())) {
                modifyFeature.getGeometry().setCoordinates(translateCoords);
            }
        }
    });

    // Add edit tool.
    // NOTE: It needs to follow the Draw tools and drag interaction to ensure Modify tool processes clicks first.
    var editButton = new ol.control.Toggle({
        html: '<i class=" icon-edit" ></i>',
        title: 'To edit any mapped field, drag center of field to move it; drag any border line to stretch it; shift-click on any field corner to delete vertex.',
        interaction: new ol.interaction.Modify({
            features: fieldsLayer.getSource().getFeaturesCollection(),
            // Snap interaction is doing the heavy lifting here. So we only need a pixelTolerance
            // of 1 because 0 causes the edge detection of the modify interaction not to work.
            pixelTolerance: 1,
            // The SHIFT key must be pressed to delete vertices, so that new
            // vertices can be drawn at the same position as existing vertices.
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

    // Prevent overlap during modifications.
    // Save the feature being modified's initial coordinates at the start.
    // NOTE: Requires a specially patched version of OpenLayers v4.6.5.
    var modifyCoords;
    editButton.getInteraction().on('modifystart', function(event) {
        // Save the current feature's starting coordinates.
        if (event.features.getArray().length == 1) {
            var modifyFeature = event.features.getArray()[0];
            modifyCoords = modifyFeature.getGeometry().getCoordinates().slice();
            //modifyCoords = [...modifyFeature.getGeometry().getCoordinates()];
            //modifyCoords = new Array(modifyFeature.getGeometry().getCoordinates());
            console.log("modifystart");
        }
    });
    // At the end, compare the feature being modified (with a 1-pixel negative buffer)
    // to all other features. If any intersect, restore the coordinates of the
    // feature being modified to its saved starting coordinates.
    // NOTE: Requires a specially patched version of OpenLayers v4.6.5.
    editButton.getInteraction().on('modifyend', function(event) {
        if (event.features.getArray().length == 1) {
            var modifyFeature = event.features.getArray()[0];
            console.log("modifyend");
            // If current feature self-intersects,
            // restore current feature to pre-modification coordinates.
            if (hasSelfIntersection(modifyFeature.getGeometry(), true)) {
                modifyFeature.getGeometry().setCoordinates(modifyCoords);
                return;
            }
            // If current feature intersects with another feature,
            // restore current feature to pre-modification coordinates.
            if (hasOverlap(modifyFeature.getGeometry())) {
                modifyFeature.getGeometry().setCoordinates(modifyCoords);
                return;
            }
        }
    });

    // Add selection tool (a toggle control with a select interaction)
    var delBar = new ol.control.Bar();

    delBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-delete-o"></i>',
        title: "Click this button to delete selected mapped field(s).",
        className: "noToggle",
        onToggle: function() {
            var features = selectButton.getInteraction().getFeatures();
            if (!features.getLength()) alert("Please click on one or more mapped fields to select for deletion first.");
            for (var i=0, f; f=features.item(i); i++) {
                fieldsLayer.getSource().removeFeature(f);
            }
            // Clear all shape selections.
            selectButton.getInteraction().getFeatures().clear();

            // Hide the labeling block.
            document.getElementById("labelBlock").style.display = "none";
        }
    }));
    var selectButton = new ol.control.Toggle({
        html: '<i class="icon-select-o"></i>',
        title: "Select tool: Click a mapped field to select it for category editing or deletion. Shift-click to select multiple fields.",
        interaction: new ol.interaction.Select({
            condition: ol.events.condition.click,
            layers: [fieldsLayer]
        }),
        bar: delBar
    });
    mainbar.addControl(selectButton);

    // The snap interaction is added after the Draw and Modify interactions
    // in order for its map browser event handlers to be fired first. 
    // Its handlers are responsible of doing the snapping.
    var snapInteraction = new ol.interaction.Snap({
        source: fieldsLayer.getSource(),
        pixelTolerance: snapTolerance
    });
    map.addInteraction(snapInteraction);

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

    return [mainbar, selectButton];
};
