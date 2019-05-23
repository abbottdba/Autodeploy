/**
 * Created by aaron on 2017/9/11.
 */

var OrderTableInit = function () {
    var oTableInit = new Object();
    //初始化Table
    oTableInit.Init = function (order_id) {
        $('#order_table').bootstrapTable({
            url: '/cmdb/apply/list/' + order_id + '-json.html',         //请求后台的URL（*）
            method: 'get',                      //请求方式（*）
            toolbar: '#order_toolbar',                //工具按钮用哪个容器
            striped: true,                      //是否显示行间隔色
            cache: false,                       //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
            pagination: true,                   //是否显示分页（*）
            sortable: false,                     //是否启用排序
            sortOrder: "asc",                   //排序方式
            queryParams: oTableInit.queryParams,//传递参数（*）
            sidePagination: "client",           //分页方式：client客户端分页，server服务端分页（*）
            pageNumber:1,                       //初始化加载第一页，默认第一页
            pageSize: 10,                       //每页的记录行数（*）
            pageList: [10, 25, 50, 100],        //可供选择的每页的行数（*）
            search: true,                       //是否显示表格搜索，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
            strictSearch: true,
            showColumns: true,                  //是否显示所有的列
            showRefresh: true,                  //是否显示刷新按钮
            minimumCountColumns: 2,             //最少允许的列数
            clickToSelect: true,                //是否启用点击选中行
            //height: 300,                        //行高，如果没有设置height属性，表格自动根据记录条数觉得表格高度
            uniqueId: "ID",                     //每一行的唯一标识，一般为主键列
            showToggle:true,                    //是否显示详细视图和列表视图的切换按钮
            cardView: false,                    //是否显示详细视图
            detailView: false,                   //是否显示父子表
            columns: [
                {
                    field: 'id',
                    title: 'ID'
                },
                {
                    field: 'ipaddress',
                    title: 'IP Addr'
                },
                {
                    field: 'idc',
                    title: 'IDC'
                },
                {
                    field: 'sys_type',
                    title: 'OS Type'
                },
                {
                    field: 'cpu',
                    title: 'CPU',
                    formatter: get_Core_format_unit
                },
                {
                    field: 'mem',
                    title: 'Mem',
                    formatter: get_GB_format_unit
                },
                {
                    field: 'disk',
                    title: 'Disk',
                    formatter: get_GB_format_unit
                },
                {
                    field: 'business',
                    title: 'Business'
                },
                {
                    field: 'function',
                    title: 'Function'
                },
                {
                    field: 'memo',
                    title: 'Memo'
                },
                {
                    field: 'approved',
                    title: 'Status',
                    formatter: item_statusFormatter
                },
                {
                    field: 'name',
                    title: 'Options',
                    //width: 330,
                    align: 'center',
                    formatter: item_operateFormatter
                },
            ]
        });
    };

    //得到查询的参数
    oTableInit.queryParams = function (params) {
        var temp = {   //这里的键的名字和控制器的变量名必须一直，这边改动，控制器也需要改成一样的
            limit: params.limit,   //页面大小
            offset: params.offset,  //页码
            departmentname: $("#txt_search_departmentname").val(),
            statu: $("#txt_search_statu").val()
        };
        return temp;
    };
    return oTableInit;
};

function get_Core_format_unit(value, row, index) {
    return value + 'C'
}

function get_GB_format_unit(value, row, index) {
    return value + 'G'
}

function item_statusFormatter(value, row, index) {
    if (value == 1) {
        return '<a type="button" class="btn btn-danger btn-xs">Pending</a>'
    } else if (value == 2) {
        return '<a type="button" class="btn btn-warning btn-xs">Standby</a>'
    } else if (value == 3) {
        return '<a type="button" class="btn btn-success btn-xs">Created</a>'
    } else {
        return '<a type="button" class="btn btn-danger btn-xs">False</a>'
    }
}

function item_operateFormatter(value, row, index) {
    if ( $("input[name='order_approval_status']").val() == 'False' ) {
        return [
            '<div class="btn-group">',
            '<a type="button" class="btn btn-default btn-xs" onclick="edit_item_fn(' + row.id + ')"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span> Edit</a>',
            '</div>'
        ].join('');
    } else {
        return [
            '<div class="btn-group">',
            '<a type="button" class="btn btn-default btn-xs" disabled><span class="glyphicon glyphicon-edit" aria-hidden="true"></span> Edit</a>',
            '</div>'
        ].join('');
    }
}

function edit_item_fn(obj_id) {
    $("#edit_item_modal").modal('show');
    $("input[name='edit_item_id']").val(obj_id);
}

function checkIP(value) {
    var exp=/^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;
    var reg = value.match(exp);
    if(reg) {
        return true;
    }
}

function update_item_fn(order_id) {

    var ipaddress = $('input[name="ipaddress"]').val()
    var obj_id = $('input[name="edit_item_id"]').val()

    if (! checkIP(ipaddress) || ipaddress.match(/^[ ]*$/)) {
        alert('Please check your IP format.');
        return false;
    }

    // 检查ip是否在当前列表存在
    var table_data = $('#order_table').bootstrapTable('getData');

    var ip_exist_tag = false;

    $(table_data).each(function () {
        if ($(this)[0].ipaddress == ipaddress) {
            ip_exist_tag = true;
        }
    });

    if (ip_exist_tag) {
        alert('This ip has already exist in the current list, please check again.');
        return false;
    } else {
        $.ajax({
            url: '/cmdb/apply/list/' + order_id + '-json.html',
            type: 'put',
            dataType: 'json',
            traditional:true,
            data: {
                'obj_id': obj_id,
                'ipaddress': ipaddress,
            },
            success: function (data, response, status) {
                if (data.status) {
                    $('#order_table').bootstrapTable('refresh');
                    $("#edit_item_modal").modal('hide');
                    $("#edit_item_form").trigger("reset");
                } else {
                    alert(data.message);
                    return false;
                }
            }
        });
    }
}

function order_approve_fn() {
    $("#order_update_confirm_modal").modal('show');
}

function do_order_approve_fn(order_id) {

    var table_data = $('#order_table').bootstrapTable('getData');

    var ip_exist_tag = true;

    $(table_data).each(function () {
        if (! $(this)[0].ipaddress) {
            ip_exist_tag = false;
        };
    });

    if (! ip_exist_tag) {
        alert('Please Confirm all server has already created.');
    } else {
        // 提交任务数据
        $.ajax({
            url: '/cmdb/apply/list/' + order_id + '.html',
            type: 'put',
            dataType: 'json',
            traditional:true,
            data: {
                'order_id': order_id,
            },
            success: function (data, response, status) {
                if (data.status) {
                   window.location.reload();
                } else {
                    alert(data.message);
                    return false;
                }
            }
        });
    }
}