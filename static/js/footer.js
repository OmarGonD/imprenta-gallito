$(document).ready(function() {

    var docHeight = $(window).height();
    var footerHeight = $('#footer-navbar').height();
    var footerTop = $('#footer-navbar').position().top + footerHeight;

    if (footerTop < docHeight)
        $('#footer-navbar').css('margin-top', 10+ (docHeight - footerTop) + 'px');
});
