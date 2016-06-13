function init(kmlPath, polygonPath, noPolygonPath, kmlName, assignmentId, trainingId, tryNum, mapPath, workerId) {

// Constants defining status returned for a training map with a low score.
lowScoreCode = 460;
lowScoreText = "Low Score";

// Create the map using the specified DOM element
var map = new OpenLayers.Map("kml_display");

var satellite = new OpenLayers.Layer.Google(
    "Google Satellite", 
    {
        type: google.maps.MapTypeId.SATELLITE, 
        minZoomLevel: 14,
        maxZoomLevel: 18
    }
);
var hybrid = new OpenLayers.Layer.Google(
    "Google Hybrid", 
    {
        type: google.maps.MapTypeId.HYBRID,
        minZoomLevel: 14,
        maxZoomLevel: 18
    }
);
var streets = new OpenLayers.Layer.Google(
    "Google Streets", 
    {
        minZoomLevel: 14,
        maxZoomLevel: 18
    }
);
map.addLayers([satellite, hybrid, streets]);

var sty = new OpenLayers.Style({
    strokeColor: "white", 
    strokeOpacity: 1.0, 
    strokeWidth: 2, 
    fillOpacity: 0.0
});
var stymap = new OpenLayers.StyleMap({ 'default': sty });
kmlLayer = new OpenLayers.Layer.Vector(
    "One Square Km in Africa", 
    {
        styleMap: stymap,
        protocol: new OpenLayers.Protocol.HTTP({
                url: kmlPath + '/' + kmlName + '.kml',
                format: new OpenLayers.Format.KML()
        }),
        strategies: [new OpenLayers.Strategy.Fixed()],
        displayInLayerSwitcher: false
    }
)
map.addLayer(kmlLayer);

// If this is a worker-feedback map, create two additional layers.
if (assignmentId.length == 0 && workerId.length > 0) {
    rMapLayer = new OpenLayers.Layer.Vector(
        "Reference Map", 
        {
            protocol: new OpenLayers.Protocol.HTTP({
                    url: mapPath + '/' + workerId + '/' + kmlName + '_r.kml',
                    format: new OpenLayers.Format.KML()
            }),
            strategies: [new OpenLayers.Strategy.Fixed()],
            displayInLayerSwitcher: true
        }
    )
    map.addLayer(rMapLayer);

    var wSty = new OpenLayers.Style({
        fillColor: "blue",
        fillOpacity: 0.2,
        strokeOpacity: 0.0
    });
    var wStymap = new OpenLayers.StyleMap({ 'default': wSty });
    wMapLayer = new OpenLayers.Layer.Vector(
        "Worker Map", 
        {
            styleMap: wStymap,
            protocol: new OpenLayers.Protocol.HTTP({
                    url: mapPath + '/' + workerId + '/' + kmlName + '_w.kml',
                    format: new OpenLayers.Format.KML()
            }),
            strategies: [new OpenLayers.Strategy.Fixed()],
            displayInLayerSwitcher: true
        }
    )
    map.addLayer(wMapLayer);
}

saveStrategy = new OpenLayers.Strategy.Save();

if (assignmentId.length > 0) {
    // If this is an MTurk accepted HIT, let user save changes, 
    // and add assignment ID to kml name.
    if (assignmentId != 'ASSIGNMENT_ID_NOT_AVAILABLE') {
        saveStrategyActive = true;
        foldersName = kmlName + '_' + assignmentId;
        preview = false;
    } else {
        // Else, if this is an MTurk preview, don't let user save changes.
        saveStrategyActive = false;
        foldersName = kmlName;
        preview = true;
    }
// If this is a training map, let user save changes, and add training ID to kml name.
} else if (trainingId.length > 0) {
    saveStrategyActive = true;
    // Note: double underscore below.
    foldersName = kmlName + '__' + trainingId + '_' + tryNum;
    preview = false;
// If this is a worker-feedback map, don't let the user save maps.
} else if (assignmentId.length == 0 && workerId.length > 0) {
    saveStrategyActive = false;
    foldersName = kmlName;
    preview = true;
// Else, if this is a standalone invocation, let user save changes.
} else {
    saveStrategyActive = true;
    foldersName = kmlName;
    preview = false;
}

fieldsLayer = new OpenLayers.Layer.Vector(
    "Mapped Fields",
    {
        protocol: new OpenLayers.Protocol.HTTP({
            url: polygonPath,
            format: new OpenLayers.Format.KML({
                foldersName: foldersName
            })
        }),
        strategies: [saveStrategy],
        displayInLayerSwitcher: true
    }
);
// Special callback to catch completions after each POST to send a new polygon
// to the server. There will be only one POST in our case. This is necessary
// (instead of registering 'success' and 'fail' handlers with saveStrategy) 
// so that we can retrieve the HTTP status code and string.
// NOTE: 'response' argument in passed by low-level callback code.
fieldsLayer.protocol.options.create = { callback: function(response) {saveKMLStatus(response, assignmentId, trainingId);} };
map.addLayer(fieldsLayer);

var layerSwitcher = new OpenLayers.Control.LayerSwitcher({ roundedCorner:true });
map.addControl(new OpenLayers.Control.LayerSwitcher());
var panZoomBar = new OpenLayers.Control.PanZoomBar();
var mousePosition = new OpenLayers.Control.MousePosition({
    'displayProjection': 'EPSG:4326',
    'numDigits': 3
});
var scaleline = new OpenLayers.Control.ScaleLine();
map.addControls([layerSwitcher, panZoomBar, mousePosition, scaleline]);
if (assignmentId.length == 0 && workerId.length > 0) {
    layerSwitcher.maximizeControl();
}

var DeleteFeature = OpenLayers.Class(OpenLayers.Control, {
    initialize: function(layer, options) {
        OpenLayers.Control.prototype.initialize.apply(this, [options]);
        this.layer = layer;
        this.handler = new OpenLayers.Handler.Feature(
            this, layer, {click: this.clickFeature}
        );
    },
    clickFeature: function(feature) {
        // if feature doesn't have a fid, destroy it
        if(feature.fid == undefined) {
            this.layer.destroyFeatures([feature]);
        } else {
            feature.state = OpenLayers.State.DELETE;
            this.layer.events.triggerEvent("afterfeaturemodified", {feature: feature});
            feature.renderIntent = "select";
            this.layer.drawFeature(feature);
        }
    },
    setMap: function(map) {
        this.handler.setMap(map);
        OpenLayers.Control.prototype.setMap.apply(this, arguments);
    },
    CLASS_NAME: "OpenLayers.Control.DeleteFeature"
});
var panelControl1, panelControl2, panelControl3;
if (preview) {
    panelControl1 = new OpenLayers.Control.Button({
        displayClass: 'olControlDeleteFeature',
        title: '*** Disabled in preview mode *** Delete mapped field: Click on tool. Click on mapped field to delete.'
    });
    panelControl2 = new OpenLayers.Control.Button({
        displayClass: 'olControlDrawFeaturePoint',
        title: '*** Disabled in preview mode *** Edit mapped field: Click on tool. Click on mapped field to select. Drag any circle to reshape mapped field. Hover over a circled corner and press the \'d\' key to remove it. Click anywhere when done.'
    });
    panelControl3 = new OpenLayers.Control.Button({
        displayClass: 'olControlDrawFeaturePolygon',
        title: '*** Disabled in preview mode *** Create mapped field: Click on tool. Click on map at each corner to be created. Double-click when done.'
    });
    panelControl4 = new OpenLayers.Control.Button({
        displayClass: 'saveButton',
        title: '*** Disabled in preview mode *** Save changes: Click on this button only ONCE when all mapped fields have been created, and you are satisfied with your work. Click when done even if there are NO fields to draw on this map.'
    });
} else {
    panelControl1 = new DeleteFeature(
        fieldsLayer,
        {
            displayClass: 'olControlDeleteFeature',
            title: 'Delete mapped field: Click on tool. Click on mapped field to delete.'
        }
    );
    panelControl2 = new OpenLayers.Control.ModifyFeature(
        fieldsLayer,
        {
            // Consider 'd'  and the PC delete key (46) as the only delete codes.
            // Ideally, we'd like to consider the backspace (8) key as well, 
            // since the delete key on the Mac is the keycode for backspace. But trapping 
            // backspace deletes the vertex *and* still triggers the browser Back button.
            // So better to avoid it unless we can disable its action as a Back button.
            deleteCodes: [68, 46],
            displayClass: 'olControlDrawFeaturePoint',
            title: 'Edit mapped field: Click on tool. Click on mapped field to select. Drag any circle to reshape mapped field. Hover over a circled corner and press the \'d\' key to remove it. Click anywhere when done.'
        }
    );
    panelControl3 = new OpenLayers.Control.DrawFeature(
        fieldsLayer,
        OpenLayers.Handler.Polygon,
        {
            displayClass: 'olControlDrawFeaturePolygon',
            title: 'Create mapped field: Click on tool. Click on map at each corner to be created. Double-click when done.'
        }
    );
    panelControl4 = new OpenLayers.Control.Button({
        displayClass: 'saveButton',
        trigger: function() {checkSaveStrategy(kmlName, noPolygonPath, assignmentId, trainingId, tryNum);},
        title: 'Save changes: Click on this button only ONCE when all mapped fields have been created, and you are satisfied with your work. Click when done even if there are NO fields to draw on this map.'
    });
}
panelControls = [
    new OpenLayers.Control.Navigation({ title: 'Navigate' }),
    panelControl1,
    panelControl2,
    panelControl3,
    panelControl4
];
var editingToolbarControl = new OpenLayers.Control.Panel({
    displayClass: 'olControlEditingToolbar',
    defaultControl: panelControls[0]
});
editingToolbarControl.addControls(panelControls);
map.addControl(editingToolbarControl);

kmlLayer.events.register("loadend", kmlLayer, function() {
    map.zoomToExtent(kmlLayer.getDataExtent());
});

}

