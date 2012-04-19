$script(['/static/js/jquery.js'], 'jquery');
$script(['/static/js/raphael.min.js', '/static/js/kartograph.min.js', '/static/js/chroma.min.js', '/static/js/qtip.min.js'], 'kartograph');

$script.ready(['kartograph'], function() {
   $(function() {
      var map,
         colorscale,
         dep_data,
         w = $('#map').parent().width();

      $.ajax({
         url: '/quotes/'+topicid,
         dataType: 'json',
         success: function(data) {
            dep_data = data;
            drawSources();
            redrawMeasures();
            map = $K.map('#map', w, w);
            map.loadMap('/static/world.svg', function() {
               map.loadStyles('/static/css/svg-styles.css', function() {
                  map.addLayer({
                     id: 'regions',
                     tooltip: {
                        content: function(obj,foo) {
                           return foo.data.name;
                        }
                     },
                     key: 'id'
                  });
                  updateMap();
               })
            });
         }
      });

      function drawSources() {
         var parent=$('#sources');
         parent.empty();
         var first=true;
         for(var i in dep_data) {
            var tmp='';
            if(first) {
              tmp=' btn-primary';
              first=false;
            }
            parent.append('<a class="source btn'+tmp+'" data-value="'+i+'">'+i+'</a>')
         }
      }

      function redrawMeasures() {
         var data=dep_data[$('.source.btn-primary').data('value')];
         var parent=$('#measures');
         parent.empty();
         var first=true;
         for(var i in data[0]) {
            if(i=='id') continue;
            var tmp='';
            if(first) {
              tmp=' btn-primary';
              first=false;
            }
            parent.append('<a class="measure btn'+tmp+'" data-value="'+i+'">'+i+'</a>')
         }
         // init user interface
         $('.btn').click(buttonClick);
      }
      /*
       * update map colors
       */
      function buttonClick(event) {
         var tgt = $(event.target), par = tgt.parent();
         $('.btn', par).removeClass('btn-primary');
         tgt.addClass('btn-primary');
         if(tgt.hasClass('source')) {
            redrawMeasures();
         }
         updateMap();
      }

      function updateMap() {
         var prop = $('.measure.btn-primary').data('value'),
            scale = 'q';

         colorscale = new chroma.ColorScale({
            colors: chroma.brewer.YlGnBu,
            limits: chroma.limits(dep_data[$('.source.btn-primary').data('value')], 'c', 4, prop)
         });

         map.choropleth({
            data: dep_data[$('.source.btn-primary').data('value')],
            key: 'id',
            colors: function(d) {
               if (d == null) return '#fff';
               return colorscale.getColor(d[prop]);
            },
            duration: 0
         });

      }
   });
});