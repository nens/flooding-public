#alphabetical order
from flooding_lib.tools.importtool.models import ImportScenario
from flooding_lib.tools.importtool.models import ImportScenarioInputField
from flooding_lib.tools.importtool.models import InputField
from flooding_lib.tools.importtool.models import RORKering


from django.contrib import admin

'''
class PresentationLayerInline(admin.TabularInline):
    model = Scenario_PresentationLayer
    extra = 2

class PresentationTypeInline(admin.TabularInline):
    model = ResultType_PresentationType
    extra = 2
'''


class ImportScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'owner', 'validation_remarks']
    list_filter = ('state', 'owner')
    search_fields = ['name', ]


class InputFieldAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'header', 'position', 'type',
        'visibility_dependency_field', 'visibility_dependency_value',
        'required']
    list_filter = ('header', 'type', 'required')
    search_fields = ['name']


class RORKeringAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at', 'owner', 'file_name', 'status', 'type_kering']
    list_filter = ['status', 'type_kering', 'owner']
    search_fields = ['title']


#alphabetical order
admin.site.register(ImportScenario, ImportScenarioAdmin)
admin.site.register(ImportScenarioInputField)
admin.site.register(InputField, InputFieldAdmin)
admin.site.register(RORKering, RORKeringAdmin)
