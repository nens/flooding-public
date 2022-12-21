# Create your views here.

import json
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.views.generic import View

from lizard_worker import executor
from lizard_worker import models as workermodels

from flooding_lib import models as libmodels


logger = logging.getLogger(__name__)


class ScenarioWorkflowView(View):
    """
    Scenario processing view:
    shows latest execution status, logging.
    Contains functionality to execute a Scenario
    """
    template = 'scenarios_processing.html'

    def get(self, request, step=1, amount_per_step=25):

        if request.user.is_superuser is False:
            return render(request, '403.html')

        all_scenarios = libmodels.Scenario.objects.all().order_by("-id")
        step = int(step)
        sl = slice((step - 1) * amount_per_step, step * amount_per_step)
        scenarios = all_scenarios[sl]

        from_indexes = range(0, all_scenarios.count(), amount_per_step)

        processing = []

        for scenario in scenarios:
            workflows = workermodels.Workflow.objects.filter(
                scenario=scenario.id)

            workflow_template_code = ""
            workflow_template_id = ""
            if scenario.workflow_template is not None:
                workflow_template_code = scenario.workflow_template.code
                workflow_template_id = scenario.workflow_template.id

            scenario_workflow = {
                'scenario_id': scenario.id,
                'scenario_name': scenario.name,
                'template_id': workflow_template_id,
                'template_code': workflow_template_code}

            if workflows.exists():
                workflow = workflows.latest('tcreated')
                scenario_workflow.update({'workflows_count': workflows.count(),
                                          'workflow': workflow})
            processing.append(scenario_workflow)

        context = {'processing': processing,
                   'step': step,
                   'steps': range(1, len(from_indexes) + 1),
                   'amount_per_stap': amount_per_step}

        return render(request, self.template, context, request)

    def post(self, request):
        if request.user.is_superuser is False:
            return render(request, '403.html')
        scenario_id = request.POST.get('scenario_id')
        template_id = request.POST.get('template_id', u'')
        success = False
        if template_id != u'':
            success = executor.start_workflow(scenario_id, template_id)
        message = "Scenario {0} is {1} in de wachtrij geplaatst."
        if success is False:
            message = message.format(scenario_id, "NIET")
        else:
            message = message.format(scenario_id, "")
        context = {'success': success, 'message': message}
        return HttpResponse(content=json.dumps(context))
