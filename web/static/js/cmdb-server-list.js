/**
 * Created by aaron on 2017/12/22.
 */

function load_business_tree_list() {

    var setting = {
        data: {
            simpleData: {
                enable: true
            }
        }
    };

    $.ajax({
        url: '/cmdb/business-json.html?from=cmdb_list',
        type: 'get',
        dataType: 'json',
        traditional:true,
        success: function (data, response, status) {
            if (data.status) {
                var zNodes = data.data
                $.fn.zTree.init($("#business_tree_list"), setting, zNodes);
            }
        }
    });

}

function do_search_by_business(obj, business_id) {
    $('input[name="default_business_unit"]').val(business_id);
    $('input[name="server__ipaddress"]').val('')  //点击业务线时，清空ip搜索条件
    $('#do_refresh').trigger("click");
}

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
                $.fn.zTree.init($("#treeDemo"), setting, zNodes);
            }
        }
    });

}

function business_update_fn(obj_id) {
    $("#business_update_modal").modal('show')
    load_tree_data()
    $('input[name="business_update_obj_id"]').val(obj_id)
}

function select_business_node(obj, business_id) {
    $('input[name="business_update_unit_id"]').val(business_id)
}

function update_business_unit_fn() {

    var nid = $('input[name="business_update_obj_id"]').val()
    var business_unit_id = $('input[name="business_update_unit_id"]').val()

    if (business_unit_id.length == 0) {
        alert('Please select business node!')
        return false
    }

    data_list = [{'nid': nid, 'business_unit_id': business_unit_id, 'num': 1}]

    $.ajax({
        url: '/cmdb/server-json.html',
        type: 'put',
        dataType: 'json',
        traditional:true,
        data : {'update_list': JSON.stringify(data_list)},
        success: function (data, response, status) {
            if (data.status) {
                $('#do_refresh').trigger("click");
                $("#business_update_modal").modal('hide')
                $('input[name="business_update_obj_id"]').attr("value","");
                $('input[name="business_update_unit_id"]').attr("value","");
                SuccessHandleStatus(data.message)
            } else {
                ErrorHandleStatus(data.message, data.error);
            }
        }
    });
}

function asset_eventlogs_fn(obj_id) {
    $("#asset_eventlogs_modal").modal('show')
    $.ajax({
        url: '/cmdb/logstimeline.html',
        type: 'get',
        traditional:true,
        data : {'asset_id': obj_id},
        success: function (data, response, status) {
            $('#asset_eventlogs_html_area').html(data)
        }
    });
}