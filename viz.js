
regseasonData = {}
d3.json("datasets/with_cat_reg_season_advanced.json").then(function (data) {
  let svg = d3.select("#clusterContainer").append("svg");
  svg.attr("width", 900).attr("height", 600).attr("id", "clusterSvg");
  let width = svg.attr("width");
  let height = svg.attr("height");
  let plotlayer = svg.append("g");
  regseasonData = data
  let nameLst = []
  Object.keys(regseasonData).forEach(function (key){
    nameLst.push(key)
  });
  var player_coordinate_lst = {};
  nameLst.forEach( d => {
     x = d3.randomUniform(10,width-10)();
     y = d3.randomUniform(10,height-10)();
     coor_lst = [x,y]
     player_coordinate_lst[d] = coor_lst
   });

   Object.keys(player_coordinate_lst).forEach(function(key){
     curr_obj = player_coordinate_lst[key]
     plotlayer.append("circle").attr("r", 3)
     .attr("cx", curr_obj[0]).attr("cy", curr_obj[1])
     .attr("fill", "grey")
     .attr("opacity", .75)
     .attr("name", key)
     .on("mouseover", function(d, i){

       d3.select(this).attr("r", 6);
       plotlayer.append("text").attr("x",  d3.select(this).attr("cx") - 10)
       .attr("y", d3.select(this).attr("cy") - 10).attr('id',"hi")
       .attr('font-size', 10).text(key);
     })
     .on("mouseout", function(d, i){
       d3.select(this).attr("r", 3);
       d3.select("#hi").remove();
     })
   });



})
