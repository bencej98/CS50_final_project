/*
$('.navbar-nav .nav-link').click(function(){
    $('.navbar-nav .nav-link').removeClass('active');
    $(this).addClass('active');
})
*/


$(document).ready(function () {
    $('.navbar li a').click(function(e) {

        $('.navbar a.active').removeClass('active');

        var $parent = $(this).parent();
        $parent.addClass('active');
        //e.preventDefault();
    });
});



/*
$(".nav-item a").on("click", function() {
    $(".nav-item a").removeClass("active");
    $(this).addClass("active");
  });
*/