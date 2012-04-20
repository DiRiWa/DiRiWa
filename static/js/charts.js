Array.prototype.sum = function(){
   for(var i=0,sum=0;i<this.length;sum+=this[i++]);
   return sum;
}

$script.ready(['jquery','raphael'], function() {
   $(document).ready(function() {
      Raphael.fn.pieChart = function (cx, cy, r, values, labels, stroke) {
          var paper = this,
              rad = Math.PI / 180,
              chart = this.set();
          function sector(cx, cy, r, startAngle, endAngle, params) {
              var x1 = cx + r * Math.cos(-startAngle * rad),
                  x2 = cx + r * Math.cos(-endAngle * rad),
                  y1 = cy + r * Math.sin(-startAngle * rad),
                  y2 = cy + r * Math.sin(-endAngle * rad);
              return paper.path(["M", cx, cy, "L", x1, y1, "A", r, r, 0, +(endAngle - startAngle > 180), 0, x2, y2, "z"]).attr(params);
          }
          var angle = 0,
              total = 0,
              start = 0,
              process = function (j) {
                  var value = values[j],
                      angleplus = 360 * value / total,
                      popangle = angle + (angleplus / 2),
                      color = Raphael.hsb(start, .75, 1),
                      ms = 500,
                      delta = 5,
                      bcolor = Raphael.hsb(start, 1, 1),
                      p = sector(cx, cy, r, angle, angle + angleplus, {fill: "90-" + bcolor + "-" + color, stroke: stroke, "stroke-width": 3}),
                      txt = paper.text(cx + (r + delta) * Math.cos(-popangle * rad), cy + (r + delta) * Math.sin(-popangle * rad), labels[j]).attr({fill: '#000', stroke: "none", opacity: 0, "font-size": 13});
                  p.mouseover(function () {
                      p.stop().animate({transform: "s1.1 1.1 " + cx + " " + cy}, ms, "elastic");
                      txt.stop().animate({opacity: 1}, ms, "elastic");
                  }).mouseout(function () {
                      p.stop().animate({transform: ""}, ms, "elastic");
                      txt.stop().animate({opacity: 0}, ms);
                  });
                  angle += angleplus;
                  chart.push(p);
                  chart.push(txt);
                  start += .1;
              };
          for (var i = 0, ii = values.length; i < ii; i++) {
              total += values[i];
          }
          for (i = 0; i < ii; i++) {
              process(i);
          }
          return chart;
      };

      $(".quotes").each(function () {
         var values = [],
             labels = [],
             maxs=[];
         $(this).find(".quote").each(function () {
            var tmp=parseInt($(this).find('.score').text());
            var label=$(this).find('.rating-label').text();
            if(isNaN(tmp) || label=='Total') return;
            values.push(tmp);
            labels.push(label+': '+tmp);
            maxs.push(parseInt($(this).find('.maxscore').text()));
            //$(this).hide();
         });
         if(values.length==0) return;
         values.push(maxs.sum() - values.sum());
         labels.push('');
         Raphael($(this).prev('.bargraph')[0], 200, 200).pieChart(100, 100, 33, values, labels, "#fff");
      });
   });
});
