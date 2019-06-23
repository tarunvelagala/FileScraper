$(document).ready(function () {
    $('#urls_link').click(function () {
        $('#urls_div').css('display', 'block');
        $('#pdfs_div').css('display', 'none');
    });
    $('#pdfs_link').click(function () {
        $('#pdfs_div').css('display', 'block');
        $('#urls_div').css('display', 'none');
    });
});
