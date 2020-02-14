$(function(){

  // Handle flowline object events
  // =================================================================

  for(j = 0; j < 3; j++){
    (function(_j){
      // Flowline marker placement
      flowline.markers[_j].on('editable:drawing:end', function(){
	drawFlowline(_j, function(){
	  if(_j < 2){
	    flowline.markers[_j + 1].enableEdit(map).startDrawing();
	  }
	  else{
	    plotDisabled = false;
	    downloadDisabled = false;
	  }
	});
      });

      // Marker drag end event
      flowline.markers[_j].on('editable:dragend', function(){
	flowline.lines[_j].disableEdit();
	drawFlowline(_j, function(){});
      });

      // Ctrl click vertex to continue flowline
      flowline.lines[_j].on('editable:vertex:ctrlclick', function(){
	flowline.lines[_j].editor.continueForward();
      });

      // Double click flowline marker to edit flowline
      flowline.lines[_j].on('dblclick', L.DomEvent.stop).on('dblclick', function(){
	flowline.lines[_j].toggleEdit();
      });

      // Any flowline edit
      flowline.lines[_j].on('editable:editing', function(){
	$('#chart-accordion').hide();
      });
    })(j);
  }


  // Flowline state functions and variables
  // =================================================================
  
  var plotDisabled = true;
  var downloadDisabled = true;
  
  function resetFlowline(){
    plotDisabled = true;
    downloadDisabled = true;
    $('#chart-accordion').hide();
    for(i = 0; i < 3; i++){
      flowline.lines[i].disableEdit();
      flowline.markers[i].removeFrom(map);
      flowline.lines[i].setLatLngs([[]]);
    }
  }

  // Create a new flowline by selecting center / shear lines
  function newFlowline(){
    resetFlowline();
    flowline.markers[0].enableEdit(map).startDrawing();
  }


  // Gets data (bed, velocity, width) etc. for the flowline
  function getFlowlineData(){
    send_data = {}
    send_data['data_res'] = 1.0
    send_data.coords = {}

    for(i = 0; i < 3; i++){
      flowline.lines[i].disableEdit();
      send_data.coords[i] = flowline.lines[i].getLatLngs()
    }

    return new Promise(resolve => {
      $.getJSON({
        method: 'POST',
        url: "http://127.0.0.1:5000/get_flowline_data",
        async: true,
        data: JSON.stringify(send_data),
        contentType: 'application/json'
      }).done(function(return_data) {
        console.log(return_data);
	resolve(return_data);
      });
    });
  }


  // Context menu
  // =================================================================
  
  menu = $.contextMenu({
    selector: '#menu-div',
    trigger: 'left',
    callback: function(key, options) {
      var m = "clicked: " + key;
      window.console && console.log(m) || alert(m);
    },
    items: {
      'new': {
        name: 'New Flowline',
        callback: newFlowline,
        icon: 'fas fa-slash'
      },
      'load': {
        name: 'Load Flowline',
        callback: function(){
	  loadFlowlineDialog.dialog('open');
	},
        icon: 'fas fa-file-upload'
      },
      'download' : {
        name: 'Download Flowline',
        callback: function(){
	  downloadFlowlineDialog.dialog('open');
	},
        disabled: function(key, opt) {
          return downloadDisabled;
        },
        icon: 'fas fa-file-download'
      },
      'plot' : {
        name: 'Plot Flowline',
        callback: plotFlowline,
        disabled: function(key, opt) {
          return plotDisabled;
        },
        icon: 'fas fa-chart-line'
      }
    }
  });


  // Add Flowline functions
  // =================================================================


  // Draw a flowline
  function drawFlowline(index, callback){

    x = flowline.markers[index].getLatLng().lng;
    y = flowline.markers[index].getLatLng().lat;
    send_data = {'x' : [x], 'y' : [y]};

    // Do ajax request to get flowlines
    $.getJSON({
      method: 'POST',
      url: "http://127.0.0.1:5000/get_flowline",
      async: true,
      data: JSON.stringify(send_data),
      contentType: 'application/json'
    })
      .done( function(json) {
	flowline.lines[index].disableEdit(map);
	flowline.lines[index].setLatLngs(json[0]);
	$('#chart-accordion').hide();
	callback();
      });
  }



  // Plot flowline functions
  // =================================================================

  // Plot width averaged flowline
  function plotFlowline(){

    send_data = {}
    send_data['data_res'] = 1.0
    send_data.coords = {}

    for(i = 0; i < 3; i++){
      flowline.lines[i].disableEdit();
      send_data.coords[i] = flowline.lines[i].getLatLngs()
    }

    $.getJSON({
      method: 'POST',
      url: "http://127.0.0.1:5000/plot_flowline",
      async: true,
      data: JSON.stringify(send_data),
      contentType: 'application/json'
    })
      .done( function(json) {
	console.log(json);
	surfaceChart.options.data[0].dataPoints = json.bed;
	surfaceChart.options.data[1].dataPoints = json.bhat;
	surfaceChart.options.data[2].dataPoints = json.surface;
	surfaceChart.render();
	widthChart.options.data[0].dataPoints = json.width;
	widthChart.render();
	smbChart.options.data[0].dataPoints = json.smb;
	smbChart.render();
	tempChart.options.data[0].dataPoints = json.t2m;
	tempChart.render();
	$('#chart-accordion').show();
	//flowline.extension.enableEdit();
      });
  }


  // Load flowline functions
  // =================================================================

  var flowlineFile = null;
  $('#flowline-coords-file').change(function(e){
    flowlineFile = e.target.files[0];
  });

  loadFlowlineDialog = $('#load-flowline-dialog').dialog({
    autoOpen: false,
    height: 300,
    width: 400,
    modal: true,
    buttons: {
      'Load': function(){
	reader = new FileReader();
	reader.onload = function(event){
	  text = event.target.result;
	  data = JSON.parse(text);
          resetFlowline();
	  console.log(data);

	  for(i = 0; i < 3; i++){
	    console.log(data['coords_y_x'][i]);
	    flowline.lines[i].setLatLngs(data['coords_y_x'][i]);

	    coordsLen = data['coords_y_x'][i].length;
	    mid_index = Math.floor(coordsLen / 2);
	    lat = data['coords_y_x'][i][mid_index][0];
	    lng = data['coords_y_x'][i][mid_index][1];
	    flowline.markers[i].setLatLng([lat, lng]);
	    flowline.markers[i].addTo(map);
	    flowline.markers[i].enableEdit();
	  }

	  coordsLen = data['coords_y_x'][0].length;
	  mid_index = Math.floor(coordsLen / 2);
	  lat = data['coords_y_x'][0][mid_index][0];
	  lng = data['coords_y_x'][0][mid_index][1];
	  map.flyTo(new L.LatLng(lat, lng), 0.8);
          plotDisabled = false;
	  downloadDisabled = false;
	}
	reader.readAsText(flowlineFile);
	loadFlowlineDialog.dialog('close');
      }
    }
  });


  // Download flowline
  // =================================================================

  downloadFlowlineDialog = $('#download-flowline-dialog').dialog({
    autoOpen: false,
    height: 300,
    width: 400,
    modal: true,
    buttons: {
      'Download': async function(){
	flowlineName = $('#input-flowline-name').val();
	dataResolution = parseFloat($('#input-data-resolution').val());
        return_data = await getFlowlineData();
        console.log(return_data);
        downloadObjectAsJson(return_data, flowlineName);
        downloadFlowlineDialog.dialog('close');
      }
    }
  });

  // Downloads a json object exporObj and saves as exportName
  function downloadObjectAsJson(exportObj, exportName){
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href",     dataStr);
    downloadAnchorNode.setAttribute("download", exportName + ".json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }
  
});
