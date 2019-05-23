function load_tree_data() {

    var setting = {
        data: {
            simpleData: {
                enable: true
            }
        }
    };

    $.ajax({
        url: '/cmdb/business-json.html?from=cmdb_asset_create',
        type: 'get',
        dataType: 'json',
        traditional:true,
        success: function (data, response, status) {
            if (data.status) {
                var zNodes = data.data
                business_nodes = zNodes
                $.fn.zTree.init($("#treeDemo"), setting, zNodes);
            }
        }
    });

}

function select_business_node(node_data, business_id) {
    if (business_id) {
        $('input[name="business_unit_id"]').val(business_id)
        close_business_tree()
        $("#business_select_text").html(node_data.title)
    }
}

$(".model-group-list").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
});

function close_business_tree() {
    $("#business_tree_btn").removeClass("open");
}

function checkIP(value) {
    var exp=/^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
    var reg = value.match(exp);
    if(reg) {
        return true;
    }
}

function isInteger(obj) {
 return obj%1 === 0
}

function get_server_config() {
        var ret = [];
        var memo_tag = false;
        $("#config_conditions").children().each(function () {
            var $cpu = $(this).find("select[name='cpu']");
            var $mem = $(this).find("select[name='mem']");
            var $disk = $(this).find("select[name='disk']");
            var $function = $(this).find("select[name='function']");
            var $memo = $(this).find("input[name='memo']");

            if ( $memo.val().match(/^[ ]*$/) ) {
                memo_tag = true;
                return false;
            }

            ret.push({'cpu': $cpu.val(), 'mem': $mem.val(), 'disk': $disk.val(), 'function': $function.val(), 'memo': $memo.val()});
        });

        if (memo_tag) {
            alert('Server memo is very important! Please put some words to discribe server.');
            return false;
        } else {
            return ret;
        }
    }

function cmdb_asset_apply_fn() {
    var title = $('input[name="title"]').val()
    var business_unit_id = $('input[name="business_unit_id"]').val()
    var idc = $('select[name="idc"]').val()
    var os_type = $('select[name="os_type"]').val()
    var creator = $('select[name="creator"]').val()

    // Title 验证
    if ( title.match(/^[ ]*$/) ) {
        alert("Please enter Title.")
        return false;
    }

    // Business 验证
    if (! business_unit_id) {
        alert("Please select Business Unit.")
        return false
    }

    if (business_nodes) {
        var business_level_check = false;
        $.each(business_nodes, function (index, value) {
            if (business_unit_id == value.pId) {
                business_level_check = true;
            }
        });
        if (business_level_check) {
            alert("The middle business node cannot be selected, Please select the lowest level node.");
            return false;
        }
    }

    var get_all_config = get_server_config();

    if (get_all_config) {
        console.log(get_all_config)
        var config_json_data = JSON.stringify(get_all_config);
        $.ajax({
            url: '/cmdb/apply.html',
            type: 'post',
            dataType: 'json',
            traditional:true,
            data : {
                "title": title,
                "business_unit_id": business_unit_id,
                "idc": idc,
                "os_type": os_type,
                "creator": creator,
                "apply_list": config_json_data,
            },
            success: function (data, response, status) {
                if (data.status) {
                    window.location.href='/cmdb/apply/list.html'
                } else {
                    alert(data.message)
                }
            }
        });
    }

}