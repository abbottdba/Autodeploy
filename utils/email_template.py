def asset_apply_create(**kwargs):
    template_var = kwargs
    title = 'CMDB云主机任务申请 - {title}'.format(**template_var)
    content = '<b>Hi {creator}:</b> <br><br>CMDB系统中接收到一项您待处理的任务，请点击下面的连接进行操作，谢谢！' \
              '<br><br>The CMDB system receives a task that you need to handle, please click the link below to operate, thank you!' \
              '<br><br><a href="http://cmdb.omtools.me/cmdb/apply/list/{id}.html">http://cmdb.omtools.me/cmdb/apply/list/{id}.html</a>'.format(**template_var)

    return title, content


def asset_apply_create_inform_group(**kwargs):
    template_var = kwargs
    title = 'CMDB云主机任务创建完成 - %s' % template_var['title']
    asset_table_html = '<table border="1">' \
                       '<thead align="left">' \
                       '<tr>' \
                       '<th style="height:25px;">IP Addr</th>' \
                       '<th style="height:25px;">IDC</th>' \
                       '<th style="height:25px;">OS Type</th>' \
                       '<th style="height:25px;">CPU</th>' \
                       '<th style="height:25px;">Mem</th>' \
                       '<th style="height:25px;">Disk</th>' \
                       '<th style="height:25px;">Function</th>' \
                       '<th style="height:25px;">Memo</th>' \
                       '</tr>' \
                       '</thead>' \
                       '<tbody>%s</tbody></table>'
    asset_table_rows_html = ''
    for asset_obj in template_var['json_data']:
        asset_table_rows_html += '<tr> ' \
                               '<td style="height:25px; min-width:95px;">%s</td> ' \
                               '<td style="height:25px; min-width:95px;">%s</td> ' \
                               '<td style="height:25px; min-width:95px;">%s</td> ' \
                               '<td style="height:25px; min-width:95px;">%sC</td> ' \
                               '<td style="height:25px; min-width:95px;">%sG</td> ' \
                               '<td style="height:25px; min-width:95px;">%sG</td> ' \
                               '<td style="height:25px; min-width:95px;">%s</td> ' \
                               '<td style="height:25px; min-width:95px;">%s</td> ' \
                               '</tr>' % (asset_obj['ipaddress'], asset_obj['idc'], asset_obj['sys_type'], asset_obj['cpu'], asset_obj['mem'], asset_obj['disk'], asset_obj['function'], asset_obj['memo'])

    detail_table_html = asset_table_html % asset_table_rows_html

    basic_info = '业务线归属 / Business Unit: {business_unit}' \
                 '<br>申请用户 / User Apply: {user_apply}' \
                 '<br>审批用户 / User Approve: {user_approve}'\
                 '<br>主机数量 / Number of Servers: {server_count}'.format(**template_var)

    content = '<b>Hi All:</b> <br><br>CMDB系统接收到您所在分组云主机申请，创建信息如下：' \
              '<br><br>The CMDB system receives your group application for cloud server, the creation information is as follows:' \
              '<br><br>%s' \
              '<br><br>%s' % (basic_info, detail_table_html)

    return title, content
