// Grab a querystring from a dropdown select, and redirect the URL
function dropdown_redirect(object){
    window.location = object.querystring+$(object.identifier).val();
}