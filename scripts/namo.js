function show_second_paddler(b) {
    if (b) {
        $("#ncc_second_firstname_tr").show();
        $("#ncc_second_lastname_tr").show();
        $("#ncc_second_age_tr").show();
        $("#ncc_second_gender_tr").show();
    }
    else  {
        $("#ncc_second_firstname_tr").hide();
        $("#ncc_second_lastname_tr").hide();
        $("#ncc_second_age_tr").hide();
        $("#ncc_second_gender_tr").hide();
    }
}

function change_boat_type() {
    b = ($("#ncc_boat_type_select").val() == "oc2");
    show_second_paddler(b);
}

function loadPage() {
    change_boat_type();
}
