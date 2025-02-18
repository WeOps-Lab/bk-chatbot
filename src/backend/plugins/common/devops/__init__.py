"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云PaaS平台社区版 (BlueKing PaaSCommunity Edition) available.
Copyright (C) 2017-2018 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from opsbot import on_command, CommandSession
from .api import DevOpsTask
from .settings import (
    DEVOPS_PROJECT_LIST_KEY, DEVOPS_PROJECT_LIST_ALIAS,
    DEVOPS_PROJECT_SELECT_KEY, DEVOPS_PIPELINE_SELECT_KEY,
    DEVOPS_PIPELINE_UPDATE_KEY, DEVOPS_PIPELINE_PARAM_PROMPT,
    DEVOPS_PIPELINE_FORMAT_PROMPT, DEVOPS_PIPELINE_EXECUTE_KEY,
    DEVOPS_PIPELINE_CANCEL_KEY, DEVOPS_PIPELINE_COMMON_PREFIX,
    DEVOPS_PIPELINE_CANCEL_TIP
)


@on_command(DEVOPS_PROJECT_LIST_KEY, aliases=DEVOPS_PROJECT_LIST_ALIAS)
async def _(session: CommandSession):
    bk_biz_id = session.bot.parse_action('parse_select', session.ctx)
    devops_task = DevOpsTask(session, bk_biz_id)
    msg_template = await devops_task.render_devops_project_list()
    if not msg_template:
        msg_template = devops_task.render_null_msg('CI')
    await session.send(**msg_template)


@on_command(DEVOPS_PROJECT_SELECT_KEY)
async def _(session: CommandSession):
    msg_template = await DevOpsTask(session).render_devops_pipeline_list()
    msg_template and await session.send(**msg_template)


@on_command(DEVOPS_PIPELINE_SELECT_KEY)
async def _(session: CommandSession):
    msg_template = await DevOpsTask(session).render_devops_pipeline_detail()
    msg_template and await session.send(**msg_template)


@on_command(DEVOPS_PIPELINE_UPDATE_KEY)
async def _(session: CommandSession):
    bk_devops_pipeline = session.bot.parse_action('parse_interaction', session.ctx)
    if not bk_devops_pipeline:
        session.state['bk_devops_pipeline'] = bk_devops_pipeline

    title = '<bold>CI TIP<bold>'
    content = f'{DEVOPS_PIPELINE_PARAM_PROMPT}，<bold>{DEVOPS_PIPELINE_FORMAT_PROMPT}<bold>'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    params, _ = session.get('params', prompt='...', **msg_template)
    params = params.split('\n')
    for i, item in enumerate(params):
        session.state['bk_devops_pipeline']['start_infos'][i]['value'] = item

    msg_template = await DevOpsTask(session).render_devops_pipeline_detail()
    msg_template and await session.send(**msg_template)


@on_command(DEVOPS_PIPELINE_EXECUTE_KEY)
async def _(session: CommandSession):
    bk_devops_pipeline = session.bot.parse_action('parse_interaction', session.ctx)
    flow = DevOpsTask(session)
    result = await flow.execute_task(bk_devops_pipeline)
    msg_template = flow.render_ci_execute_msg(result, bk_devops_pipeline)
    await session.send(**msg_template)


@on_command(DEVOPS_PIPELINE_CANCEL_KEY)
async def _(session: CommandSession):
    bk_devops_pipeline_name = session.bot.parse_action('parse_interaction', session.ctx)
    title = '<bold>CI TIP<bold>'
    content = f'<warning>{DEVOPS_PIPELINE_COMMON_PREFIX}「{bk_devops_pipeline_name}」' \
              f'{DEVOPS_PIPELINE_CANCEL_TIP}...<warning>'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    await session.send(**msg_template)
