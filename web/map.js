var map = null;
var AnchoredPolylineEditor = null;

$(function(){

  proj4.defs("EPSG:3413","+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs");

  AnchoredPolylineEditor = L.Editable.PolylineEditor.extend({
    addVertexMarker: function (latlng, latlngs, opts) {
      return new this.tools.options.vertexMarkerClass(latlng, latlngs, this, opts || {});
    },
    addVertexMarkers: function (latlngs) {
      for (var i = 0, l = latlngs.length; i < l; i++) {
        this.addVertexMarker(latlngs[i], latlngs, {
          draggable: (i>0)  && (i<l-1)
        });
      }
    }
  });

  // Setup Map 
  map = L.map('map', {
    crs: L.CRS.Simple,
    minZoom: -3,
    editable : true,
    editOptions : {'skipMiddleMarkers' : true}
  });


  // Add layers with different data sets
  bounds = [[0, 0], [2691.0, 1502.1]];
  image1 = L.imageOverlay('/home/jake/web_data/web/images/velocity.png', bounds).addTo(map);
  image2 = L.imageOverlay('/home/jake/web_data/web/images/bed.png', bounds).addTo(map);
  image3 = L.imageOverlay('/home/jake/web_data/web/images/surface.png', bounds).addTo(map);
  image4 = L.imageOverlay('/home/jake/web_data/web/images/thickness.png', bounds).addTo(map);
  map.setView([1350, 700], -2);

  baseMaps = {
    'Bed': image2,
    'Surface': image3,
    'Thickness' : image4,
    'Velocity': image1
  };

  L.control.layers(baseMaps).addTo(map);

  
  // Flowline menu button
  // =================================================================
  L.FlowControl = L.Control.extend({
    options: {
      position: 'bottomleft',
    },
    onAdd: function (map) {
      //container = L.DomUtil.create('i', 'leaflet-control leaflet-bar flow-control');
      //container.innerHTML = 'Menu'
      //return container;
      container = L.DomUtil.create('div', 'leaflet-control leaflet-bar menu-control');
      container.id = 'menu-div';
      L.DomUtil.create('i', 'context-menu fas fa-bars fa-2x', container);
      return container;
    }
  });

  map.addControl(new L.FlowControl());
  
});
