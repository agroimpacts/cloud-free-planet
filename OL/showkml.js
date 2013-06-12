function init(kmlPath, polygonPath, noPolygonPath, kmlName, assignmentId, trainingId) {

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
    "One Square Km in South Africa", 
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

saveStrategy = new OpenLayers.Strategy.Save();
saveStrategy.events.register('success', null, function() {saveSuccess(kmlName, assignmentId, trainingId);});
saveStrategy.events.register('fail', null, function() {saveFail(kmlName, assignmentId);});
saveStrategyFailed = false;
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
    foldersName = kmlName + '__' + trainingId;
    preview = false;
// Else, if this is not an MTurk invocation, let user save changes.
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
        displayInLayerSwitcher: false
    }
);
// Special callback to catch completions after each POST to send a new polygon
// to the server. There will be only one POST in our case. This is necessary
// (instead of registering a 'fail' handler with saveStrategy) so that we can
// retrieve the HTTP status code and string.
// fieldsLayer.protocol.options.create = { callback: saveKMLFail, scope: this };
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
        trigger: function() {checkSaveStrategy(kmlName, noPolygonPath, assignmentId, trainingId);},
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

function checkSaveStrategy(kmlName, noPolygonPath, assignmentId, trainingId) {
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
                trainingId: trainingId
            },
            success: function() {notificationSuccess(kmlName, assignmentId, trainingId);},
            failure: function() {notificationFail(kmlName, assignmentId);}
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

// Report to the worker that the save was successful, and that they should complete the HIT.
function saveSuccess(kmlName, assignmentId, trainingId) {
    if (trainingId.length > 0) {
        alert('Success! Your mapped fields were saved. Click Ok to continue to next training map.');
    }
    if (assignmentId.length > 0 || trainingId.length > 0) {
        document.mturkform.save_status.value = true;
        document.mturkform.submit();
    }
}

// Report to the worker that the notification was successful, and that they should complete the HIT.
function notificationSuccess(kmlName, assignmentId, trainingId) {
    if (trainingId.length > 0) {
        alert('Success! Your notification was saved. Click Ok to continue to next training map.');
    }
    if (assignmentId.length > 0 || trainingId.length > 0) {
        document.mturkform.save_status.value = true;
        document.mturkform.submit();
    }
}

function saveFail(kmlName, assignmentId) {
    alert('Error! Your mapped fields could not be saved, but we will pay you for your effort.');
    
    if (assignmentId.length > 0) {
        document.mturkform.save_status.value = false;
        document.mturkform.submit();
    }
}

function notificationFail(kmlName, assignmentId) {
    alert('Error! Your notification could not be saved, but we will pay you for your effort.');
    
    if (assignmentId.length > 0) {
        document.mturkform.save_status.value = false;
        document.mturkform.submit();
    }
}

// Report error to the worker. If it's a bad KML error, let him try to remap once more time.
// *** Not currently used, since we no longer need to examine each http request's details. ***
function saveKMLFail(response) {
    // If no error, let the Save Strategy's 'success' callback deal with this.
    if (response.code == OpenLayers.Protocol.Response.SUCCESS) {
        return;
    }
    errCode = response.priv.status;
    errText = response.priv.statusText;
    if (errText == 'Bad KML' && ! saveStrategyFailed) {
        alert('We\'re sorry, but through no fault of your own, we were unable to save the maps you drew.\nWe now have to erase these maps and ask that to draw them again.\nWe apologize for the inconvenience!');
        saveStrategyFailed = true
        fieldsLayer.removeAllFeatures();
        saveStrategyActive = true;
        
    } else {
        alert('Error! Your changes could not be saved, but we will pay you for your effort.');
        if (assignmentId.length > 0) {
            document.mturkform.save_status.value = false;
            document.mturkform.submit();
        }
    }
}
