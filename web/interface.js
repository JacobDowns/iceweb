$(function(){

  // Handle flowline object events
  // =================================================================


  flowline.markers[0].on('editable:drawing:end', function(){
    drawFlowline(0, function(){
      flowline.markers[1].enableEdit(map).startDrawing();
    });
  });

  flowline.markers[1].on('editable:drawing:end', function(){
    drawFlowline(1, function(){
      flowline.markers[2].enableEdit(map).startDrawing();
    });
  });

  flowline.markers[2].on('editable:drawing:end', function(){
    drawFlowline(2, function(){
      plotDisabled = false;
      downloadDisabled = false;
    });
  });

  flowline.markers[0].on('editable:dragend', function(){
    flowline.lines[0].disableEdit();
    drawFlowline(0, function(){});
  });

  flowline.lines[0].on('editable:editing', function(){
    $('#chart-container').hide();
  });

  flowline.markers[1].on('editable:dragend', function(){
   flowline.lines[1].disableEdit();
    drawFlowline(1, function(){});
  });

  flowline.markers[2].on('editable:dragend', function(){
    flowline.lines[2].disableEdit();
    drawFlowline(2, function(){});
    plotDisabled = false;
  });

  for(j = 0; j < 3; j++){

    (function(_j){
      flowline.lines[_j].on('editable:vertex:ctrlclick', function(){
	flowline.lines[_j].editor.continueForward();
      });

      flowline.markers[_j].on('dblclick', L.DomEvent.stop).on('dblclick', function(){
	console.log(flowline.lines[_j]);
	flowline.lines[_j].toggleEdit();  
      });
    })(j);
    
  }


  var plotDisabled = true;
  var downloadDisabled = true;
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
          callback: loadFlowline,
          icon: 'fas fa-file-upload'
        },
        'download' : {
          name: 'Download Flowline',
          callback: downloadFlowline,
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
        },
	'data' : {
          name: 'Get Flowline Data',
          callback: getFlowline,
          icon: 'fas fa-database'
        },
      }
  });

  function resetFlowline(){
    plotDisabled = true;
    downloadDisabled = true;

    $('#chart-container').hide();

    for(i = 0; i < 3; i++){
      flowline.lines[i].disableEdit();
      flowline.markers[i].removeFrom(map);
      flowline.lines[i].setLatLngs([[]]);
    }
  }


  // Add Flowline functions
  // =================================================================

  // Create a new flowline by selecting center / shear lines
  function newFlowline(){
    resetFlowline();
    flowline.markers[0].enableEdit(map).startDrawing();
  }


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
	$('#chart-container').hide();
	callback();
    });
  }



  // Plot flowline functions
  // =================================================================

  // Plot width averaged flowline
  function plotFlowline(){

    send_data = {};
    flowline.lines[0].disableEdit();
    flowline.lines[1].disableEdit();
    flowline.lines[2].disableEdit();

    send_data.flowline_coords = {};
    send_data.flowline_coords[0] = flowline.lines[0].getLatLngs();
    send_data.flowline_coords[1] = flowline.lines[1].getLatLngs();
    send_data.flowline_coords[2] = flowline.lines[2].getLatLngs();

    $.getJSON({
      method: 'POST',
      url: "http://127.0.0.1:5000/plot_flowline",
      async: true,
      data: JSON.stringify(send_data),
      contentType: 'application/json'
    })
      .done( function(json) {
	chart.options.data[0].dataPoints = json.S;
	chart.options.data[1].dataPoints = json.B;
	chart.options.data[2].dataPoints = json.Bhat;
	chart.render();
	$('#chart-container').show();
	flowline.extension.enableEdit();
      });
  }


  // Load flowline functions
  // =================================================================

  $( "input[type='checkbox']" ).checkboxradio({
      icon: true
  });
  
  function loadFlowline(){
    loadFlowlineDialog.dialog('open');
  }

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

	  for(i = 0; i < 3; i++){
	    console.log(data['coords_y_x'][i]);
	    flowline.lines[i].setLatLngs(data['coords_y_x'][i]);

	    coordsLen = data['coords_y_x'][i].length; 
	    mid_index = Math.floor(coordsLen / 2);
            lat = data['coords_y_x'][i][mid_index][0];
            lng = data['coords_y_x'][i][mid_index][1];
            flowline.markers[i].setLatLng([lat, lng]);
            flowline.markers[i].addTo(map);

	    if(i == 0){
              lat = data['coords_y_x'][i][0][0];
              lng = data['coords_y_x'][i][0][1];
              flowline.extension.setLatLngs([[lat, lng]]);
              flowline.extension.enableEdit(map);
	    }
	  }

          flowline.markers[0].enableEdit();
          plotDisabled = false;
	}
	reader.readAsText(flowlineFile);
	loadFlowlineDialog.dialog('close');
      }
    },
    close: function() {
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
      'Download': function(){
	flowlineName = $('#input-flowline-name').val();
	dataResolution = parseFloat($('#input-data-resolution').val());

	send_data = {}
	send_data['data_resolution'] = dataResolution;
	flowline.lines[0].disableEdit();
	flowline.lines[1].disableEdit();
	flowline.lines[2].disableEdit();
	flowline.extension.disableEdit();
	send_data.flowline_coords = {}
	send_data.flowline_coords[0] = flowline.lines[0].getLatLngs()
	send_data.flowline_coords[1] = flowline.lines[1].getLatLngs()
	send_data.flowline_coords[2] = flowline.lines[2].getLatLngs()
	send_data.extension_coords = flowline.extension.getLatLngs()

	$.getJSON({
	  method: 'POST',
	  url: "http://127.0.0.1:5000/download_flowline",
	  async: true,
	  data: JSON.stringify(send_data),
	  contentType: 'application/json'
	})
	  .done( function(json) {
	    console.log(json);
	    downloadObjectAsJson(json, flowlineName);
	    downloadFlowlineDialog.dialog('close');
	  });
      }
    },
    close: function() {
    }
   });
  

  function downloadFlowline(){
    downloadFlowlineDialog.dialog('open');
  }

  function downloadObjectAsJson(exportObj, exportName){
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href",     dataStr);
    downloadAnchorNode.setAttribute("download", exportName + ".json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }


  function getFlowline(){
    send_data = {}
    send_data['data_res'] = 1.0
    send_data.coords = {}

    for(i = 0; i < 3; i++){
      flowline.lines[i].disableEdit();
      send_data.coords[i] = flowline.lines[i].getLatLngs()
    }
    $.getJSON({
      method: 'POST',
      url: "http://127.0.0.1:5000/get_flowline_data",
      async: true,
      data: JSON.stringify(send_data),
      contentType: 'application/json'
    })
      .done(function(return_data) {
	console.log(return_data);
    });
  }
});
