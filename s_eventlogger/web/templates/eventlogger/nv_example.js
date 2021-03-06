var NUM_OF_SAMPLES = 1000;
/* Inspired by Lee Byron's test data generator. */

function stream_layers(n, m, o) {
  if (arguments.length < 3) o = 0;
  function bump(a) {
    var x = 1 / (.1 + Math.random()),
        y = 2 * Math.random() - .5,
        z = 10 / (.1 + Math.random());
    for (var i = 0; i < m; i++) {
      var w = (i / m - y) * z;
      a[i] += x * Math.exp(-w * w);
    }
  }
  return d3.range(n).map(function() {
      var a = [], i;
      for (i = 0; i < m; i++) a[i] = o + o * Math.random();
      for (i = 0; i < 5; i++) bump(a);
      return a.map(stream_index);
    });
}

/* Another layer generator using gamma distributions. */
function stream_waves(n, m) {
  return d3.range(n).map(function(i) {
    return d3.range(m).map(function(j) {
        var x = 20 * j / m - i / 3;
        return 2 * x * Math.exp(-.5 * x);
      }).map(stream_index);
    });
}

var now = new Date();
var start_ts = now.getTime()-(NUM_OF_SAMPLES*1000);
console.log(now);
console.log(now.getTime())

function stream_index(d, i) {
  return {x: start_ts + i*1000, y: Math.max(0, d)};
}

var format = d3.time.format.utc.multi([
                      ["%H:%M:%S", function(d) { return d.getSeconds(); }],
                      ["%H:%M", function(d) { return d.getMinutes(); }],
                      ["%d/%m", function(d) { return d.getDay(); }],
                      ["%d/%m%Y", function() { return true; }]
                      ]);

nv.addGraph(function() {
    var chart = nv.models.lineWithFocusChart();
    //chart.brushExtent([50,70]);
    chart.xAxis.tickFormat(function(d) {
        // Will Return the date, as "%m/%d/%Y"(08/06/13)
        return format(new Date(d))
      }).axisLabel("Time");
    chart.x2Axis.tickFormat(function(d) {
      // Will Return the date, as "%m/%d/%Y"(08/06/13)
      return d3.time.format.utc("%m/%d/%y %X")(new Date(d))
    });
    chart.yTickFormat(d3.format(',.2f'));
    chart.useInteractiveGuideline(true);
    var a = testData();
    console.log(a);
    d3.select('#chart svg')
        .datum(a)
        .call(chart);
    nv.utils.windowResize(chart.update);
    return chart;
});

function testData() {
    return stream_layers(3,NUM_OF_SAMPLES,.1).map(function(data, i) {
        return {
            key: 'Stream' + i,
            area: i === 1,
            values: data
        };
    });
}
