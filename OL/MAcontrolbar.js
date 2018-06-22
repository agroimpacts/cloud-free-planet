// 
// *** Create control bar ***
//
function addControlBar(fieldsLayer, workerMap, checkSaveStrategy, checkReturnStrategy, kmlName) {
    var mainbar = new ol.control.Bar({
        autoDeactivate: true,   // deactivate controls in bar when parent control off
        toggleOne: true,	    // one control active at the same time
        group: false	        // group controls together
    });
    mainbar.setPosition("top-right");

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
            features: workerMap,
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
            features: workerMap,
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
        html: '<i class="icon-bullseye" ></i>',
        title: 'Point creation: Click on map at desired location.',
        interaction: new ol.interaction.Draw({
            type: 'Point',
            features: workerMap,
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
            features: workerMap,
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
            features: workerMap,
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

    // Need the following  to be last to ensure Modify tool processes clicks before Draw tool.
    // Add edit tool.
    var editButton = new ol.control.Toggle({
        html: '<i class=" icon-edit" ></i>',
        title: 'To edit any mapped field, drag center of field to move it; drag any border line to stretch it; shift-click on any field corner to delete vertex.',
        interaction: new ol.interaction.Modify({
            features: workerMap,
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
        title: "Select tool: Click a mapped field to select for deletion. Shift-click to select multiple fields.",
        interaction: new ol.interaction.Select({
            condition: ol.events.condition.click,
            layers: [fieldsLayer]
        }),
        bar: delBar
    });
    mainbar.addControl(selectButton);

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
