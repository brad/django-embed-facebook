function sohail_expand_content(id) {
    document.getElementById(id).style.display = "inline";
    document.getElementById("sohailmorelink"+id).style.display = "none";
}
function showLocalDate(timestamp)
{
    var d = new Date(timestamp);
    document.write(d.toLocaleString());
}