function checkSaveStrategy(kmlName, noPolygonPath, assignmentId, trainingId, tryNum) {
    var msg;
    if (!saveStrategyActive) {
        return;
    }
    if (fieldsLayer.features != '') {
        msg = 'You can only save your mapped fields ONCE!\nPlease confirm that you\'re COMPLETELY done mapping fields.\nIf not done, click Cancel.';
    } else {
        msg = 'You have not mapped any fields!\nYou can only save your mapped fields ONCE!\nPlease confirm that you\'re COMPLETELY done mapping fields.\nIf not done, click Cancel.'
    }
    if (!confirm(msg)) {
        return;
    }
    // Save the current polygons if there are any.
    if (fieldsLayer.features != '') {
        var i = 1;
        for (var feature in fieldsLayer.features) {
            fieldsLayer.features[feature].attributes.name = kmlName + '_' + i;
            i = i + 1;
        }
        saveStrategy.save();
    } else {
        var request = OpenLayers.Request.PUT({
            url: noPolygonPath,
            params: {
                kmlName: kmlName,
                assignmentId: assignmentId,
                trainingId: trainingId,
                tryNum: tryNum
            },
            // Special callback to catch the completion after the PUT to notification
            // to the server. This is necessary (instead of registering 'success' and 
            // 'failure' handlers above) so that we can retrieve the HTTP status code 
            // and string.
            callback: function() {notificationStatus(request, assignmentId, trainingId);}
        });
    }
    // Don't allow Save button to be used again.
    saveStrategyActive = false
    // Set the active control to be Navigation.
    for(var i=1, len=panelControls.length; i<len; i++) {
        panelControls[i].deactivate();
    }
    panelControls[0].activate();
}

