var map = L.map('map', {
    crs: L.CRS.Simple,
    minZoom: -3
});

var yx = L.latLng;

var xy = function(x, y) {
    if (L.Util.isArray(x)) {    // When doing xy([x, y]);
	return yx(x[1], x[0]);
    }
    return yx(y, x);  // When doing xy(x, y);
};

var bounds = [xy(0, 0), xy(1502.1, 2691.0)];
var image1 = L.imageOverlay('/home/jake/web_data/web/images/velocity.png', bounds).addTo(map);
var image2 = L.imageOverlay('/home/jake/web_data/web/images/bed.png', bounds).addTo(map);
var image3 = L.imageOverlay('/home/jake/web_data/web/images/surface.png', bounds).addTo(map);
map.setView(xy(700, 1350), -2);

var baseMaps = {
"Velocity": image1,
"Bed": image2,
"Surface": image3
};

L.control.layers(baseMaps).addTo(map);
var flowlineControl = L.control.layers()
console.log(flowlineControl);

var flowlineCount = 0
var overlays = {}
var activeFlowline = null;


var polylineOptions = {
  maxMarkers: 1000
}

var chart = new CanvasJS.Chart("chartContainer", {
	animationEnabled: false,
	theme: "light2",
	title:{
		text: "Simple Line Chart"
	},
	axisY:{
		includeZero: false
	},
	data: [{        
		type: "line",       
		dataPoints: []
	},
	{
	    type : "line",
	    dataPoints: []
	}]
});
chart.render();


function onMapClick(e){
    coords = {'x' : e.latlng.lng, 'y' : e.latlng.lat};
    console.log(coords);
    
    jQuery.when(
    $.getJSON({
	method: 'POST',
	url: "http://127.0.0.1:5000/map_click",
	async: true,
	data: JSON.stringify(coords),
	contentType: 'application/json' 
    })
    ).done( function(json) {	
	if(flowlineCount == 0){
	    activeFlowline = L.Polyline.PolylineEditor(json.flowline_coords, polylineOptions).addTo(map);
	    overlays['Flowline ' + flowlineCount.toString()] = activeFlowline;
	}
	else{
	    for(k in overlays){
		console.log(k);
		map.removeLayer(overlays[k]);
	    }

	    map.removeControl(flowlineControl);
	    polyline = L.Polyline.PolylineEditor(json.flowline_coords, polylineOptions);
	    overlays['Flowline ' + flowlineCount.toString()] = polyline;
	    flowlineControl = L.control.layers(overlays).addTo(map);
	    map.addLayer(polyline);
	    activeFlowline = polyline;
	}

	flowlineCount ++;
   });
}

function onKeyPress(e){

    // Update charts
    if(e.originalEvent.key == 'Enter' && flowlineCount > 0){
	$.getJSON({
	method: 'POST',
	url: "http://127.0.0.1:5000/get_data",
	async: true,
	data: JSON.stringify(activeFlowline._latlngs),
	contentType: 'application/json' 
	})
	.done( function(json) {	
	console.log(json);
	})
    }
}	


map.on('dblclick', onMapClick);
map.on('keypress', onKeyPress);

