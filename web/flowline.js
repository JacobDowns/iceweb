// Setup a flowline object
// =================================================================

var flowline = null;

$(function(){

  flowline = {};
  flowline.markers = [];
  flowline.lines = [];

  shearIcon = L.divIcon({
    iconSize: new L.Point(10, 30),
    className: 'leaflet-div-icon shear-marker'
  });
  centerIcon = L.divIcon({
    iconSize: new L.Point(10, 30),
    className: 'leaflet-div-icon center-marker'
  });

  for(i = 0; i < 3; i++){

    markerOptions = {icon: shearIcon};
    lineOptions = {color : '#0000ff'};

    if(i == 0){
      markerOptions = {icon: centerIcon};
      lineOptions = {color : '#ff0000'}
    }

    flowline.markers.push(L.marker([], markerOptions));
    flowline.lines.push(L.polyline([[]], lineOptions));
    flowline.lines[i].addTo(map);
  }

  flowline.extension = L.polyline([[]], {
    editorClass : AnchoredPolylineEditor,
    color : '#ff0000'
  });
  flowline.extension.addTo(map);
  
});
