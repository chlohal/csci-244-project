from uuid import UUID
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from src.client_flows.attendance import record_attendance
from src.client_flows.clark_sso import clark_sso_process
from src.client_flows.forms import form_process
from src.models import FlowInstanceState, QrCodeId


def user_flow_view(request, context, path_remaining):
    state = None
    # These context types mean that we're creating a new flow instance
    if context in ("qr", ):
        state = make_new_flow_instance(request, context, path_remaining)
    else:
        state = get_existing_state_instance(request, context, path_remaining)
    
    return process_next_step(request, context, path_remaining, state)

def get_existing_state_instance(request, context, path_remaining):
    return get_object_or_404(FlowInstanceState, uuid=UUID(hex=context))

def make_new_flow_instance(request, context, path_remaining):
    match context:
        case "qr":
            code_id = QrCodeId.objects.get(uuid=path_remaining)
            flowchart_contents = code_id.flowchart.contents
            steps = build_next_steps_for_user(flowchart_contents['blocks'], code_id.block_in_flowchart_id, 'user.qrcode_scan.scan')
            
            new_state = FlowInstanceState.objects.create(
                flowchart=code_id.flowchart,
                state={ "done_step_count": 0, "steps": steps, "accumulated_user_information": dict() }
            )
            return new_state
        case _:
            return HttpResponse(status=404, content="404 Not Found")

def process_next_step(request, context, path_remaining, state):
    if state.state['done_step_count'] >= len(state.state['steps']):
        return user_done_page(request)
    
    next_step_def = process_next_step_int(request, context, path_remaining, state)
    while next_step_def is True:
        state.state['done_step_count'] += 1
        if state.state['done_step_count'] >= len(state.state['steps']):
            state.save()
            return user_done_page(request)
        
        next_step_def = process_next_step_int(request, context, path_remaining, state)
    
    state.save()
    return next_step_def


def user_done_page(request):
    return render(request, "client-flow-complete.html")
    

def process_next_step_int(request, context, path_remaining, state):
    step_index = state.state['done_step_count']
    next_step = state.state['steps'][step_index]

    block_type, block_specific_id = next_step

    match block_type:
        case 'integrate.login.sso.clark':
            return clark_sso_process(request, context, path_remaining, state)
        case 'user.form_question':
            return form_process(request, context, path_remaining, state, block_specific_id)
        case 'canvas.attendance':
            return record_attendance(request, context, path_remaining, state, block_specific_id)

def build_next_steps_for_user(flowchart_blocks, start_block_id, start_flow_id):
    block_queue = [
        x['block'] for x in flowchart_blocks[start_block_id]['flows'][start_flow_id]
    ]
    visited = set()

    todo = []

    while len(block_queue):
        next_item = block_queue.pop(0)
        if next_item in visited:
            continue
        else:
            visited.add(next_item)
        
        block = flowchart_blocks[next_item]
        allflows = block['flows']
        for value in allflows.values():
            for flow_destination in value:
                if flow_destination['direction'] == "out":
                    block_queue.append(flow_destination['block'])
        todo.append((block['type'], block['id']))
    
    return todo
    