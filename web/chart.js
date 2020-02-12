var chart = null;

$(function(){

  // Setup Chart
  chart = new CanvasJS.Chart("chart-container", {
    animationEnabled: false,
    theme: 'light2',
    title: {text: 'Flowline Chart'},
    axisY:{includeZero: false},
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

});
