/**
 * Created by aaron on 2017/9/11.
 */

var LogsTableInit = function () {
    var oTableInit = new Object();
    //初始化Table
    oTableInit.Init = function (app_id) {
        $('#domains_table').bootstrapTable({
            url: '/server/config/domains/json-' + app_id + '.html',         //请求后台的URL（*）
            method: 'get',                      //请求方式（*）
            toolbar: '#domains_toolbar',      //工具按钮用哪个容器
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
                    field: 'domain',
                    title: 'Domain'
                },
                {
                    field: 'ssl_tag',
                    title: 'SSL Tag',
                    formatter: sslFormatter
                },
                {
                    field: 'app_id__name',
                    title: 'Application',
                },
                {
                    field: 'app_id__project_id__name',
                    title: 'Project',
                },
                {
                    field: 'memo',
                    title: 'Memo'
                },
                {
                    field: 'name',
                    title: 'Options',
                    width: 280,
                    align: 'center',
                    formatter: button_operateFoarmatter
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


var ButtonInit = function () {
    var oInit = new Object();
    var postdata = {};

    oInit.Init = function () {
        //初始化页面上面的按钮事件
    };

    return oInit;
};

function sslFormatter(value, row, index) {
    var ssl_tag_html = ''
    if (row.ssl_tag) {
        ssl_tag_html = '<button type="button" class="btn btn-success btn-xs" ><span class="glyphicon glyphicon-ok" aria-hidden="true"></span> True</button>'
    } else {
        ssl_tag_html = '<button type="button" class="btn btn-danger btn-xs" ><span class="glyphicon glyphicon-remove" aria-hidden="true"></span> False</button>'
    }
    return [ssl_tag_html]
}

function button_operateFoarmatter(value, row, index) {
    return [
        '<div class="btn-group">',
        '<a type="button" class="btn btn-default btn-xs no-radius" onclick="edit_domain_data_fn(' + row.id + ')"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span> Edit</a>',
        '<a type="button" class="btn btn-default btn-xs no-radius" onclick="delete_domain_fn(' + row.id + ',' + '\'' + row.domain + '\')"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span> Delete</a>',
        '</div>'
    ].join('');
}

function create_domain_fn() {
    $("#update_domain_form").trigger("reset");
    $("#update_domain_fn").attr('onclick', 'update_domain_fn("post")')
}

function delete_domain_fn(domain_id, domain_url) {

    $("#delete_domain_html_area").html("Confirm remove domain " + domain_url + " ?")
    $("#delete_domain_fn").attr("onclick", "do_delete_domain_fn(" + domain_id + ")")
    $("#delete_domain_modal").modal('show')

}

function edit_domain_data_fn(domain_id) {
    $("#update_domain_fn").attr("onclick", "update_domain_fn('put', " + domain_id + ")")

    $.ajax({
        url: '/server/config/domains/update-server-domains.html',
        type: 'get',
        dataType: 'json',
        traditional:true,
        data: {'domain_id': domain_id},
        success: function (data, response, status) {

            $('input[name="domain_url"]').val(data[0].domain);
            $('textarea[name="domain_memo"]').val(data[0].memo);
            $("#create_domain_modal").modal('show')

        }
    });
}

function checkUrl(urlString){
    // if(urlString!=""){
    //     var reg=/(http|ftp|https|ws):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?/;
    //     if(!reg.cstest(urlString)){
    //         alert("Error Http Url...");
    //         return false;
    //     } else {
    //         return true;
    //     }
    // } else {
    //     alert('Please enter url address...');
    //     return false;
    // }
    return true;
}

function update_domain_fn(update_type, domain_id) {

    var app_id = $('input[name="app_id"]').val();
    var domain_url = $('input[name="domain_url"]').val();
    var domain_memo = $('textarea[name="domain_memo"]').val();

    if (checkUrl(domain_url)) {
        $.ajax({
            url: '/server/config/domains/update-server-domains.html',
            type: update_type,
            dataType: 'json',
            traditional: true,
            data: {
                'domain_id': domain_id,
                'app_id': app_id,
                'domain_url': domain_url,
                'domain_memo': domain_memo
            },
            success: function (data, response, status) {
                $('#domains_table').bootstrapTable('refresh');
                $("#create_domain_modal").modal('hide');
                $("#update_domain_form").trigger("reset");
            }
        });
    }
}

function do_delete_domain_fn(domain_id) {
    $.ajax({
        url: '/server/config/domains/update-server-domains.html',
        type: 'delete',
        dataType: 'json',
        traditional:true,
        data: {'domain_id': domain_id},
        success: function (data, response, status) {
            $('#domains_table').bootstrapTable('refresh');
            $("#delete_domain_modal").modal('hide')
        }
    });
}
