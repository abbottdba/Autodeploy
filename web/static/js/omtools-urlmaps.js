/**
 * Created by aaron on 2017/9/11.
 */

var OmToolsUrlmapsInit = function () {
    var oTableInit = new Object();
    // 初始化Table
    oTableInit.Init = function (project_id) {
        $('#omtools_urlmaps_table').bootstrapTable({
            url: '/omtools/urlmaps-' + project_id + '.html',         //请求后台的URL（*）
            method: 'get',                      //请求方式（*）
            toolbar: '#omtools_urlmaps_toolbar',                //工具按钮用哪个容器
            striped: true,                      //是否显示行间隔色
            cache: false,                       //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
            pagination: true,                   //是否显示分页（*）
            sortable: false,                     //是否启用排序
            sortOrder: "asc",                   //排序方式
            queryParams: oTableInit.queryParams,//传递参数（*）
            sidePagination: "client",           //分页方式：client客户端分页，server服务端分页（*）
            pageNumber:1,                       //初始化加载第一页，默认第一页
            pageSize: 40,                       //每页的记录行数（*）
            pageList: [10, 25, 50, 100],        //可供选择的每页的行数（*）
            search: true,                       //是否显示表格搜索，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
            strictSearch: false,
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
                    title: 'ID',
                    valign: 'middle'
                },
                {
                    field: 'project_id__name',
                    title: '项目名称',
                    valign: 'middle'
                },
                {
                    field: 'url',
                    title: 'URL地址',
                    valign: 'middle',
                    formatter: url_formatter
                },
                {
                    field: 'forward',
                    title: '外部nginx',
                    formatter: forward_formatter
                },
                {
                    field: 'nginx',
                    title: '内部Nginx',
                    formatter: nginx_formatter
                },
                {
                    field: 'ha',
                    title: '内部HA服务器',
                    formatter: ha_formatter
                },
                {
                    field: 'backend',
                    title: '后端服务器',
                    formatter: backend_formatter
                },
                {
                    field: 'memo',
                    title: '备注信息'
                },
            ]
        });
    };

    //得到查询的参数
    oTableInit.queryParams = function (params) {
        var temp = {   // 这里的键的名字和控制器的变量名必须一直，这边改动，控制器也需要改成一样的
            limit: params.limit,   //页面大小
            offset: params.offset,  //页码
            departmentname: $("#txt_search_departmentname").val(),
            statu: $("#txt_search_statu").val()
        };
        return temp;
    };
    return oTableInit;
};

function ipaddress_format(ip_data) {
    var reg = new RegExp("\r\n","g")
    return ip_data.replace(reg, '<br>')
}

function forward_formatter(value, row, index) {
    return ipaddress_format(row.forward)
}

function nginx_formatter(value, row, index) {
    return ipaddress_format(row.nginx)
}

function ha_formatter(value, row, index) {
    return ipaddress_format(row.ha)
}

function backend_formatter(value, row, index) {
    return ipaddress_format(row.backend)
}

function url_formatter(value, row, index) {
    return '<a href="' + row.url + '" target="_blank">' + row.url + '</a>'
}

function server_type_formatter(value, row, index) {
    var type_map = {0: '客服测试', 1: '正式环境', 2: '开发环境'};
    return type_map[row.server_type];
}

function logs_status_formatter(value, row, index) {
    if (row.logs_status == 0) {
        return '<button type="button" class="btn btn-danger btn-xs"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span> 关闭</button>' ;
    } else if (row.logs_status == 1) {
        return '<button type="button" class="btn btn-success btn-xs"><span class="glyphicon glyphicon-ok" aria-hidden="true"></span> 正常</button>' ;
    }
}

function load_urlmapsviews_detail_fn(project_id) {
    // 激活头部菜单
    $(".urlmapsviews_nav_control").removeClass('active')
    $("#" + project_id).addClass('active')

    opt = {
        url: '/omtools/urlmaps-' + project_id + '.html'
    }

    $("#omtools_urlmaps_table").bootstrapTable('refresh', opt)
}

function default_urlmapsviews_detail_fn(project_id) {

    // 激活头部菜单
    $(".urlmapsviews_nav_control").removeClass('active')
    $("#" + project_id).addClass('active')

    var omtoolsUrlmaps = new OmToolsUrlmapsInit();
    omtoolsUrlmaps.Init(project_id);
}