// Report polygon status to the worker. 
// If it's for a training map with a low score, let him try to remap again.
function saveKMLStatus(response, assignmentId, trainingId) {
    statusCode = response.priv.status;
    statusText = response.priv.statusText;

    // Save the status code in the MTurk HTML form.
    document.mturkform.save_status_code.value = statusCode;

    // Training case.
    if (trainingId.length > 0) {
        if (statusCode >= 200 && statusCode < 300) {
            alert("Congratulations! You successfully mapped the crop fields in this map. Please click Ok to move on to the next training map.");
        } else if (statusCode == lowScoreCode || statusText == lowScoreText) {
            alert("We're sorry, but you failed to correctly map the crop fields in this map. Please click Ok to try again.");
        } else {
            // alert("statusCode: " + statusCode + "; statusText: '" + statusText + "'");
            alert("Error! Your work could not be saved. The Mapping Africa server may be down for maintenance, but you will be paid for your time when it is available again. Please try again later. We apologize for the inconvenience.");
        }
    // HIT and stand-alone cases.
    } else if (! (statusCode >= 200 && statusCode < 300)) {
        alert("Error! Your work could not be saved. The Mapping Africa server may be down for maintenance. Please try again later. We apologize for the inconvenience.");
    }
    if (assignmentId.length > 0 || trainingId.length > 0) {
        document.mturkform.submit();
    }
}

// Report notification status to the worker. 
// If it's for a training map with a low score, let him try to remap once more time.
function notificationStatus(request, assignmentId, trainingId) {
    statusCode = request.status;
    statusText = request.statusText;

    // Save the status code in the MTurk HTML form.
    document.mturkform.save_status_code.value = statusCode;

    // Training case.
    if (trainingId.length > 0) {
        if (statusCode >= 200 && statusCode < 300) {
            alert("Congratulations! You successfully reported the absence of crop fields in this map. Please click Ok to move on to the next training map.");
        } else if (statusCode == lowScoreCode || statusText == lowScoreText) {
            alert("We're sorry, but you failed to map the crop fields in this map. Please click Ok to try again.");
        } else {
            // alert("statusCode: " + statusCode + "; statusText: '" + statusText + "'");
            alert("Error! Your work could not be saved. The Mapping Africa server may be down for maintenance, but you will be paid for your time when it is available again. Please try again later. We apologize for the inconvenience.");
        }
        
    // HIT and stand-alone cases.
    } else if (! (statusCode >= 200 && statusCode < 300)) {
        alert("Error! Your work could not be saved. The Mapping Africa server may be down for maintenance. Please try again later. We apologize for the inconvenience.");
    }
    if (assignmentId.length > 0 || trainingId.length > 0) {
        document.mturkform.submit();
    }
}
