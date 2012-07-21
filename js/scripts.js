
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

function openOverlay(image_path) {
    console.debug(image_path);
    
    $("#overlay").show();
    $("#img_preview").show();
    
    var preview_width = 360;
    var preview_height = 540;
    
    var center_x= window.innerWidth / 2 - preview_width/2 ;
    var center_y = window.innerHeight / 2 - preview_height/2 ;
    
    
    $('#img_preview').css({ 'width' : preview_width, 'height' : preview_height });
    $('#img_preview').css({ 'top' : center_y, 'left' : center_x });
    $('#img_preview').append("<img class='preview' src=" + image_path + ">");

}

function closeOverlay() {
    $("#overlay").hide();
    $("#img_preview").hide();
    $("#img_preview").children("img").remove();
}