$(document).ready(function() {
    $("#add_subject_type").accordion({collapsible: true,autoHeight:false, active:2});


    $("#add_type").live("click", function(){

         var new_type = $("#id_entity_type_text").val().toLowerCase();
        $.post("/entity/type/create/", { entity_type_regex: new_type},
                function(response) {
                    var data=JSON.parse(response)
                    if(data.success==true){
                        var options = $("#id_entity_type").attr('options');
                        if(should_append(options, new_type)){
                            $("#id_entity_type").prepend("<option value=" + new_type+ ">" +new_type + "</option>");
                        }
                        $('#id_entity_type').val(new_type);
                        $('#id_entity_type').trigger('change');
                        $("#add_subject_type").accordion({collapsible: true,autoHeight:false, active:2});
                        $("#type_message").html('');
                    }
                    else{
                        $('#id_entity_type').val(new_type.toLowerCase());
                        $("#add_subject_type").accordion({collapsible: false,autoHeight:false, active:2});
                        $("#type_message").html(data.message);
                    }
                });
    });

    should_append = function(options, new_type){
        for(i=0; i< options.length; i++){
            if(new_type == options[i].value)
                return false;
        }
        return true;
    };

});
