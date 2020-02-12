$(function(){

  // Handle flowline object events
  // =================================================================

  function endFirstFlowline(){
    flowline.extension.disableEdit(map);
    index = flowline.lines[0].getLatLngs().length - 1;
    lat = flowline.lines[0].getLatLngs()[index].lat;
    lng = flowline.lines[0].getLatLngs()[index].lng;
    flowline.extension.setLatLngs([[lat, lng]]);
    flowline.extension.enableEdit(map);
  }

  flowline.markers[0].on('editable:drawing:end', function(){
    drawFlowline(0, function(){
      endFirstFlowline();
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
    drawFlowline(0, function(){
      endFirstFlowline();
    });
  });

  flowline.lines[0].on('editable:editing', function(){
    $('#chart-container').hide();
    endFirstFlowline();
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

  flowline.extension.on('editable:vertex:ctrlclick', function(){
    flowline.extension.editor.continueForward();
  });

  flowline.extension.on('editable:editing', function(){
    $('#chart-container').hide();
  });

  flowline.markers[0].on('dblclick', L.DomEvent.stop).on('dblclick', function(){
    flowline.extension.toggleEdit();
    flowline.lines[0].toggleEdit();
  });

  flowline.markers[1].on('dblclick', L.DomEvent.stop).on('dblclick', function(){
    flowline.lines[1].toggleEdit();
  });

  flowline.markers[2].on('dblclick', L.DomEvent.stop).on('dblclick', function(){
    flowline.lines[2].toggleEdit();
  });


  var plotDisabled = true;
  var downloadDisabled = true;
  menu = $.contextMenu({
      selector: '.context-menu',
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

    flowline.extension.disableEdit();
    flowline.extension.setLatLngs([[]]);
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

    send_data = {}
    flowline.lines[0].disableEdit();
    flowline.lines[1].disableEdit();
    flowline.lines[2].disableEdit();
    flowline.extension.disableEdit();
    send_data.flowline_coords = {}
    send_data.flowline_coords[0] = flowline.lines[0].getLatLngs()
    send_data.flowline_coords[1] = flowline.lines[1].getLatLngs()
    send_data.flowline_coords[2] = flowline.lines[2].getLatLngs()
    send_data.extension_coords = flowline.extension.getLatLngs()
    console.log(send_data);

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

	sendData = {}
	sendData.file = JSON.parse(text);
	sendData.extend_down = $('#checkbox-extend-down').prop('checked');
	sendData.extend_up = $('#checkbox-extend-up').prop('checked');
	  
	$.getJSON({
          method: 'POST',
          url: "http://127.0.0.1:5000/load_flowline",
          async: true,
          data: JSON.stringify(sendData),
          contentType: 'application/json'
	})
        .done( function(json) {
          resetFlowline();
          flowline.lines[0].disableEdit(map);
          flowline.lines[0].setLatLngs(json[0]);

          flowline.extension.disableEdit(map);
          index = json[0].length - 1;
          lat = json[0][index][0];
          lng = json[0][index][1];
          flowline.extension.setLatLngs([[lat, lng]]);
          flowline.extension.enableEdit(map);

          mid_index = Math.floor(json[0].length / 2);
          lat1 = json[0][mid_index][0]
          lng1 = json[0][mid_index][1]
          flowline.markers[0].setLatLng([lat1, lng1]);
          flowline.markers[0].addTo(map);

          flowline.markers[0].enableEdit();
          flowline.markers[1].enableEdit(map).startDrawing();
          plotDisabled = false;
	  console.log(json);
        });
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
  
});
