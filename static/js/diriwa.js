

$(function() {
	// $(".lexp").delay(1500).animate({width:43}, 1500);
});


function biglist_filter(element) {
    searchstring = $(element).val();
    $(element).parent().find("ul").find("li").each(function(index, item) { 
	it = $(item);
	if (it.text().match(searchstring) == null) { 
	    it.hide(); 
	} else {
	    it.show();
	} 
    })
}

$(document).ready(function() {
  $('.more-button').click(function() {
   $(this).next().toggleClass('hidden');
  });
  $('.more-button').next().addClass('hidden');
});
