
$(document).ready(function() {
	$(".number_link_disable").click(function(){
		$(this).removeClass("number_link_disable").addClass("number_link_enable");
		$(this).children().removeClass("enabled").addClass("disabled");
		$(this).parent().siblings().removeClass("img_enabled").addClass("img_disabled");
 		$.get('disable/'+this.id);
	});

	$(".number_link_enable").click(function(){
		$(this).removeClass("number_link_enable").addClass("number_link_disable");
		$(this).children().removeClass("disabled").addClass("enabled");
		$(this).parent().siblings().removeClass("img_disabled").addClass("img_enabled");
 		$.get('enable/'+this.id);
	});

});
