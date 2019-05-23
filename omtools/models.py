from django.db import models

from user_center import models as USER_MODELS
from repository import models as REPOSITORY_MODELS
from cmdb import models as CMDB_MODELS


class MongodbMission(models.Model):
    op_type_choices = (
        (1, 'find'),
        (2, 'delete'),
        (3, 'update'),
        (4, 'create'),
    )
    op_type = models.IntegerField(verbose_name=u'操作类型', choices=op_type_choices, default=1)
    title = models.CharField(verbose_name=u'任务标题', max_length=200)
    op_exec = models.CharField(verbose_name=u'执行语句', max_length=2000)
    database = models.CharField(verbose_name=u'执行数据库', max_length=100)
    document = models.CharField(verbose_name=u'执行表', max_length=100)
    find = models.CharField(verbose_name=u'find查询', max_length=2000)
    update = models.CharField(verbose_name=u'update更新', max_length=2000, null=True, blank=True)
    multi_tag = models.BooleanField(u'批量更新', default=False)
    req_user = models.ForeignKey(USER_MODELS.UserProfile, related_name='mongo_req_user', null=True, blank=True)
    op_user = models.ForeignKey(USER_MODELS.UserProfile, related_name='mongo_op_user', null=True, blank=True)
    approval_md5 = models.CharField(verbose_name=u'md5审核值', max_length=100)
    approved = models.BooleanField(u'批准执行', default=False)
    status_choices = (
        (1, 'Success'),
        (2, 'Pendding'),
        (3, 'Warning'),
    )
    status = models.IntegerField(verbose_name=u'任务状态', choices=status_choices, default=2)
    op_detail = models.CharField(verbose_name='执行详情', max_length=200, null=True, blank=True, default='等待执行')
    date = models.DateTimeField(auto_now_add=True)
    memo = models.CharField(verbose_name='备注', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Mongodb任务表"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return "{0},{1},{2}".format(self.op_type, self.title, self.status_choices)

    __str__ = __unicode__


class MongodbMissionTemplate(models.Model):
    op_type_choices = (
        (1, 'find'),
        (2, 'delete'),
        (3, 'update'),
        (4, 'create'),
    )
    op_type = models.IntegerField(verbose_name=u'操作类型', choices=op_type_choices, default=1)
    title = models.CharField(verbose_name=u'任务标题', max_length=200)
    database = models.CharField(verbose_name=u'执行数据库', max_length=100)
    document = models.CharField(verbose_name=u'执行表', max_length=100)
    find = models.CharField(verbose_name=u'find查询', max_length=100)
    update = models.CharField(verbose_name=u'update更新', max_length=100, null=True, blank=True)
    var_dict = models.CharField(verbose_name=u'变量字典', max_length=2000)
    op_exec = models.CharField(verbose_name=u'模板语句', max_length=2000)
    multi_tag = models.BooleanField(u'批量更新', default=False)
    approve_mail = models.CharField(u'审批人邮箱', max_length=100, null=True, blank=True)
    note = models.TextField(verbose_name=u'提示信息', null=True, blank=True)
    memo = models.CharField(verbose_name='备注', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Mongodb任务模板表"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return "{0},{1}".format(self.op_type, self.title)

    __str__ = __unicode__


class LogsControl(models.Model):
    project_id = models.ForeignKey(REPOSITORY_MODELS.ProjectInfo, related_name='logscontrol')
    # server_obj = models.ForeignKey(CMDB_MODELS.Asset, related_name='logsserver')
    server_ip = models.GenericIPAddressField(u'节点IP')
    server_node = models.CharField(u'节点名称', max_length=100)
    server_type_choices = (
        (0, '客服测试'),
        (1, '正式环境'),
        (2, '开发环境'),
    )
    server_type = models.SmallIntegerField(choices=server_type_choices, default=1)
    # logs_type_choices = (
    #     (0, '错误日志'),
    #     (1, '默认日志'),
    # )
    logs_type = models.CharField('日志类型', max_length=100)
    # url = models.URLField('日志地址', blank=True, null=True)
    url = models.CharField('日志地址', max_length=400, blank=True, null=True)
    logs_status_choices = (
        (0, '关闭'),
        (1, '正常'),
    )
    logs_status = models.SmallIntegerField('日志状态', choices=logs_status_choices, default=1)
    order_value = models.SmallIntegerField('排序值', default=1)
    memo = models.CharField('备注', max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "项目日志表"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return "{0}\t{1}".format(self.project_id.name, self.server_node, self.url)

    __str__ = __unicode__


class UrlMapsControl(models.Model):
    project_id = models.ForeignKey(REPOSITORY_MODELS.ProjectInfo, related_name='urlmapscontrol')
    url = models.CharField('URL地址', max_length=100)
    forward = models.TextField(u'云服务器IP组', blank=True, null=True)
    nginx = models.TextField(u'内部Nginx IP组', blank=True, null=True)
    ha = models.TextField(u'内部HA IP组', blank=True, null=True)
    backend = models.TextField(u'应用后端IP组', blank=True, null=True)
    order_value = models.SmallIntegerField('排序值', default=1)
    memo = models.CharField('备注', max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "URL地址映射"
        verbose_name_plural = verbose_name


class ProductDomains(models.Model):
    project_id = models.ForeignKey(REPOSITORY_MODELS.ProjectInfo, related_name='productdomains', blank=True, null=True, default=None)
    domain = models.CharField(u'域名地址', max_length=200, unique=True)
    ssl_tag = models.BooleanField(default=True)
    status = models.BooleanField(u'域名状态', default=True)
    memo = models.CharField(max_length=400, blank=True, null=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "产品域名管理"

    def __str__(self):
        return self.domain


class ProductDomainsIPaddr(models.Model):
    ip_addr = models.GenericIPAddressField(unique=True)
    domain = models.ManyToManyField(ProductDomains, related_name='productdomainsipaddr')

    class Meta:
        verbose_name_plural = "产品域名解析地址"

    def __str__(self):
        return self.ip_addr


class DnsMonitorControl(models.Model):
    project_id = models.ForeignKey(REPOSITORY_MODELS.ProjectInfo, related_name='dnsmonitorcontrol', blank=True,
                                   null=True)
    domain = models.CharField('URL地址', max_length=100)
    node1_status = models.BooleanField(u'监测节点1', default=False)
    date = models.DateTimeField(u'更新时间', auto_now=True)
    memo = models.CharField('备注', max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "DNS监测数据表"
        verbose_name_plural = verbose_name
