// 
// *** Create control bar ***
//
function addControlBar(map, fieldsLayer, checkSaveStrategy, checkReturnStrategy, kmlName, snapTolerance) {

    // JSTS is used to prevent feature overlaps.
    var jstsParser = new jsts.io.OL3Parser();
    var geomFactory = new jsts.geom.GeometryFactory();

    // Function to return feature at click event.
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
        // Save the current feature's starting coordinates.
        if (features && features.length > 0) {
            return features[0];
        } else {
            //console.log("getClickFeature: No feature at pixel.");
            return undefined;
        }
    };

    // Function to check if specified geometry overlaps with other existing features.
    function hasOverlap(geom) {
        var jsts_geom = jstsParser.read(geom);
        // Create a negative 1-pixel buffer to allow for border sharing.
        var resolution = map.getView().getResolution();
        jsts_geomBuf = jsts_geom.buffer(-resolution);
        var features = fieldsLayer.getSource().getFeatures();
        for (var i in features) {
            var feature = features[i];
            var jsts_featureGeom = jstsParser.read(feature.getGeometry());
            // Don't compare to feature being modified.
            if (jsts_geom.equals(jsts_featureGeom)) {
                continue;
            }
            if (jsts_geomBuf.intersects(jsts_featureGeom)) {
                return true;
            }
        }
        return false;
    };

    // Draw tool 'condition' point overlap testing function.
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

    // Draw tool 'finalCondition' overlap testing function.
    function overlapCheck(event) {
        if (hasOverlap(drawGeom)) {
            // Remove last point.
            var ctrl = drawBar.getControls()[0];
            ctrl.getInteraction().removeLastPoint();
            return false;
        }
        // If we got here, there are no intersections.
        return true;
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
    var drawGeom = undefined;
    drawBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-polygon-o" ></i>',
        title: 'Polygon creation: Click at each corner of field; double-click when done.',
        autoActivate: true,
        interaction: new ol.interaction.Draw({
            type: 'Polygon',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            // Store the geometry being currently drawn for use by the finishCondition.
            geometryFunction: function(coords, geom) {
                drawGeom = geom;
                if (!drawGeom) {
                    drawGeom = new ol.geom.Polygon(null);
                }
                newCoords = coords[0].slice();
                // Close the polygon each time we come through here.
                if (newCoords.length > 0) {
                    newCoords.push(newCoords[0].slice());
                }
                drawGeom.setCoordinates([newCoords]);
                return drawGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                return pointOverlapCheck(event);
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            finishCondition: function(event) {
                return overlapCheck(event);
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
        html: '<i class="icon-circle-thin" ></i>',
        title: 'Circle creation: Click at center of field; slide mouse to expand and click when done.',
        interaction: new ol.interaction.Draw({
            type: 'Circle',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            geometryFunction: function(coords, geom) {
                func = ol.interaction.Draw.createRegularPolygon();
                drawGeom = func(coords, geom);
                return drawGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                return pointOverlapCheck(event);
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            finishCondition: function(event) {
                return overlapCheck(event);
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
    drawBar.addControl( new ol.control.Toggle({
        html: '<i class="icon-rectangle-o" ></i>',
        title: 'Rectangle creation: Click at corner of field; slide mouse to expand and click when done.',
        interaction: new ol.interaction.Draw({
            type: 'Circle',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            geometryFunction: function(coords, geom) {
                func = ol.interaction.Draw.createBox();
                drawGeom = func(coords, geom);
                return drawGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                return pointOverlapCheck(event);
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            finishCondition: function(event) {
                return overlapCheck(event);
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
        html: '<i class="icon-square-o" ></i>',
        title: 'Square creation: Click at center of field; slide mouse to expand and click when done.',
        interaction: new ol.interaction.Draw({
            type: 'Circle',
            features: fieldsLayer.getSource().getFeaturesCollection(),
            geometryFunction: function(coords, geom) {
                func = ol.interaction.Draw.createRegularPolygon(4);
                drawGeom = func(coords, geom);
                return drawGeom;
            },
            // Check for feature overlap on each click.
            condition: function(event) {
                return pointOverlapCheck(event);
            },
            // Check that currently drawn geometry doesn't overlap any previously drawn feature.
            finishCondition: function(event) {
                return overlapCheck(event);
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
            // Ensure that the polygon drawing control is currently active.
            var ctrl = drawBar.getControls()[0];
            if (ctrl.getActive()) {
                // If so, remove its last drawn vertex.
                ctrl.getInteraction().removeLastPoint();
            }
        }
    });

    // Add the new drag interaction. It will be active in edit mode.
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
 
    // Add edit tool.
    // NOTE: It needs to follow the Draw tools and drag interaction to ensure Modify tool processes clicks first.
    var editButton = new ol.control.Toggle({
        html: '<i class=" icon-edit" ></i>',
        title: 'To edit any mapped field, drag center of field to move it; drag any border line to stretch it; shift-click on any field corner to delete vertex.',
        interaction: new ol.interaction.Modify({
            features: fieldsLayer.getSource().getFeaturesCollection(),
            pixelTolerance: snapTolerance,
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

    var modifyFeature;
    var modifyCoords;
    // Prevent overlap during modifications.
    // Save the feature being modified and its starting coordinates at the start.
    editButton.getInteraction().on('modifystart', function(event) {
        // Make snapTolerance one more than the modify tool's snap tolerance to avoid 
        // boundary issues where Modify responds to click, but not getFeaturesAtPixel().
        modifyFeature = getClickFeature(event.mapBrowserEvent, snapTolerance + 1);
        // Save the current feature's starting coordinates.
        if (modifyFeature) {
            modifyCoords = modifyFeature.getGeometry().getCoordinates();
        }
    });
    // At the end, compare the feature being modified (with a 1-pixel negative buffer)
    // to all other features. If any intersect, restore the coordinates of the
    // feature being modified to its saved starting coordinates.
    editButton.getInteraction().on('modifyend', function(event) {
        if (modifyFeature) {
            // If current feature intersects with another feature,
            // restore current feature to pre-modification coordinates.
            if (hasOverlap(modifyFeature.getGeometry())) {
                if (modifyCoords.length > 0) {
                    modifyFeature.getGeometry().setCoordinates(modifyCoords);
                }
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
