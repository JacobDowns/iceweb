var surfaceChart = null;
var widthChart = null;

$(function(){

  // Surface elevation and bed 
  surfaceChart = new CanvasJS.Chart("surface-chart", {
    animationEnabled: false,
    theme: 'light2',
    axisY:{includeZero: false},
    width: 805,
    data: [{        
      type: "line",       
      dataPoints: []
    },{
      type : "line",
      dataPoints: []
    },{
      type : "line",
      dataPoints: []
    }]
  });

  // Width
  widthChart = new CanvasJS.Chart("width-chart", {
    animationEnabled: false,
    theme: 'light2',
    axisY:{includeZero: false},
    width: 805,
    data: [{        
      type: "line",       
      dataPoints: []
    }]
  });

  // SMB
  smbChart = new CanvasJS.Chart("smb-chart", {
    animationEnabled: false,
    theme: 'light2',
    axisY:{includeZero: false},
    width: 805,
    data: [{        
      type: "line",       
      dataPoints: []
    }]
  });

  // Temp. 
  tempChart = new CanvasJS.Chart("temp-chart", {
    animationEnabled: false,
    theme: 'light2',
    axisY:{includeZero: false},
    width: 805,
    data: [{        
      type: "line",       
      dataPoints: []
    }]
  });

  $('#chart-accordion').hide();
  $('#chart-accordion').accordion({
    collapsible:true,
    header: "h3",
    heightStyle: 'content',
    beforeActivate: function(event, ui) {
         // The accordion believes a panel is being opened
        if (ui.newHeader[0]) {
            var currHeader  = ui.newHeader;
            var currContent = currHeader.next('.ui-accordion-content');
         // The accordion believes a panel is being closed
        } else {
            var currHeader  = ui.oldHeader;
            var currContent = currHeader.next('.ui-accordion-content');
        }
         // Since we've changed the default behavior, this detects the actual status
        var isPanelSelected = currHeader.attr('aria-selected') == 'true';

         // Toggle the panel's header
        currHeader.toggleClass('ui-corner-all',isPanelSelected).toggleClass('accordion-header-active ui-state-active ui-corner-top',!isPanelSelected).attr('aria-selected',((!isPanelSelected).toString()));

        // Toggle the panel's icon
        currHeader.children('.ui-icon').toggleClass('ui-icon-triangle-1-e',isPanelSelected).toggleClass('ui-icon-triangle-1-s',!isPanelSelected);

         // Toggle the panel's content
        currContent.toggleClass('accordion-content-active',!isPanelSelected)    
        if (isPanelSelected) { currContent.slideUp(); }  else { currContent.slideDown(); }

        return false; // Cancels the default action
    }
  });

});
