

from django.shortcuts import render, redirect, HttpResponse
from .models import Patient, Message, AppointmentChangeRequest
from .utils import get_bot_response, summarize_conversation

def chat_view(request):
    patient = Patient.objects.first()
    if not patient:
        return HttpResponse("No patient data available.")

    if request.method == 'POST':
        user_input = request.POST.get('message')

        # Pass the request to the get_bot_response function
        bot_response = get_bot_response(request, user_input, patient)

        # Create message entries for patient and bot
        Message.objects.create(patient=patient, sender='patient', text=user_input)
        Message.objects.create(patient=patient, sender='bot', text=bot_response)
        
        return redirect('chat')

    # Retrieve conversation history
    messages = Message.objects.filter(patient=patient).order_by('timestamp')

    # Summarize the conversation if messages exist
    if messages.exists():
        conversation_summary = summarize_conversation(messages)
    else:
        conversation_summary = ""

    # Retrieve unreviewed appointment requests
    appointment_requests = AppointmentChangeRequest.objects.filter(patient=patient, reviewed=False)

    # Prepare context for the template
    context = {
        'patient': patient,
        'messages': messages,
        'appointment_requests': appointment_requests,
        'conversation_summary': conversation_summary,
    }
    return render(request, 'chat/chat.html', context)


